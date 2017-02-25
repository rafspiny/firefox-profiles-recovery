import os.path as fs
import os
import re
import model.models


class ProfileGenerator:
    """
    Write profiles to ini file
    """

    def __init__(self, ini_path=None, profiles=[]):
        if ini_path is None:
            raise Exception("No profiles.ini path has been specified")
        if not fs.exists(ini_path):
            raise Exception("File %s do not exists" % (ini_path))

        if profiles is None:
            raise Exception('No previous list of profiles specified')
        check_list = [profile for profile in profiles if not isinstance(profile, model.models.Profile)]
        if len(check_list) > 0:
            raise Exception('List of profiles has invalid objects')

        self.ini_path = ini_path
        self.present_in_profile_file = []
        # It is not enough to do self.new_id = len(profiles)
        current_id = -1
        for profile in profiles:
            current_id = profile.__getattribute__('id')
        self.new_id = current_id + 1

    def add_profile(self, profile):
        """
        Add a profile to the ini file

        :param profile: Profile to add
        :return:
        """
        if profile is None:
            raise Exception('Profile is None')
        if not isinstance(profile, model.models.Profile):
            raise Exception('Profile is not a valid object')

        fd = os.open(self.ini_path, os.O_WRONLY | os.O_APPEND)

        # content of fake profiles.ini
        content = profile.stringify(self.new_id)
        self.new_id += 1

        os.write(fd, content.encode())
        os.close(fd)
