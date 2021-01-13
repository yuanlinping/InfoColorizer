import cv2
import numpy as np
import math
import logging
logger = logging.getLogger('tester')
logger.setLevel(logging.DEBUG)

class Montage(object):
    def __init__(self,initial_image):
        self.montage = initial_image
        self.height, self.width= self.montage.shape[:2]

    def append(self,image):
        new_image = np.full((image.shape[0], self.width, 3),255)
        try:
            new_image[:,:image.shape[1],:] = image
        except:
            logging.debug("fail to append elements or legends")
        self.montage = np.vstack((self.montage, new_image))

    def show(self):
        cv2.imshow('montage',self.montage)
        cv2.waitKey()
        cv2.destroyAllWindows()

def generate_color_legend(colors, legend_width):
    """

    :param colors: n colors x 3; in bgr
    :param legend_width:
    :return:
    """
    gap = math.ceil(legend_width / len(colors))
    legend = np.full((1+15+1+5, legend_width, 3),255)

    legend[0,:,:] = [0,0,0] # white
    for i in range(0, legend_width, gap):
        legend[1:16, i: i + gap, :] = colors[math.floor(i/gap)]
    legend[16,:,:] = [0,0,0] #
    return legend.astype('uint8')


def stitchElementsAndExtractedColors(img, annotated_img, infographics_elements, img_theme_colors, output_file):
    """

    :param img: img without annotation
    :param annotated_img:
    :param infographics_elements: {"title": [<Element>], "arrow":[<Element>]}
    :param img_theme_colors: 2D array, in bgr;
    :param output_file:
    :return:
    """
    resize_height, resize_width = np.multiply(img.shape[:2], 0.5).astype('int')
    annotated_img = cv2.resize(annotated_img, (resize_width, resize_height))  ## resize(_, (width, height))
    m = Montage(annotated_img)

    bg_legend = generate_color_legend(img_theme_colors, resize_width)
    m.append(bg_legend)

    for key, values in infographics_elements.items():
        for curElem in values:
            tl_i, tl_j, br_i, br_j = curElem.conner["tl_i"], curElem.conner["tl_j"], curElem.conner["br_i"], curElem.conner["br_j"]
            bb_content = img[tl_i:br_i, tl_j:br_j]

            colors = [curElem.colors["bg_color"], curElem.colors["main_color"], curElem.colors["other_color"]]

            legend = generate_color_legend(colors, resize_width)

            m.append(bb_content)
            m.append(legend)

    cv2.imwrite(output_file, m.montage)





