import imutils

from shapedetector import ShapeDetector
from treeconstructor.helper import *
import time
IS_DEBUGGING = False
# IS_DEBUGGING = True

def getPossibleChildrenMap(node_ind_of_ROI):
    def isPointInArea(pt, area):
        """
        :param pt: (i,j) in array coordinate
        :param area: 0, 1 mask; 1 represents the area
        :return: points physically inside the roi; not sure whether the points are assigned to other nodes, or are noise.
        """
        i = pt[0]
        j = pt[1]
        thres = 1
        lines = np.array([area[:i, j], area[i:, j], area[i, :j], area[i, j:]])
        cnts = np.array([np.count_nonzero(line == 1) for line in lines])
        if (cnts < thres).any():
            return 0  # the point is not in the area
        else:
            return 1  # the point is in the area

    def isPossibleChildren(cell):
        i,j = cell[0], cell[1]
        if rect_of_roi[i][j] == 0:
            return 0
        elif roi[i][j] == 1:
            return 0
        else:
            return isPointInArea(cell, roi)

    def indices_array_generic(m, n):
        r0 = np.arange(m)
        r1 = np.arange(n)
        out = np.empty((m, n, 2), dtype=int)
        out[:, :, 0] = r0[:, None]
        out[:, :, 1] = r1
        return out

    roi_cells = np.argwhere(final_tree_node_map == node_ind_of_ROI)
    roi_j, roi_i, roi_w, roi_h = getBoundaryOfCells(roi_cells)
    rect_of_roi = np.zeros_like(final_tree_node_map)
    rect_of_roi[roi_i:roi_i + roi_h, roi_j : roi_j + roi_w] = 1

    roi = np.zeros_like(final_tree_node_map)
    roi[final_tree_node_map == node_ind_of_ROI] = 1

    coord = indices_array_generic(height, width)
    coord = np.reshape(coord, (-1, 2))

    possible_children_map = np.apply_along_axis(isPossibleChildren, 1, coord)
    possible_children_map = np.reshape(possible_children_map, (height, width))

    return possible_children_map

def preprocessPossibleChildrenMap(mask):
    """
    This is used for: 1) remove small noise (points, or discontinuous) from the children map
    2) merge the small parts like the unexpected black lines or areas to the children map.
    (Those areas may be classified as background, but they may be also close to one foreground color, so here we give then a second chance.)
    :param possible_children_map:
    :return:
    """
    # erosion for remove noise
    mask = mask.astype('uint8')
    kernel_1 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask = cv2.erode(mask, kernel_1, iterations=1)

    # dilation for merge areas
    kernel_2 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.dilate(mask, kernel_2, iterations=2)

    return mask

def getDisconnectComponents(mask, thres):
    def getComponentsOrders(labels):  ## based on left corner
        unique_labels = np.unique(labels)
        center = {}
        for lb in unique_labels:
            if lb == 0:
                continue
            cells = np.argwhere(labels == lb)
            roi_j, roi_i, roi_w, roi_h = getBoundaryOfCells(cells)
            center[lb] = [roi_i, roi_j]
        center = {k: v for k, v in sorted(center.items(), key=lambda item: (item[1][0], item[1][1]))}
        return center

    mask_cp = np.where(mask == 1, 255, 0)
    mask_cp = mask_cp.astype('uint8')
    retval, labels = cv2.connectedComponents(mask_cp,8)
    num = labels.max()
    for i in range(1, num + 1):
        pts = np.where(labels == i)
        if len(pts[0]) < thres:
            labels[pts] = 0

    order_with_centers = getComponentsOrders(labels)

    return labels, order_with_centers

def postprocessingColorMask(mask):
    mask_cp = copy.deepcopy(mask)
    mask_cp = mask_cp.astype('uint8')
    kernel_2 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask_cp = cv2.dilate(mask_cp, kernel_2, iterations=1)
    return mask_cp

def addANodeToTree(node_ind_of_ROI, father_node_ind):
    def getShapeType(mask):
        mask_cp = np.zeros([height, width], dtype=np.uint8)
        mask_cp[mask == 1] = 255
        contours = cv2.findContours(mask_cp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        if len(contours) >= 1:
            c = contours[0]
            sd = ShapeDetector()
            shape_type = sd.detect(c)
        else:
            shape_type = 7
        return shape_type


    # add text/icon/index (if any) as node as well; read the bounding boxes, once added, remove it from the available bbs.
    if node_ind_of_ROI == -1:
        return
    roi_cells = np.argwhere(final_tree_node_map == node_ind_of_ROI)
    roi_j, roi_i, roi_w, roi_h = getBoundaryOfCells(roi_cells)

    mask = np.where(final_tree_node_map == node_ind_of_ROI, 1, 0)
    pixel_array = np.argwhere(final_tree_node_map == node_ind_of_ROI)
    type = getShapeType(mask)
    relative_height, relative_width = roi_h / height, roi_w / width
    relative_pixel_area = np.count_nonzero(final_tree_node_map == node_ind_of_ROI) / (height * width)

    colors = [img[c[0]][c[1]] for c in roi_cells]
    color = np.average(colors, axis=0).astype('uint8')   # Lab now

    node = {
        "id": node_ind_of_ROI,
        "father_id":father_node_ind,
        "type": type,
        "relative_height":relative_height,
        "relative_width": relative_width,
        "relative_pixel_area": relative_pixel_area,
        "color":color,
        "pixel_array": pixel_array,
        "conner": [roi_i, roi_j, roi_i + roi_h, roi_j + roi_w]
    }

    assert not (str(node_ind_of_ROI) in constructed_tree.keys()), "node {} has already existed!".format(node_ind_of_ROI)
    constructed_tree[str(node_ind_of_ROI)] = node
    return

def removeNoiseAndConstructTreeDFS(node_ind_of_ROI, father_node_ind):
    possible_children = np.zeros_like(final_tree_node_map)  # 0: not child, 1: possible child
    if node_ind_of_ROI == -1:
        possible_children = np.ones_like(final_tree_node_map)
    elif node_ind_of_ROI == 0:
        possible_children[final_tree_node_map != 0] = 1
    else:
        possible_children = getPossibleChildrenMap(node_ind_of_ROI)

    possible_children = preprocessPossibleChildrenMap(possible_children)

    returned_possible_children = copy.deepcopy(possible_children)

    inner_noise = np.zeros(final_tree_node_map.shape)

    if IS_DEBUGGING:
        displayMask(possible_children, 1,
                "pc_in_DFS({},{})_before_any_operations_{}".format(node_ind_of_ROI, father_node_ind, time.time()))

    # check if the pc children have already became a node/nodes in tree
    children_and_tree_relationship = copy.deepcopy(final_tree_node_map)
    children_and_tree_relationship[possible_children == 0] = -1
    node_count_pair = np.array(np.unique(children_and_tree_relationship, return_counts=True)).T
    for pair in node_count_pair:
        if pair[0] == -1:
            continue
        elif pair[0] == node_ind_of_ROI:
            possible_children[final_tree_node_map == pair[0]] = 0
            continue
        elif str(pair[0]) in constructed_tree.keys():
            total_count_in_a_node = np.count_nonzero(final_tree_node_map == pair[0])
            if pair[1] > int(total_count_in_a_node / 2):  # change father
                constructed_tree[str(pair[0])]["father_id"] = node_ind_of_ROI
            possible_children[final_tree_node_map == pair[0]] = 0

    # leaf node
    if np.count_nonzero(possible_children == 1) < small_noise_threshold:
        inner_noise[possible_children == 1] = 1
        addANodeToTree(node_ind_of_ROI, father_node_ind)
        return returned_possible_children, inner_noise



    # inner node
    while (possible_children == 1).any():
        valid = False
        while not valid:
            if not (possible_children == 1).any():
                break
            else:
                cur_first_unvisited_index = np.argwhere((possible_children == 1) & (merged_tree_node_map != -1))
                if len(cur_first_unvisited_index) == 0:
                    break
                cur_first_unvisited_index = cur_first_unvisited_index[0]
                possible_children[cur_first_unvisited_index[0]][cur_first_unvisited_index[1]] = 0
                cur_mask_label = merged_tree_node_map[cur_first_unvisited_index[0]][cur_first_unvisited_index[1]]

                mask = np.where(possible_children == 0, 0,
                                np.where(merged_tree_node_map == cur_mask_label, 1, 0))
                if np.count_nonzero(mask == 1) < small_noise_threshold:
                    inner_noise[mask == 1] = 1
                    possible_children[mask == 1] = 0
                else:
                    labeled_components, order_with_centers = getDisconnectComponents(mask, small_noise_threshold)
                    if len(order_with_centers.keys()) == 0:
                        inner_noise[mask == 1] = 1
                        possible_children[mask == 1] = 0
                    else:
                        first_valid_children_component = list(order_with_centers.keys())[0]
                        mask[labeled_components == first_valid_children_component] = 1
                        mask[labeled_components != first_valid_children_component] = 0
                        mask = postprocessingColorMask(mask)
                        possible_children[mask == 1] = 0
                        valid = True

        global final_node_ind
        if valid:
            update_father_node = node_ind_of_ROI
            cur_ind = final_node_ind
            final_tree_node_map[mask == 1] = cur_ind  ## node_ind is one greater than node_ind_of_interest
            if IS_DEBUGGING:
                displayMask(mask, 1,
                            "tree_valid_area_{}_in_DFS({},{})_{}".format(cur_ind, node_ind_of_ROI, father_node_ind,
                                                                         time.time()))
            final_node_ind = final_node_ind + 1
            son_possible_children, son_inner_noise = removeNoiseAndConstructTreeDFS(cur_ind, update_father_node)
            ## for some noise inside a shape, assign the noise the color of the shape
            mask[son_inner_noise == 1] = 1
            final_tree_node_map[mask == 1] = cur_ind
            possible_children[son_possible_children == 1] = 0

            if IS_DEBUGGING:
                displayMask(possible_children, 1, "pc_in_DFS({},{})_after_DFS({},{})_{}".format(node_ind_of_ROI, father_node_ind, cur_ind, update_father_node, time.time()))
        else:  # possible_children may contain several parts, each part is smaller than threshold, thus cannot turn valid to true
            break

    addANodeToTree(node_ind_of_ROI, father_node_ind)
    return returned_possible_children, inner_noise


def getConstructedShapeTree(image, small_noise_threshold_p, merged_img_p, merged_tree_node_map_p, wgb_node_index_p):
    global img, height, width, small_noise_threshold, merged_img, merged_tree_node_map, wgb_node_index, final_tree_node_map, final_node_ind, constructed_tree
    img = image
    height, width = img.shape[:2]

    small_noise_threshold = small_noise_threshold_p

    merged_img = merged_img_p
    merged_tree_node_map = merged_tree_node_map_p
    wgb_node_index = wgb_node_index_p


    final_tree_node_map = np.full(img.shape[:2],-1)
    final_node_ind = 0
    constructed_tree = {}

    removeNoiseAndConstructTreeDFS(-1, -1)

    return constructed_tree, final_tree_node_map