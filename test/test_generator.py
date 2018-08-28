from ddt import ddt, unpack, data
import unittest
import logic.profile_generator
import model.models
import os
import tempfile

basedir = None
unexisting_directory = None
real_profile_path = None
real_profiles_dir = None
fake_profiles = ['s6zuh3tz.default', '2h2h4h.mr_x', '12k4k8.doctor_who']


def create_fake_profile(profile):
    """
    Create a fake profile in the testing directory
    :param profile: profile name
    :return:
    """
    if not os.path.exists('%s%s%s' % (GeneratorTestCase.basedir, GeneratorTestCase.real_profiles_dir, profile)):
        os.mkdir('%s%s%s' % (GeneratorTestCase.basedir, GeneratorTestCase.real_profiles_dir, profile))


@ddt
class GeneratorTestCase(unittest.TestCase):

    def tearDown(self):
        """
        Remove the directories for the fake profiles
        :return:
        """
        super().tearDown()
        for profile in fake_profiles:
            if os.path.exists('%s%s%s' % (GeneratorTestCase.basedir, GeneratorTestCase.real_profiles_dir, profile)):
                os.removedirs('%s%s%s' % (GeneratorTestCase.basedir, GeneratorTestCase.real_profiles_dir, profile))

        if os.path.exists('%s%s%s' % (GeneratorTestCase.basedir, GeneratorTestCase.real_profiles_dir, 's6zuh3TZ.default')):
            os.removedirs('%s%s%s' % (GeneratorTestCase.basedir, GeneratorTestCase.real_profiles_dir, 's6zuh3TZ.default'))


    @classmethod
    def setUpClass(cls):
        """
        Prepare the FS with all the directory needed for the test:
        - a profile.ini file
        - a profiles direcotry that wil hold the fake profiles
        - create a placer that hold the name of a directory that does not exists.
        :return:
        """
        cls.basedir = tempfile.mkdtemp(suffix='test', prefix='mozilla')
        cls.unexisting_directory = '/bar'
        tmp_unexisting_directory = '%s%s' % (cls.basedir, cls.unexisting_directory)

        if os.path.exists(tmp_unexisting_directory):
            os.removedirs(tmp_unexisting_directory)

        # Make sure a bunch of fake profiles are created, along with a valid profiles.ini file
        cls.real_profiles_dir = '/profiles/'
        os.makedirs('%s%s' % (cls.basedir, cls.real_profiles_dir), exist_ok=True)
        cls.real_profile_path = '/profiles/profiles.ini'
        real_profile_fd = os.open('%s%s' % (cls.basedir, cls.real_profile_path), os.O_CREAT | os.O_WRONLY | os.O_TRUNC)

        # content of fake profiles.ini
        content = """
[General]
StartWithLastProfile=1

[Profile0]
Name=default
IsRelative=1
Path=s6zuh3tz.default
Default=1
"""

        os.write(real_profile_fd, content.encode())
        os.close(real_profile_fd)

        if not os.path.exists('%s%s' % (cls.basedir, cls.real_profiles_dir)):
            os.mkdir('%s%s' % (cls.basedir, cls.real_profiles_dir))

    @classmethod
    def tearDownClass(cls):
        """
        Clean the temp directory
        :return:
        """
        os.remove('%s%s' % (cls.basedir, cls.real_profile_path))
        os.removedirs('%s%s' % (cls.basedir, cls.real_profiles_dir))
        if os.path.exists(cls.basedir):
            os.removedirs(cls.basedir)
        super().tearDownClass()

    @data(
        (None, None, 'No profiles.ini path has been specified'),
        ("/profiles.ini", None, 'File .*/profiles.ini do not exists'),
        ("/profiles/profiles.ini", None, 'No previous list of profiles specified'),
        ("/profiles/profiles.ini", [{'id': 5}], 'List of profiles has invalid objects'),
    )
    @unpack
    def test_default_constructor_param(self, path, profiles, exception_message):
        """
        Verify that an exception is raised when invalid parameters are passed to the constructor
        :param path: The path for the profiles.ini file
        :param exception_message: The expected error message
        :return:
        """
        if path is not None:
            path = '%s%s' % (GeneratorTestCase.basedir, path)

        with self.assertRaisesRegex(Exception, exception_message):
            logic.profile_generator.ProfileGenerator(ini_path=path, profiles=profiles)

    @data(
        ("/profiles/profiles.ini", [], 0),
        ("/profiles/profiles.ini", [{'profile_id': 5}], 6),
    )
    @unpack
    def test_default_constructor_good_param(self, path, list_profiles, expected_id):
        """
        Verify default initialization
        :param path: Path of the ini file
        :param list_profiles: list of profiles already present
        :return:
        """
        if path is not None:
            path = '%s%s' % (GeneratorTestCase.basedir, path)

        # convert dict to profile
        list_of_profiles_objs = [model.models.Profile(**profile_dict) for profile_dict in list_profiles]

        generator = logic.profile_generator.ProfileGenerator(ini_path=path, profiles=list_of_profiles_objs)
        self.assertEqual(generator.new_id, expected_id)

    @data(
        ('/profiles/profiles.ini', None, 'Profile is None'),
        ('/profiles/profiles.ini', object(), 'Profile is not a valid object'),
    )
    @unpack
    def test_add_profile_fails(self, path, profile, expected_message):
        if path is not None:
            path = '%s%s' % (GeneratorTestCase.basedir, path)
        # if profile is not None:
        #    profile = model.models.Profile(**profile)

        generator = logic.profile_generator.ProfileGenerator(ini_path=path)
        with self.assertRaisesRegex(Exception, expected_message):
            generator.add_profile(profile)

    @data(
        ('/profiles/profiles.ini', [{'profile_id':0}], [{'name':'profile', 'is_relative':True, 'is_default':False, 'path':'profile.profile', 'profile_id':-1}], """
[General]
StartWithLastProfile=1

[Profile0]
Name=default
IsRelative=1
Path=s6zuh3tz.default
Default=1

[Profile1]
Name=profile
IsRelative=1
Path=profile.profile
Default=0
"""),
    )
    @unpack
    def test_add_profiles(self, path, existing_profiles, profiles_to_add, expected_ini_content):
        """
        Test that the list of recoverable profiles is computed correctly
        For the second parameter, we just need to pass on an ID, nothing more...

        :param path: The path for the profiles.ini file
        :param profiles_to_add: List of profiles to add
        :param expected_ini_content: Expected set of added profiles
        :return:
        """
        # TODO add more test case
        if path is not None:
            path = '%s%s' % (GeneratorTestCase.basedir, path)

        # convert dict to profile
        list_of_profiles_objs = [model.models.Profile(**profile_dict) for profile_dict in existing_profiles]

        generator = logic.profile_generator.ProfileGenerator(ini_path=path, profiles=list_of_profiles_objs)
        for profile in profiles_to_add:
            generator.add_profile(model.models.Profile(**profile))

        with open(path) as myfile:
            data = "".join(line for line in myfile)
        self.assertEqual(data, expected_ini_content)


