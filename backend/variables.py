import os

PERCEPTUAL_DIS_FOR_DISTINCT_BG = 4.0
PERCEPTUAL_DIS_FOR_DISTINCT_BIG = 10.0

PERCEPTUAL_DIS_FOR_DISTINCT_THEME_COLORS = 15.0

WHITE_S_THREH = 20 * 255 / 100
WHITE_V_THREH = 90 * 255 / 100
BLACK_V_THREH = 25 * 255 / 100

dirname = os.path.dirname(__file__)
DATA_ROOT = os.path.join(dirname, "datasets/4300_infographics/")
DATA_ROOT_2 = os.path.join(dirname,"datasets/all_infographics/")

INFOGRAPHICS_FOLDER = "0_infographics/"
BOUNDING_BOX_FOLDER = "0_bounding_box/"

ANNOTATED_FOLDER = "0_annotated_infographics"
STITCH_FOLDER = "feature_v1_res/"
REMOVED_TEXT_ICON_INDEX_FOLDER = "2_removed_text_icon_index"

# ------- 4300 infographics (refer to Lu et al. for the meaning of the following numbers)-------
INDEX = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
         11, 12, 13, 14, 15, 16, 17, 18, 19,
         20, 21, 22, 23, 24, 25, 26]

ARROW = [27, 28, 29, 30, 31, 32, 33, 34]

BODY_TEXT = [35]

ICON = [36]

TITLE = [37]

# ------- all infographics -------
# bounding box of all infographics detected by yolo using format of Zhu et al. [timeline]
EVENT_MARK = [0]
EVENT_TEXT = [1]   # equal to text above
ANNOTATION_MARK = [2]
ANNOTATION_TEXT = [3]  # equal to text above
ICON_2 = [4] # equal to icon above
INDEX_2 = [5] # equal to index above
MAIN_BODY = [6]

# ---- others -----

LOCATION = ["x", "y", "w", "h"]
STATISTIC = ["max", "avg", "min", "std"]

COLOR_CONSIDERED_NUM = 5

BACKBONE_TYPE_NAMES = ["Unrecognized", "LandScape", "Pulse", "Portrait", "Spiral", "Clock", "Star", "Bowl", "Dome", "Down-ladder", "Up-ladder", "Left-wing", "Right-wing"]