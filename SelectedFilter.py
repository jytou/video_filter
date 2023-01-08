class SelectedFilter:
    """
    A simple container for a filter and its attributes.

    Attributes
    ----------
    filter : Filter (one of the filters in the subdirectory "filters")
        the filter itself
    widget : QWidget
        a widget associated to the filter, typically a frame that contains the sliders, labels, etc.
    index : int
        the index of the filter in the list of currently selected filters
    vals : array of objects {name => value}
        the current values of the filter's parameters
    """
    def __init__(self, filter, widget, index, vals):
        self.filter = filter
        self.widget = widget
        self.index = index
        self.vals = vals
