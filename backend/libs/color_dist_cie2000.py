from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000

def dist_cie2000(bgr1, bgr2):
    """

    :param bgr1: for example [227, 236, 250]
    :param bgr2: for example [67, 99, 161]
    :return: delta_e_cie2000 distance
    """
    color1_rgb = sRGBColor(bgr1[2] / 255.0, bgr1[1] / 255.0, bgr1[0] / 255.0)

    color2_rgb = sRGBColor(bgr2[2] / 255.0, bgr2[1] / 255.0, bgr2[0] / 255.0)

    # Convert from RGB to Lab Color Space
    color1_lab = convert_color(color1_rgb, LabColor)

    # Convert from RGB to Lab Color Space
    color2_lab = convert_color(color2_rgb, LabColor)

    # Find the color difference
    delta_e = delta_e_cie2000(color1_lab, color2_lab)

    return delta_e