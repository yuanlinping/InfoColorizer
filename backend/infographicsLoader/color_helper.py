import cv2
import numpy as np
from libs import dist_cie2000
from sklearn.cluster import DBSCAN, KMeans
from variables import *


def find_background_color(img):
    """
    :param img: in BGR
    :return:  in BGR
    white -> different white
    """
    MARGIN = 3
    height, width, channel = img.shape
    top = img[MARGIN,:,:]
    left = img[:,MARGIN,:]
    right = img[:, width - MARGIN, :]
    bottom = img[height - MARGIN, :, :]
    edge_colors = np.concatenate((top, left, right, bottom), axis=0)
    unique_colors, frequencies = np.unique(edge_colors, axis=0, return_counts=True)
    return unique_colors[np.argmax(frequencies)]

def kmeans_main_colors_in_bounding_boxes(img):
    """

    :param img: the output of cv2.imread(); see https://github.com/algolia/color-extractor
    :return: bgr color
    use lab + euclidean
    """
    bg_color = find_background_color(img)
    return {
        "bg_color": bg_color,
        "main_color": bg_color,
        "other_color": bg_color
    }


def kmeans_main_colors_in_whole_images(img):
    """
    :param img: the output of cv2.imread(); see https://github.com/algolia/color-extractor
    :return: bgr color; without background colors (the most one)
    use lab + euclidean
    """
    reshape_img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).reshape((-1,3))
    kmeans = KMeans(n_clusters=COLOR_CONSIDERED_NUM + 1, max_iter=100, tol = 1.0)
    kmeans.fit(reshape_img)
    square_dist_sum, labels, cluster_center = kmeans.inertia_, kmeans.labels_, kmeans.cluster_centers_

    cluster_center = cluster_center.astype('uint8')
    cluster_center = cv2.cvtColor(cluster_center.reshape(1,-1,3), cv2.COLOR_LAB2BGR).reshape(-1,3)

    unique_labels, frequencies = np.unique(labels, return_counts=True)
    unique_labels = [l for l,f in sorted(zip(unique_labels, frequencies), key=lambda x:x[1], reverse=True)]

    k_main_colors = np.array([[0,0,0]])
    for i in range(COLOR_CONSIDERED_NUM + 1):
        k_main_colors = np.append(k_main_colors, cluster_center[unique_labels[i]])

    k_main_colors = k_main_colors.reshape((-1,3))
    k_main_colors = np.delete(k_main_colors, 0, axis=0)
    k_main_colors = np.delete(k_main_colors, 0, axis=0) # delete background color
    return k_main_colors



def getColorsWithinSameTypeElements(samples, feature):
    """

    :param samples: ELements with same types; like all body_text
    :param feature: "bg_color", "main_color", "other_color"
    :return:
    """
    original_colors = np.array([[0,0,0]])
    for element in samples:
        original_colors = np.append(original_colors, element.colors[feature].reshape((1,3)), axis=0)
    original_colors =np.delete(original_colors, 0, axis=0)
    cluster = DBSCAN(eps=PERCEPTUAL_DIS_FOR_DISTINCT_THEME_COLORS, min_samples=1, metric=dist_cie2000).fit(original_colors)
    n_cluster = len(set(cluster.labels_)) - (1 if -1 in cluster.labels_ else 0)

    cluster_centers = np.array([[0,0,0]])
    for cl in range(n_cluster):
        indices = np.where(cluster.labels_ == cl)
        cluster_centers = np.append(cluster_centers, np.array([original_colors[indices].mean(axis = 0)]), axis=0)
    cluster_centers = np.delete(cluster_centers, 0, axis=0)
    return n_cluster, cluster_centers.astype('uint8')
