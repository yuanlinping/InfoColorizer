from infographicsLoader.infographicsLoader import *

import cv2
from glob import glob
import os
import numpy as np
import re
import shutil

import logging
logger = logging.getLogger('stageRemoveTextIconIndex')
logger.setLevel(logging.DEBUG)
logging.disable(logging.DEBUG)  # the flag
# if logger.isEnabledFor(logging.DEBUG):  # for block

inx = 0
def rm_text_icon_index_in_bb(img, datacomponent):
    tl_i, tl_j, br_i, br_j = datacomponent.conner["tl_i"], datacomponent.conner["tl_j"], datacomponent.conner["br_i"], datacomponent.conner["br_j"],
    bg_color = datacomponent.colors["bg_color"]
    bg_color = tuple([int(x) for x in bg_color])

    bb_content = img[tl_i:br_i, tl_j:br_j]

    # ----- remove text/icon/index ----- #
    gray = cv2.cvtColor(bb_content, cv2.COLOR_BGR2GRAY)

    gray_threshold = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]

    uni, fre = np.unique(gray_threshold, return_counts=1)
    uni = [u[0] for u in sorted(zip(uni,fre), key = lambda x:x[1])]
    if len(uni) > 1 and uni[0] < uni[1]:
        gray_threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    ## dilation
    dilate_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilate = cv2.dilate(gray_threshold, dilate_kernel, iterations=1)

    ## replace color

    bg_dilate = cv2.dilate(dilate, dilate_kernel, iterations=1)
    bg_dilate[dilate == 255] = 0 # outer dilation removing the small dilation
    near_bg_color = np.mean(bb_content[bg_dilate == 255], axis=0).astype('uint8')
    bb_content[dilate == 255] = near_bg_color

    ## smooth, making it more similar to near colors
    for i in range(10):
        bb_content = cv2.medianBlur(bb_content, 5)

    img[tl_i:br_i, tl_j:br_j] = bb_content

    if logger.isEnabledFor(logging.DEBUG):
        global inx
        cv2.imwrite("rm_tii_debug/{}.png".format(inx), np.vstack((gray, gray_threshold, dilate)))
        inx = inx + 1

    return img

# API
def remove_text_icon_index_from_image(img_file_name, bb_file_name, mode):
    img = cv2.imread(img_file_name)

    # try:
    if mode == "4300_infographics":
        infographics_data_components = constructDataComponents(img_file_name, bb_file_name)
    else:
        infographics_data_components = constructDataComponentsForTimelineFormat(img_file_name, bb_file_name)
    for key, values in infographics_data_components.items():
        if mode == "all_infographics":
            if key in ["event_mark", "annotation_mark", "main_body"]:
                continue
        for curDTComp in values:
            img = rm_text_icon_index_in_bb(img, curDTComp)

    return img, infographics_data_components


if __name__ == "__main__":
    # mode = "4300_infographics"
    mode = "all_infographics"
    data_root = DATA_ROOT if mode == "4300_infographics" else DATA_ROOT_2

    finish_removing_folder = os.path.join(data_root, REMOVED_TEXT_ICON_INDEX_FOLDER)

    if not os.path.exists(finish_removing_folder):
        os.makedirs(finish_removing_folder)

    info_files = sorted(glob(os.path.join(data_root, BOUNDING_BOX_FOLDER, "*.txt")))
    for img_file_name in info_files:
        file_sequence_order = re.findall(r'\d+', img_file_name.split('/')[-1])[0]
        file_sequence_order = str(file_sequence_order)
        img_file_name = os.path.join(data_root, INFOGRAPHICS_FOLDER, file_sequence_order+".jpg")
        bb_file_name = os.path.join(data_root, BOUNDING_BOX_FOLDER, file_sequence_order+".txt")

        if os.path.exists(os.path.join(finish_removing_folder, file_sequence_order + ".jpg")):
            logger.debug("skip " + file_sequence_order)
            continue

        try:
            img,_ = remove_text_icon_index_from_image(img_file_name, bb_file_name, mode)
            cv2.imwrite(os.path.join(finish_removing_folder, file_sequence_order + ".jpg"), img)
        except:
            print(file_sequence_order)

