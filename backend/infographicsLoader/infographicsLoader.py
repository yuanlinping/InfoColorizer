from variables import *
from infographicsLoader.DataComponent import DataComponent, DataComponentForTimelineFormat
import csv
import cv2

def constructDataComponents(img_file_name, bb_file_name):
    img = cv2.imread(img_file_name)

    infographics_data_components = {
        "title": [],
        "index": [],
        "body_text": [],
        "icon": [],
        "arrow": []
    }

    with open(bb_file_name) as f:
        elements = csv.reader(f, delimiter=" ")
        for params in elements:
            curElem = DataComponent(params, img)
            if curElem.type in TITLE:
                infographics_data_components["title"].append(curElem)
            elif curElem.type in BODY_TEXT:
                infographics_data_components["body_text"].append(curElem)
            elif curElem.type in INDEX:
                infographics_data_components["index"].append(curElem)
            elif curElem.type in ICON:
                infographics_data_components["icon"].append(curElem)
            elif curElem.type in ARROW:
                infographics_data_components["arrow"].append(curElem)
            else:
                print("The element doesn't belong to any classes.")

    f.close()

    return infographics_data_components

def constructDataComponentsForTimelineFormat(img_file_name, bb_file_name):
    img = cv2.imread(img_file_name)

    infographics_data_components = {
        "event_mark": [],
        "event_text": [],
        "annotation_mark": [],
        "annotation_text": [],
        "icon": [],
        "index":[],
        "main_body":[]
    }

    with open(bb_file_name) as f:
        elements = csv.reader(f, delimiter=" ")
        for params in elements:
            curElem = DataComponentForTimelineFormat(params, img)
            if curElem.type in EVENT_MARK:
                infographics_data_components["event_mark"].append(curElem)
            elif curElem.type in EVENT_TEXT:
                infographics_data_components["event_text"].append(curElem)
            elif curElem.type in ANNOTATION_MARK:
                infographics_data_components["annotation_mark"].append(curElem)
            elif curElem.type in ANNOTATION_TEXT:
                infographics_data_components["annotation_text"].append(curElem)
            elif curElem.type in ICON_2:
                infographics_data_components["icon"].append(curElem)
            elif curElem.type in INDEX_2:
                infographics_data_components["index"].append(curElem)
            elif curElem.type in MAIN_BODY:
                infographics_data_components["main_body"].append(curElem)
            else:
                print("The element doesn't belong to any classes.")

    f.close()

    return infographics_data_components