from infographicsLoader.color_helper import *

class DataComponent():
    def __init__(self, params, img):
        """
        :param params: 5 figures in one line read from bounding box txt
        :param img: in bgr; rows x columns = height x width
        """
        self._img_height = img.shape[0]
        self._img_width = img.shape[1]

        self.type = int(params[0])

        self.location = {
            "x": float(params[1]),   # x: left -> right
            "y": float(params[2]),   # y: top -> bottom
            "w": float(params[3]),   # w: left -> right
            "h": float(params[4])    # h: top -> bottom
        }

        [[tl_i, tl_j], [br_i, br_j]] = self.getTopLeftAndBottomRightConnerIJ()

        self.conner = {   ## TopLeftAndBottomRightConner used in img[i,j]
            "tl_i": tl_i,
            "tl_j": tl_j,
            "br_i": br_i,
            "br_j": br_j
        }

        bb_content = img[tl_i:br_i, tl_j:br_j]

        self.colors = kmeans_main_colors_in_bounding_boxes(bb_content)

    def getTopLeftAndBottomRightConnerIJ(self):
        """
        x,y is for opencv img coordinate. X: left to right => width; Y: top to bottom => height
        x,y is the center point
        we first need to calculate two conners (x,y)
        then turn (x,y) to (i,j). basically, (i,j) = (y,x)
        :return:
        """
        tl_x = int((self.location["x"] - self.location["w"]/2) * self._img_width)
        tl_y = int((self.location["y"] - self.location["h"]/2) * self._img_height)

        br_x = int((self.location["x"] + self.location["w"]/2) * self._img_width)
        br_y = int((self.location["y"] + self.location["h"]/2) * self._img_height)

        tl_x = max(tl_x, 0)
        tl_y = max(tl_y, 0)
        br_x = min(self._img_width - 1, br_x)
        br_y = min(self._img_height - 1, br_y)

        return [[tl_y, tl_x],[br_y, br_x]]  # [[tl_i, tl_j],[br_i, br_j]]

class DataComponentForTimelineFormat():
    def __init__(self, params, img):
        """
        :param params: 6 figures in one line read from bounding box txt
        :param img: in bgr; rows x columns = height x width
        """
        self._img_height = img.shape[0]
        self._img_width = img.shape[1]

        self.conner = {   ## TopLeftAndBottomRightConner used in img[i,j]
            "tl_i": int(params[1]),
            "tl_j": int(params[0]),
            "br_i": int(params[3]),
            "br_j": int(params[2]),
        }

        tl_i, tl_j, br_i, br_j = self.conner["tl_i"], self.conner["tl_j"],self.conner["br_i"],self.conner["br_j"]
        self.type = int(params[4])

        self.confidence = float(params[5])
        bb_content = img[tl_i:br_i, tl_j:br_j]

        self.colors = kmeans_main_colors_in_bounding_boxes(bb_content)