import cv2
import numpy as np
import copy

def cvtBRG2LAB(arr, dim):
    """
    :param arr: [b,g,r]
    :param dim: 1D:  [b,g,r] 2D: [[b,g,r]] 3D:[[[b,g,r]]]
    :return:
    """
    if dim == "1D":
        arr = np.array(arr).reshape((1,1,3)).astype('uint8')
        arr = cv2.cvtColor(arr, cv2.COLOR_BGR2LAB).reshape(3,)
    elif dim == "2D":
        arr = np.array(arr).reshape((1, -1, 3)).astype('uint8')
        arr = cv2.cvtColor(arr, cv2.COLOR_BGR2LAB).reshape(-1,3)
    else:
        arr = cv2.cvtColor(arr, cv2.COLOR_BGR2LAB)
    return arr


def getStatistic(samples, feature):
    """
    :param samples: ELements with same types; like all body_text
    :param feature: x, y, w, h ...
    :return:
    """

    values = []
    for element in samples:
        values.append(element.location[feature])
    return {
        "max": np.amax(values),
        "avg": np.average(values),
        "min":np.amin(values),
        "std": np.std(values)
    }

def mergeWhiteGrayMaskIfNecessary(white_mask, gray_mask, low_thres, high_thres):
    margin_mask = np.zeros_like(white_mask)
    height, width = margin_mask.shape
    MARGIN = 2
    margin_mask[MARGIN,:] = 1
    margin_mask[:,MARGIN] = 1
    margin_mask[:, width - MARGIN] = 1
    margin_mask[height - MARGIN, :] = 1

    white_in_edge = np.logical_and(margin_mask == 1, white_mask == 1)
    gray_in_edge = np.logical_and(margin_mask == 1, gray_mask == 1)
    thre = 0.25 * width
    if (np.count_nonzero(white_in_edge) > thre and np.count_nonzero(gray_in_edge) > thre) \
        or (np.count_nonzero(white_mask) > high_thres and np.count_nonzero(gray_mask) < low_thres):
        white_mask[gray_mask == 1] = 1
        gray_mask[gray_mask == 1] = 0
    elif np.count_nonzero(white_mask) < low_thres and np.count_nonzero(gray_mask) > high_thres:
        gray_mask[white_mask == 1] = 1
        white_mask[white_mask == 1] = 0
    return white_mask.astype(int), gray_mask.astype(int)

# -----------------helper-------------------
def getOneAvgColorForOneMask(mask, key, image):
    """
    :param mask: segmented img
    :param key: label of roi
    :return: the avg color of this roi
    """
    label_colors = image[mask == key]
    if len(label_colors) == 0:
        color = None
    else:
        color = np.average(label_colors, axis=0)
    return color


def getAvgColorsBasedOnTreeNodeMap(masks, image):
    """
    :param masks: segmented img
    :return: the avg colors of all roi with label >= 0
    """
    max_label = np.max(masks)
    uni_labels = range(0, max_label + 1)
    colors = np.array([])
    for label in uni_labels:
        color = getOneAvgColorForOneMask(masks, label, image)
        if color is None:
            color = [255, 255, 255]
        colors = np.append(colors, color)
    return colors.reshape((-1, 3))

def getColoredTemplateForCompared(h, w, lab_color):
    L = np.full((h, w), lab_color[0])
    a = np.full((h, w), lab_color[1])
    b = np.full((h, w), lab_color[2])
    return cv2.merge([L, a, b])

def getBoundaryOfCells(pts):
    """
    :param pts: n * 2 numpy array; each 1 * 2 is a cell. (i,j) in array coordinate
    :return: x, y, w, h in img coordinate
    """
    [y_min, x_min] = np.min(pts, axis=0)
    [y_max, x_max] = np.max(pts, axis=0)
    return x_min, y_min, x_max - x_min, y_max - y_min

# -----------------show results to files-------------------
def displayComponents_2(masks, file_path, image, resized=False):
    """
    :param masks: segemented img; like tree_node_map in this code
    :param file_path: file name for saving pictures
    :param resized:
    :return:
    """
    colors = getAvgColorsBasedOnTreeNodeMap(masks, image).reshape(-1)
    colors = np.append(colors, [0, 128, 128])  # not recognized is black; for pixel with labels = -1
    colors = np.reshape(cv2.cvtColor(np.reshape(colors.astype('uint8'), (1, -1, 3)), cv2.COLOR_LAB2BGR), (-1,3))
    display = colors[masks]
    if resized:
        display = cv2.resize(display, (700,700))

    cv2.imwrite(file_path, np.hstack((display, cv2.cvtColor(image.astype('uint8'), cv2.COLOR_LAB2BGR))))

def displayComponents_3(masks, file_path, image, image_2, image_3, resized=False):
    """
    :param masks: segemented img; like tree_node_map in this code
    :param file_path: file name for saving pictures
    :param resized:
    :return:
    """
    colors = getAvgColorsBasedOnTreeNodeMap(masks, image).reshape(-1)
    colors = np.append(colors, [0, 128, 128])  # not recognized is black; for pixel with labels = -1
    colors = np.reshape(cv2.cvtColor(np.reshape(colors.astype('uint8'), (1, -1, 3)), cv2.COLOR_LAB2BGR), (-1,3))
    display = colors[masks]
    if resized:
        display = cv2.resize(display, (700,700))

    max_label = np.max(masks)
    random_colors = np.array([])
    for i in range(0, max_label + 1):
        color = np.random.randint(0, 255, (3)).tolist()
        random_colors = np.append(random_colors, color)
    random_colors = np.append(random_colors, [0,128,128])
    random_colors = np.reshape(cv2.cvtColor(np.reshape(random_colors.astype('uint8'), (1, -1, 3)), cv2.COLOR_LAB2BGR), (-1,3))
    random_display = random_colors[masks]

    cv2.imwrite(file_path, np.hstack((display, random_display, cv2.cvtColor(image.astype('uint8'), cv2.COLOR_LAB2BGR), cv2.cvtColor(image_2.astype('uint8'), cv2.COLOR_LAB2BGR), image_3)))

def displayMask(mask, key, name):
    """
    :param mask: segmented img
    :param key: label of roi
    :param name: file name for saving the picture
    :return: in the picture, the white part is roi
    """
    bw = copy.deepcopy(mask)
    bw[mask == key] = 255
    cv2.imwrite("masks/black_{}.png".format(name), bw)

def displayColorfulMask(mask, key, image, name):
    """
    :param mask: segmented img
    :param key: label of roi
    :param name: file name for saving the picture
    :return: in the picture, the colored part is roi
    """
    color = getOneAvgColorForOneMask(mask, key, image)
    color = np.reshape(cv2.cvtColor(np.reshape(color.astype('uint8'), (1, -1, 3)), cv2.COLOR_LAB2BGR), (-1))
    colored_mask = np.full(image.shape, 255)
    colored_mask[mask == key] = color
    cv2.imwrite("masks/colorful_{}.png".format(name), colored_mask)

