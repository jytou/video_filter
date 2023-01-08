from abstract_filter import Filter, FilterParameter
import cv2
import numpy as np

class Sharpen(Filter):
    """
    A basic sharpening filter
    """
    @staticmethod
    def get_filter_name():
        return "Sharpen"

    @staticmethod
    def apply_filter(frame, params):
        # Use a simple sharpening matrix
        return cv2.filter2D(frame, -1, np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]))

    @staticmethod
    def get_config():
        return []

