import os.path as fs
import os
import re
import model.models


class ProfileSearcher:
    """
    Look for profiles
    """

    def __init__(self, ini_path=None, profile_dir=None):
        # TODO maybe I should set ini_path and profile_dir to their respective linux, mac and windows value
        self.recoverable_profiles = {}
        self.present_on_fs = {}
        self.present_in_profile_file = {}
        self.inspect_profile(ini_path=ini_path)
        self.inspect_fs(profile_dir=profile_dir)

    def inspect_profile(self, ini_path):
        """
        Read the profiles.ini file
        :return:
        """
        if ini_path is None:
            raise Exception("No profiles.ini path has been specified")

        if not fs.exists(ini_path):
            raise Exception("File %s do not exists" % (ini_path))
        fd = open(ini_path, 'r')
        lines = [line.strip() for line in fd]
        fd.close()
        current_profile = None
        for line in lines:
            match = re.search("^\[Profile(\d+)\]$", line)
            if match is not None:
                # if the object is not null, add it to the list
                if current_profile is not None:
                    self.present_in_profile_file[current_profile.path] = current_profile

                # extract the id and builds the object
                current_id = match.group(1)
                current_profile = model.models.Profile(profile_id=current_id)

            match = re.search("^Name=(.*)", line)
            if match is not None:
                name = match.group(1)
                current_profile.name = name

            match = re.search("^IsRelative=(.*)", line)
            if match is not None:
                current_relative = int(match.group(1))
                current_profile.isRelative = current_relative == 1

            match = re.search("^Path=(.*)", line)
            if match is not None:
                current_path = match.group(1)
                current_profile.path = current_path

            match = re.search("^Default=(.*)", line)
            if match is not None:
                current_default = int(match.group(1))
                current_profile.isDefault = current_default == 1

        # finished reading lines, check the last profile
        if current_profile is not None:
            self.present_in_profile_file[current_profile.path] = current_profile

    def inspect_fs(self, profile_dir):
        """
        Read the fs looking for firefox profiles
        :return:
        """
        if profile_dir is None:
            raise Exception("Mozilla directory is not specified")
        if not fs.exists(profile_dir):
            raise Exception("Dir %s does not exists" % profile_dir)

        # Do not need to store the full profile object here, the path is enough
        self.present_on_fs = [dir for dir in os.listdir(profile_dir) if
                os.path.isdir(os.path.join(profile_dir, dir)) and re.search('\.', dir) is not None]

    def compute_recoverable(self):
        """
        Compute the differences between the profiles from the fs and the one listed in the profiles.ini file
        :return:
        """
        recoverable = set(self.present_on_fs) - set(self.present_in_profile_file)
        self.recoverable_profiles = [model.models.Profile(path=path) for path in recoverable]

    def print(self):
        print("From profiles: ")
        for x in self.present_in_profile_file:
            print("Profile: %s" % x)
        print("From fs: ")
        for x in self.present_on_fs:
            print("Profile: %s" % x)
        print("Recoverable: ")
        for x in self.recoverable_profiles:
            print("Profile: %s" % x.name)
