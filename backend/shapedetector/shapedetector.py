import cv2

class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):
        shape = "unidentified"
        shape_type_code = -1
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        if len(approx) == 3:
            shape = "triangle"
            shape_type_code = 3
        elif len(approx) == 4:
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w / float(h)
            shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
            # if the shape is a pentagon, it will have 5 vertices
            shape_type_code = 1 if ar >= 0.95 and ar <= 1.05 else 2
        elif len(approx) == 5:
            shape = "pentagon"
            shape_type_code = 5
        else:
            shape = "circle"
            shape_type_code = 6
        return shape_type_code