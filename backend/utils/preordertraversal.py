from functools import cmp_to_key
import cv2
import numpy as np
# ----- helper ------
def addFieldsBackToLightTree(light_tree, tree, NOT_NUMPY_ARRAY):
    def addFieldsDFS(children):
        if children == []:
            return
        for child in children:
            cur_id = child["id"]
            ori_element = tree[str(cur_id)]
            child.update({f: ori_element[f] for f in interested_fields})
            if NOT_NUMPY_ARRAY:
                child["pixel_array"] = child["pixel_array"].astype(int).tolist()
                pixel_array_of_node[str(cur_id)] = child["pixel_array"]
                child["color"] = child["color"].astype(int).tolist() # this color is in lab space
                child["rgb_color"] = cv2.cvtColor(np.reshape(np.array(child["color"]).astype('uint8'), (1,1,3)),cv2.COLOR_Lab2RGB)
                child["rgb_color"] = np.reshape(child["rgb_color"], (3,)).astype(int).tolist()
                child["relative_height"] = float(child["relative_height"])
                child["relative_width"] = float(child["relative_width"])
                child["conner"] = [int(i) for i in child["conner"]]
            addFieldsDFS(child["children"])

    pixel_array_of_node = {}

    interested_fields = ["type", "relative_height", "relative_width", "relative_pixel_area", "color", "pixel_array"]
    cur_id = 0
    temp = light_tree["0"]
    ori_element = tree[str(cur_id)]
    temp.update({f: ori_element[f] for f in interested_fields})
    addFieldsDFS(temp["children"])
    if NOT_NUMPY_ARRAY:
        temp["pixel_array"] = temp["pixel_array"].astype(int).tolist()
        pixel_array_of_node["0"] = temp["pixel_array"]
        temp["color"] = temp["color"].astype(int).tolist()  # this color is in lab space
        temp["rgb_color"] = cv2.cvtColor(np.reshape(np.array(temp["color"]).astype('uint8'), (1, 1, 3)),
                                          cv2.COLOR_Lab2RGB)
        temp["rgb_color"] = np.reshape(temp["rgb_color"], (3,)).astype(int).tolist()
        temp["relative_height"] = float(temp["relative_height"])
        temp["relative_width"] = float(temp["relative_width"])
        temp["conner"] = [int(i) for i in temp["conner"]]

    return light_tree, pixel_array_of_node




def nestedTreeDFS(children, tree):
    for element in children:
        cur_id = element["id"]
        if cur_id not in tree:
            element["children"] = []
        else:
            cur_children = tree[cur_id]
            tree.pop(cur_id, None)
            res = nestedTreeDFS(cur_children, tree)
            element["children"] = res
    return children

def sortedTreeDFS(children):
    if children == []:
        return []
    children = sorted(children,
                      key=cmp_to_key(lambda item1, item2 :
                      item1['conner'][0] - item2['conner'][0] if (item1['conner'][0] - item2['conner'][0]) > 10
                      else item1['conner'][1] - item2['conner'][1]))
    for child in children:
        cur_children = child["children"]
        res = sortedTreeDFS(cur_children)
        child["children"] = res
    return children

def leftRightNumberDFS(children):
    global number
    if children == []:
        return []
    for child in children:
        child["left_number"] = number
        number = number + 1
        cur_children = child["children"]
        leftRightNumberDFS(cur_children)
        child["right_number"] = number
        number = number + 1



def getLeftRightNumber(tree):
    if tree == {}:
        light_tree = {'1': {'id': 1, 'father_id': 0, 'conner': [17, 37, 90, 99]},
             '2': {'id': 2, 'father_id': 0, 'conner': [32, 46, 66, 61]},
             '4': {'id': 4, 'father_id': 3, 'conner': [38, 227, 69, 258]},
             '3': {'id': 3, 'father_id': 0, 'conner': [33, 98, 74, 265]},
             '5': {'id': 5, 'father_id': 0, 'conner': [34, 51, 73, 95]},
             '6': {'id': 6, 'father_id': 0, 'conner': [83, 206, 155, 268]},
             '8': {'id': 8, 'father_id': 7, 'conner': [104, 46, 134, 76]},
             '7': {'id': 7, 'father_id': 0, 'conner': [97, 39, 139, 217]},
             '9': {'id': 9, 'father_id': 0, 'conner': [99, 210, 138, 252]},
             '10': {'id': 10, 'father_id': 0, 'conner': [149, 38, 220, 98]},
             '12': {'id': 12, 'father_id': 11, 'conner': [170, 228, 199, 257]},
             '11': {'id': 11, 'father_id': 0, 'conner': [164, 97, 205, 265]},
             '14': {'id': 14, 'father_id': 13, 'conner': [235, 46, 265, 76]},
             '13': {'id': 13, 'father_id': 0, 'conner': [222, 39, 270, 243]},
             '15': {'id': 15, 'father_id': 0, 'conner': [165, 52, 205, 94]},
             '16': {'id': 16, 'father_id': 0, 'conner': [214, 206, 286, 266]},
             '17': {'id': 17, 'father_id': 0, 'conner': [230, 210, 270, 252]},
             '0': {'id': 0, 'father_id': -1, 'conner': [0, 0, 299, 299]}}
    else:
        fields = ['id', 'father_id', 'conner']
        light_tree = {key: {x: tree[key][x] for x in fields} for key in tree.keys()}


    grouped_by_father_tree = {}
    for key, value in light_tree.items():
        cur_father_id = value["father_id"]
        if cur_father_id == -1:
            continue
        if cur_father_id not in grouped_by_father_tree:
            grouped_by_father_tree[cur_father_id] = [value]
        else:
            grouped_by_father_tree[cur_father_id].append(value)

    fids = list(grouped_by_father_tree.keys())
    for fid in fids:
        if fid in grouped_by_father_tree:
            children = grouped_by_father_tree[fid]
            nestedTreeDFS(children, grouped_by_father_tree)

    temp = grouped_by_father_tree[0]
    grouped_by_father_tree.pop(0,None)

    grouped_by_father_tree['0'] = light_tree['0']
    grouped_by_father_tree['0']["children"] = temp
    res = sortedTreeDFS(temp)
    grouped_by_father_tree['0']["children"] = res

    global number
    number = 0

    grouped_by_father_tree['0']["left_number"] = number
    number = number + 1
    temp = grouped_by_father_tree['0']["children"]
    leftRightNumberDFS(temp)
    grouped_by_father_tree['0']["right_number"] = number

    return grouped_by_father_tree

# flatten light tree
def processlightconstructedtree(value, temp_dict):
    temp_dict[str(value['id'])] = {'left_number' : int(value['left_number']), 'right_number' : int(value['right_number'])}
    children_list = value['children']
    for child in children_list:
        processlightconstructedtree(child, temp_dict)
    return

def flattenlightconstructedtree(light_constructed_tree):
    temp_dict = {}
    for key, value in light_constructed_tree.items():
        processlightconstructedtree(value, temp_dict)
    return temp_dict

# flatten complete tree
def processheavyconstructedtree(value, temp_dict):
    temp_dict[str(value['id'])] = {
        'id':int(value['id']),
        'father_id': int(value['father_id']) if 'father_id' in value else np.nan,
        'left_number' : int(value['left_number']) if 'left_number' in value else np.nan,
        'right_number' : int(value['right_number']) if 'right_number' in value else np.nan,
        'type': int(value['type']) if 'type' in value else np.nan,
        'relative_height':float(value['relative_height']) if 'relative_height' in value else np.nan,
        'relative_width': float(value['relative_width']) if 'relative_width' in value else np.nan,
        'relative_pixel_area':float(value['relative_pixel_area']) if 'relative_pixel_area' in value else np.nan,
        'rgb_user_specific_color': value['rgb_user_specific_color'] if "rgb_user_specific_color" in value else None,
        'color_name': value['color_name'] if 'color_name' in value else None,
    }
    children_list = value['children']
    for child in children_list:
        processheavyconstructedtree(child, temp_dict)
    return

def flattenheavyconstructedtree(constructed_tree):
    temp_dict = {}
    for key, value in constructed_tree.items():
        processheavyconstructedtree(value, temp_dict)
    return temp_dict



if __name__ == "__main__":
    constructed_tree = getLeftRightNumber({})
