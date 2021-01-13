import os
import colour	
from glob import glob
import re
from variables import *
from treeconstructor.helper import *

import logging
logger = logging.getLogger('stageGetInitialTreeNodeMap')
logger.setLevel(logging.DEBUG)


def getInitialTreeNodeMap(image, hsv_image):
    def getCurrentColorForMask(ind, image):
        """
        :param ind: the index of the seed color
        :return: avg color around the seed color
        """
        mid_color = image[ind[0], ind[1]]
        kernel_size = 5
        margin = int(kernel_size / 2)
        u_i, b_i = max(ind[0] - margin, 0), min(ind[0] + margin + 1, height)
        l_j, r_j = max(ind[1] - margin, 0), min(ind[1] + margin + 1, width)
        neighbours = image[u_i:b_i, l_j:r_j]
        B = getColoredTemplateForCompared(neighbours.shape[0], neighbours.shape[1], mid_color)
        dists = colour.delta_E(neighbours, B)
        colors = neighbours[dists < PERCEPTUAL_DIS_FOR_DISTINCT_BG]
        if len(colors) < int(kernel_size * kernel_size / 2):
            return False, []
        return True, np.average(colors, axis=0).astype('uint8')

    def getMaskOfAColor(median_color, image, visited_map):
        """
        :param median_color: lab color
        :return:
        A mask; 0 areas refer to areas not this color; 1 areas refer to areas with this color
        """

        compared_color_template = getColoredTemplateForCompared(height, width, median_color)
        distance = colour.delta_E(image, compared_color_template)

        mask = np.where(visited_map == 1, 0, np.where(distance < PERCEPTUAL_DIS_FOR_DISTINCT_BG, 1, 0))

        return mask

    # --- start ---
    node_ind = 0
    height, width = image.shape[:2]
    visited_map = np.zeros((height, width))
    tree_node_map = np.full((height, width), -1)

    h,s,v = cv2.split(hsv_image)
    ## white
    white_mask = np.logical_and(s <= WHITE_S_THREH, v >= WHITE_V_THREH)
    visited_map[white_mask] = 1
    white_mask = white_mask.astype(int)

    gray_mask = np.logical_and(s <= WHITE_S_THREH, np.logical_and(v > BLACK_V_THREH, v < WHITE_V_THREH))
    visited_map[gray_mask] = 1
    gray_mask = gray_mask.astype(int)

    black_mask = (v <= BLACK_V_THREH)
    visited_map[black_mask] = 1
    black_mask = black_mask.astype(int)

    white_mask, gray_mask = mergeWhiteGrayMaskIfNecessary(white_mask, gray_mask, 0.1 * height * width, 0.3 * height * width)


    while (visited_map == 0).any():
        # find cur_color directly by finding the first unvisited pixel
        flag = True
        cur_first_unvisited_index = np.argwhere(visited_map == 0)[0]
        cur_color = image[cur_first_unvisited_index[0], cur_first_unvisited_index[1]]

        ## find mask
        if flag:
            mask = getMaskOfAColor(cur_color, image, visited_map)
            visited_map[mask == 1] = 1
            tree_node_map[mask == 1] = node_ind  ## node_ind is one greater than node_ind_of_interest
            node_ind = node_ind + 1
        else:
            break

    return tree_node_map, [white_mask, gray_mask, black_mask]