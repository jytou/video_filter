from abstract_filter import Filter, FilterParameter
import cv2


class Luminosity(Filter):
    """
    Simply contrast + luminosity adjustments
    """
    param_contrast = FilterParameter("Contrast", 1.0, 3.0, 1)
    param_luminosity = FilterParameter("Luminosity", 0.0, 100.0, 0.0)
    config = [param_contrast, param_luminosity]

    @staticmethod
    def get_filter_name():
        return "Luminosity"

    @staticmethod
    def apply_filter(frame, params):
        return cv2.convertScaleAbs(frame, alpha=params["Contrast"], beta=params["Luminosity"])

    @staticmethod
    def get_config():
        return Luminosity.config

