from pkgutil import walk_packages


class FilterLoader:
    """
    A class used to load all filters in the directory "filters"
    """
    @staticmethod
    def load_filters(root_import_path, is_valid=lambda entity: True):
        """Returns modules in ``root_import_path`` that satisfy the ``is_valid`` test

        :param root_import_path: A string name for importing (i.e. "myapp").
        :param is_valid: A callable that takes a variable and returns ``True``
                         if it is of interest to us."""

        classes = {}

        for finder, name, is_pkg in walk_packages(root_import_path):
            if is_pkg:
                continue
            filters_mod = __import__("filters." + name)
            actual_mod = getattr(filters_mod, name)
            c = getattr(actual_mod, name)
            classes[c.get_filter_name()] = c
        res = {key: val for key, val in sorted(classes.items(), key=lambda ele: ele[0])}
        return res
