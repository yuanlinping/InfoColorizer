import cv2
import os
import colour
from glob import glob
import re
from sklearn.neighbors.kde import KernelDensity
from scipy.signal import argrelextrema
import numpy as np

from treeconstructor.helper import *
from variables import *


import logging
logger = logging.getLogger('stageMergeSimilarColors')
logger.setLevel(logging.DEBUG)


# merge: combined colors with similar hues; combined all white/gray/black into one white/gray/black
# merged_tree_node_map: -1 indicates the pixels are not with seed colors or similar to any other areas; white/gray/black are annotated by wgb_node_index
# merged_img: white indicates merged_tree_node_map == -1

def mergeSimilarColors(tree_node_map, image, name, white_gray_black_masks):
    def getMergedAverageColor(label_range, node_in_this_cluster):
        labels = np.arange(0, label_range)
        label_of_roi = labels[node_in_this_cluster]
        color = np.average(image[np.isin(tree_node_map, label_of_roi)], axis=0)
        return color

    def runKDE(fit_arr, compared_arr, start_label_ind, output_label_arr, output_cluster_centers, type, bandwidth=3):
        """
        :param fit_arr: 1d array which kde is run on. Like the selected v arrays or h arrays
        :param compared_arr: orignal h or v array
        :param start_label_ind:
        :param output_label_arr:
        :param output_cluster_centers:
        :param bandwidth:
        :return:
        """
        kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth).fit(fit_arr.reshape(-1, 1))
        xgrid = np.linspace(fit_arr.min(), fit_arr.max())
        e = kde.score_samples(xgrid.reshape(-1, 1))
        mi, ma = argrelextrema(e, np.less)[0], argrelextrema(e, np.greater)[0]
        mi = xgrid[mi]

        inner_label_ind = start_label_ind

        if len(mi) != 0:
            for i, low in enumerate(mi):
                if i == 0:
                    if type == "v":
                        in_this_cluster = (s <= WHITE_S_THREH) & (compared_arr < low)
                    elif type == "h":
                        in_this_cluster = (output_label_arr == -1) & (compared_arr < low)
                else:
                    if type == "v":
                        in_this_cluster = (s <= WHITE_S_THREH) & (compared_arr < low) & (compared_arr >= mi[i - 1])
                    elif type == "h":
                        in_this_cluster = (output_label_arr == -1) & (compared_arr < low) & (compared_arr >= mi[i - 1])
                output_label_arr[in_this_cluster] = inner_label_ind
                color = getMergedAverageColor(len(colors), in_this_cluster)
                output_cluster_centers = np.append(output_cluster_centers, color)
                inner_label_ind = inner_label_ind + 1

            if type == "v":
                in_this_cluster = (s <= WHITE_S_THREH) & (compared_arr >= mi[-1])
            elif type == "h":
                in_this_cluster = (output_label_arr == -1) & (compared_arr >= mi[-1])

            output_label_arr[in_this_cluster] = inner_label_ind
            color = getMergedAverageColor(len(colors), in_this_cluster)
            output_cluster_centers = np.append(output_cluster_centers, color)

        else:
            in_this_cluster = output_label_arr == -1
            output_label_arr[in_this_cluster] = inner_label_ind
            color = getMergedAverageColor(len(colors), in_this_cluster)
            output_cluster_centers = np.append(output_cluster_centers, color)


        return inner_label_ind + 1, output_label_arr, output_cluster_centers

    def splitGrayAndWhite(start_label_ind, output_label_arr, output_cluster_centers):
        inner_label_ind = start_label_ind
        wg_arr = np.array([])
        inner_label_ind = inner_label_ind + 1
        # white
        in_this_cluster = (s <= WHITE_S_THREH) & (v >= WHITE_V_THREH)
        if np.count_nonzero(in_this_cluster.astype(int)) != 0:
            output_label_arr[in_this_cluster] = inner_label_ind
            color = getMergedAverageColor(len(colors), in_this_cluster)
            output_cluster_centers = np.append(output_cluster_centers, color)
            wg_arr = np.append(wg_arr, inner_label_ind)
            inner_label_ind = inner_label_ind + 1
        else:
            wg_arr = np.append(wg_arr, -2)

        # gray
        in_this_cluster = (s <= WHITE_S_THREH) & (v < WHITE_V_THREH)
        if np.count_nonzero(in_this_cluster.astype(int)) != 0:
            output_label_arr[in_this_cluster]= inner_label_ind
            color = getMergedAverageColor(len(colors), in_this_cluster)
            output_cluster_centers = np.append(output_cluster_centers, color)
            wg_arr = np.append(wg_arr, inner_label_ind)
        else:
            wg_arr = np.append(wg_arr, -2)

        return inner_label_ind, output_label_arr, output_cluster_centers, wg_arr


    colors = getAvgColorsBasedOnTreeNodeMap(tree_node_map, image)

    if (len(colors) >= 1):
        hsv_colors = cv2.cvtColor(cv2.cvtColor(np.reshape(colors.astype('uint8'), (1,-1,3)), cv2.COLOR_LAB2BGR), cv2.COLOR_BGR2HSV)
        hsv_colors = np.reshape(hsv_colors, (-1,3))
        h = hsv_colors[:,0]
        s = hsv_colors[:,1]
        v = hsv_colors[:,2]

        labels = np.full(h.shape, -1)
        label_ind = 0
        cluster_centers = np.array([])

        wgb_node_ind = np.array([])

        ## kde
        colorful_h = h[labels == -1]

        if(len(colorful_h) !=0):
            label_ind, labels, cluster_centers = runKDE(colorful_h, h, label_ind, labels, cluster_centers,"h", 3)

        merged_tree_map = labels[tree_node_map]
        merged_tree_map[tree_node_map == -1] = -1

        start_node = np.max(labels) + 1

    else:
        merged_tree_map = tree_node_map.copy()
        wgb_node_ind = np.array([])
        cluster_centers = np.array([])
        start_node = 0

    ## add white/gray/black
    for mm in white_gray_black_masks:
        if (mm == 1).any():
            wgb_node_ind = np.append(wgb_node_ind, start_node)
            color = getOneAvgColorForOneMask(mm, 1, image)
            merged_tree_map[mm == 1] = start_node
            cluster_centers = np.append(cluster_centers, color, axis=0)
            start_node = start_node + 1
        else:
            wgb_node_ind = np.append(wgb_node_ind, -2)

    print("node in merged tree map: {}".format(start_node))
    print("wgb node index")
    print(wgb_node_ind)

    cluster_centers = np.reshape(cluster_centers, (-1, 3))
    cluster_centers = np.append(cluster_centers, [[0, 128, 128]], axis=0)  # for those with tree_node_map == -1

    merged_image = cluster_centers[merged_tree_map]

    return merged_image, merged_tree_map, wgb_node_ind