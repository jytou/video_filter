class Filter:
    """
    A template class representing an image filter
    """

    @staticmethod
    def get_filter_name():
        """
        :return: this filter's name
        """
        pass

    @staticmethod
    def apply_filter(frame, params):
        """
        This function applies the current filter to the frame and returns the filtered frame
        :param frame: an image
        :param params: dictionary of parameters in the form [name => value]
        :return: the filtered image/frame
        """
        pass

    @staticmethod
    def get_config():
        """
        Returns the configuration needed for this filter
        :return: a list of FilterParameters
        """
        pass


class FilterParameter:
    """
    A class representing a parameter used for a filter
    """
    def __init__(self, name, min_val, max_val, default_val):
        """
        Initialize the parameter
        :param name: name of the parameter
        :param min_val: minimum value (float)
        :param max_val: maximum value (float)
        :param default_val: default value (float)
        """
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.default_val = default_val
