import cv2
import numpy as np
import os
from flask import Blueprint, jsonify, request, json

from infographicsLoader import color_helper
from treeconstructor.treeConstructor import featureExtractionPipeline
from utils.preordertraversal import getLeftRightNumber, flattenlightconstructedtree, flattenheavyconstructedtree, addFieldsBackToLightTree
from vaeacimputation import impute
from variables import *

process_image_api = Blueprint('process_image', __name__)

SUPPORT_NODE_UPPER = 18
SUPPORT_NODE_LOWER = 3
RETURNED_PALETTE_NUM = 20

@process_image_api.route('/getFeaturesAndTreeStructure', methods=['POST'])
def getFeaturesAndTreeStructure():
    params = request.get_json()
    num_in_img = params.get('numInImg')
    img_file_name = os.path.join(DATA_ROOT, INFOGRAPHICS_FOLDER, "{}.jpg".format(num_in_img))
    bb_file_name = os.path.join(DATA_ROOT, BOUNDING_BOX_FOLDER, "{}.txt".format(num_in_img))

    mode = "4300_infographics"
    constructed_tree = featureExtractionPipeline(img_file_name, bb_file_name, mode, num_in_img)
    light_constructed_tree = getLeftRightNumber(constructed_tree)
    final_constructed_tree, pixel_array_of_node = addFieldsBackToLightTree(light_constructed_tree, constructed_tree, True)
    result = {"constructed_tree": final_constructed_tree, "pixel_array_of_node": pixel_array_of_node}
    return jsonify(result)

@process_image_api.route('/getImputationResults', methods=['POST'])
def getImputationResults():
    params = request.get_json()
    tree_source = params.get('treeSource')
    num_in_img = params.get('numInImg')
    modified_tree = params.get('modifiedTree')
    bind_array = params.get('bindArray')

    REPEAT_TIME = 5
    VECTOR_LEN = 169  # the vector len
    # load color pair dicts
    dirname = os.path.dirname(__file__)
    json_data = open(os.path.join(dirname, "name_color_dict.json"), "r")
    name_color_dict = json.load(json_data)

    res = np.zeros((REPEAT_TIME, VECTOR_LEN))

    res[:,0] = np.full((REPEAT_TIME),num_in_img)

    if tree_source == "img":
        img_file_name = os.path.join(DATA_ROOT, INFOGRAPHICS_FOLDER, "{}.jpg".format(num_in_img))
        bb_file_name = os.path.join(DATA_ROOT, BOUNDING_BOX_FOLDER, "{}.txt".format(num_in_img))
        img = cv2.imread(img_file_name)
        img_bg_color = color_helper.find_background_color(img)
        img_bg_color = img_bg_color / 255.
    else:
        img_bg_color = np.array([0.0,0.0,0.0])

    res[:, [1, 2, 3]] = np.repeat(img_bg_color.reshape((1,-1)), REPEAT_TIME, axis=0)
    res[:, [4, 5, 6]] = np.repeat(np.array([0, 0.0, 0.0]).reshape((1, -1)), REPEAT_TIME, axis=0)

    flatten_tree = flattenheavyconstructedtree(modified_tree)
    ind = 0
    node_id = np.array([])
    element_area = np.array([])
    for key, node in flatten_tree.items():
        if ind >= SUPPORT_NODE_UPPER:
            break
        node_id = np.append(node_id, int(key))
        left_number = node['left_number']
        right_number = node['right_number']
        ty = 1
        rh = node['relative_height']
        rw = node['relative_width']
        ra = node['relative_pixel_area']
        element_area = np.append(element_area, 0 if np.isnan(ra) else ra)
        res[:, [7 + ind * 9, 8 + ind * 9, 9 + ind * 9, 10 + ind * 9, 11 + ind * 9, 12 + ind * 9]] = np.repeat(np.array([left_number, right_number, ty, rh, rw, ra]).reshape((1,-1)), REPEAT_TIME, axis=0)
        rgb_color = node['rgb_user_specific_color']
        if rgb_color == None:
            color_name = node['color_name']
            if color_name != None:
                available_colors = np.array(name_color_dict[color_name])
                colors = available_colors[np.random.choice(available_colors.shape[0], size=REPEAT_TIME, replace=False)]
            else:
                colors = np.full((REPEAT_TIME, 3),np.nan)
        else:
            colors = np.repeat(np.array(rgb_color).reshape(1,-1), REPEAT_TIME, axis=0)
        if not np.isnan(np.sum(colors)):
            colors = cv2.cvtColor(np.reshape(colors.astype('uint8'), (1, -1, 3)), cv2.COLOR_RGB2LAB)
            colors = np.reshape(colors, (-1,3))
            colors = colors / 255.
        res[:,[13 + ind * 9, 14 + ind * 9, 15 + ind * 9]] = colors
        ind = ind + 1


    while ind < SUPPORT_NODE_UPPER:
        empty = [1, 1, 1, 1, 1, 1, 1, 1, 1]
        res[:,[7 + ind * 9, 8 + ind * 9, 9 + ind * 9, 10 + ind * 9, 11 + ind * 9, 12 + ind * 9, 13 + ind * 9, 14 + ind * 9, 15 + ind * 9]] = np.repeat(np.array(empty).reshape((1,-1)), REPEAT_TIME, axis=0)
        ind = ind + 1
    # ------------get imputation results------------ #
    imputation_results = impute(res[:,1:])
    node_num = len(node_id)
    color_imputation_results = np.zeros((imputation_results.shape[0],node_num * 3))
    for i in range(0, node_num):
        color_imputation_results[:,i * 3] = imputation_results[:,12 + i * 9] * 255
        color_imputation_results[:,i * 3 + 1] = imputation_results[:, 13 + i * 9] * 255
        color_imputation_results[:,i * 3 + 2] = imputation_results[:, 14 + i * 9] * 255

    color_imputation_results = np.reshape(color_imputation_results, (color_imputation_results.shape[0],-1, 3))
    color_imputation_results = cv2.cvtColor(color_imputation_results.astype('uint8'), cv2.COLOR_LAB2RGB)

    # make the bind element with the same color
    uni_bind_flag = np.unique(bind_array)
    for flag in uni_bind_flag:
        if flag == -1:
            continue
        element_index_with_flag = np.where(bind_array == flag)[0]
        probability = element_area[element_index_with_flag]
        probability = probability / sum(probability)
        selected_index = np.random.choice(element_index_with_flag, 1, p=probability)[0]
        selected_color = color_imputation_results[:,selected_index]
        replace_color_array = np.repeat(selected_color,len(element_index_with_flag),axis=0)
        replace_color_array = np.reshape(replace_color_array, (color_imputation_results.shape[0], len(element_index_with_flag), 3))
        color_imputation_results[:,element_index_with_flag] = replace_color_array

    np.random.shuffle(color_imputation_results)
    result = {'rgb_imputation_results' : color_imputation_results.tolist(), 'corresponding_ids': node_id.tolist()}

    return jsonify(result)