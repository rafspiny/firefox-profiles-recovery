class Profile:
    """
    Model a Firefox profile
    """

    available_keys = ['name', 'isRelative', 'path', 'isDefault']

    def __init__(self, profile_id=-1, name=None, isRelative=False, path=None, isDefault=False):
        self.name = name
        self.isRelative = isRelative
        self.path = path
        self.isDefault = isDefault
        self.id = int(profile_id)
        self.__validate_name__()

    def load(self, **kwargs):
        """
        Load a bunch of params into the object
        :param kwargs:
        :return:
        """
        for key in Profile.available_keys:
            if key in kwargs:
                self.__setattr__(key, kwargs[key])
        self.__validate_name__()

    def __validate_name__(self):
        """
        Validate the name. If it is not defined, extract it from the path
        :return:
        """
        # check the name
        if self.name is None and self.path is not None:
            self.name = self.path.split('.')[1]

    def stringify(self, override_id=None):
        """
        Return a valid multiline string representing the pfofile, ready to be added to the profiles.ini file

        :param override_id:
        :return:
        """
        if override_id is None:
            override_id = int(self.id)
        return """
[Profile%d]
Name=%s
IsRelative=%d
Path=%s
Default=%d
""" % (override_id, self.name, self.isRelative, self.path, self.isDefault)
