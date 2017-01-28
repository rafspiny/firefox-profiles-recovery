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
        self.id = profile_id

    def load(self, **kwargs):
        for key in Profile.available_keys:
            if key in kwargs:
                self.__setattr__(key, kwargs[key])
        # check the name
        if self.name is None:
            self.name = self.path.split('.')[1]

    def stringify(self, override_id=None):
        if override_id is None:
            override_id = self.id
        return """
[Profile%d]
Name=%s
IsRelative=%d
Path=%s
Default=%d
""" % (override_id, self.name, self.isRelative, self.path, self.isDefault)
