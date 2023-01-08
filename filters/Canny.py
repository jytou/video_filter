from abstract_filter import Filter, FilterParameter
import cv2
import numpy as np

class Canny(Filter):
    """
    An edge detection filter, using the Canny filter.
    """
    param_horiz = FilterParameter("Horizontal", 1.0, 1000.0, 100.0)
    param_vert = FilterParameter("Vertical", 1.0, 1000.0, 100.0)
    config = [param_horiz, param_vert]

    @staticmethod
    def get_filter_name():
        return "Edge Detection (Canny)"

    @staticmethod
    def apply_filter(frame, params):
        # Do Canny on all 3 channels - separate them first
        (B, G, R) = cv2.split(frame)
        # Apply on each channel
        B_cny = cv2.Canny(B, params[Canny.param_horiz.name], params[Canny.param_vert.name])
        G_cny = cv2.Canny(G, params[Canny.param_horiz.name], params[Canny.param_vert.name])
        R_cny = cv2.Canny(R, params[Canny.param_horiz.name], params[Canny.param_vert.name])
        # Merge all channels back to a single image
        return cv2.merge([B_cny, G_cny, R_cny])

    @staticmethod
    def get_config():
        return Canny.config

