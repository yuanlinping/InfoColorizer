import os
import re
from glob import glob

from treeconstructor.helper import *
from variables import *

from treeconstructor.stageRemoveTextIconIndex import remove_text_icon_index_from_image
from treeconstructor.stageGetInitialTreeNodeMap import getInitialTreeNodeMap
from treeconstructor.stageMergeSimilarColors import mergeSimilarColors
from treeconstructor.stageGetConstructedShapeTree import getConstructedShapeTree

def featureExtractionPipeline(img_file_name, bb_file_name, mode, num_in_img):
    # ----stage 1-----
    img, infographics_data_components = remove_text_icon_index_from_image(img_file_name, bb_file_name, mode)

    # ----stage 1.5 some preprocessing-----
    img = cv2.resize(img, (300,300))
    height, width = img.shape[:2]
    small_noise_threshold = 0.001 * height * width


    ## img preprocessing
    img = cv2.medianBlur(img, 5)
    img = cv2.blur(img, (3, 3))

    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)


    # ----stage 2-----
    tree_node_map, wgb_masks = getInitialTreeNodeMap(img, hsv_img)

    # ----stage 3-----

    merged_img, merged_tree_node_map, wgb_node_index = mergeSimilarColors(tree_node_map, img, str(num_in_img), wgb_masks)   # -1 in tree_node_map still is -1 in merged_tree_node_map

    # ----stage 4-----
    constructed_tree, final_tree_node_map = getConstructedShapeTree(img, small_noise_threshold, merged_img, merged_tree_node_map, wgb_node_index)

    # ----print-------
    orignal_img = cv2.imread(img_file_name)
    orignal_img = cv2.resize(orignal_img,(300,300))
    displayComponents_3(final_tree_node_map, "./masks/{}.jpg".format(num_in_img), merged_img, img, orignal_img)

    return constructed_tree


if __name__ == "__main__":
    # mode = "4300_infographics"
    mode = "all_infographics"
    data_root = DATA_ROOT if mode == "4300_infographics" else DATA_ROOT_2

    if not os.path.exists("masks"):
        os.makedirs("masks")

    num_in_img = 644
    img_file_name = os.path.join(data_root, INFOGRAPHICS_FOLDER, "{}.jpg".format(num_in_img))
    bb_file_name = os.path.join(data_root, BOUNDING_BOX_FOLDER, "{}.txt".format(num_in_img))
    num_in_img = img_file_name.split("/")[-1].split(".")[0]
    featureExtractionPipeline(img_file_name, bb_file_name, mode, num_in_img)