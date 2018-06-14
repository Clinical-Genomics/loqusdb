# -*- coding: utf-8 -*-

class DotDict(dict):
    """
    Example:
    test = DotDict(last_name='Pool', age=24, sports=['Soccer'])
    """
    def __init__(self, *args, **kwargs):
        super(DotDict, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                try:
                    for key, value in arg.iteritems():
                        self[key] = value
                except AttributeError:
                    for key, value in arg.items():
                        self[key] = value

        if kwargs:
            try:
                for key, value in kwargs.iteritems():
                    self[key] = value
            except AttributeError:
                for key, value in kwargs.items():
                    self[key] = value

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(DotDict, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(DotDict, self).__delitem__(key)
        del self.__dict__[key]
