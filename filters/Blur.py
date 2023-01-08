from abstract_filter import Filter, FilterParameter
import cv2


class Blur(Filter):
    """
    A simple blurring filter using a matrix of a given size horizontally and vertically
    """
    param_horiz = FilterParameter("Horizontal", 2.0, 100.0, 10.0)
    param_vert = FilterParameter("Vertical", 2.0, 100.0, 10.0)
    config = [param_horiz, param_vert]

    @staticmethod
    def get_filter_name():
        return "Blur"

    @staticmethod
    def apply_filter(frame, params):
        # Simply call cv2.blur()
        return cv2.blur(frame, (round(params["Horizontal"]), round(params["Vertical"])))

    @staticmethod
    def get_config():
        return Blur.config

