from abstract_filter import Filter, FilterParameter
import cv2


class Grayscale(Filter):
    """
    A simple grayscale filter
    """
    @staticmethod
    def get_filter_name():
        return "Grayscale"

    @staticmethod
    def apply_filter(frame, params):
        # Switch to grayscale and then back to BGR since the main window expects the 3 channels to be present
        return cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)

    @staticmethod
    def get_config():
        return []

