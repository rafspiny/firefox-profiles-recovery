from ddt import ddt, unpack, data
import unittest
import logic.profile_crawler
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
    if not os.path.exists('%s%s%s' % (CrawlerTestCase.basedir, CrawlerTestCase.real_profiles_dir, profile)):
        os.mkdir('%s%s%s' % (CrawlerTestCase.basedir, CrawlerTestCase.real_profiles_dir, profile))


@ddt
class CrawlerTestCase(unittest.TestCase):

    def tearDown(self):
        """
        Remove the directories for the fake profiles
        :return:
        """
        super().tearDown()
        for profile in fake_profiles:
            if os.path.exists('%s%s%s' % (CrawlerTestCase.basedir, CrawlerTestCase.real_profiles_dir, profile)):
                os.removedirs('%s%s%s' % (CrawlerTestCase.basedir, CrawlerTestCase.real_profiles_dir, profile))

        if os.path.exists('%s%s%s' % (CrawlerTestCase.basedir, CrawlerTestCase.real_profiles_dir, 's6zuh3TZ.default')):
            os.removedirs('%s%s%s' % (CrawlerTestCase.basedir, CrawlerTestCase.real_profiles_dir, 's6zuh3TZ.default'))


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
        ('/profiles/profiles.ini', None, 'Mozilla directory is not specified'),
        ('/profiles/profiles.ini', '/bar', 'Dir .* does not exists')
    )
    @unpack
    def test_default_constructor_param(self, path, profile_folder, exception_message):
        """
        Verify that an exception is raised when invalid parameters are passed to the constructor
        :param path: The path for the profiles.ini file
        :param profile_folder: The profile direcotry in Firefox
        :param exception_message: The expected error message
        :return:
        """
        if path is not None:
            path = '%s%s' % (CrawlerTestCase.basedir, path)
        if profile_folder is not None:
            profile_folder = '%s%s' % (CrawlerTestCase.basedir, profile_folder)

        with self.assertRaisesRegex(Exception, exception_message):
            logic.profile_crawler.ProfileSearcher(ini_path=path, profile_dir=profile_folder)

    @data(
        ('/profiles/profiles.ini', '/profiles/', ['s6zuh3tz.default'], []),
        ('/profiles/profiles.ini', '/profiles/', ['s6zuh3TZ.default'], ['default']),
        ('/profiles/profiles.ini', '/profiles/', ['s6zuh3tz.default', 's6zuh3TZ.default'], ['default']),
        ('/profiles/profiles.ini', '/profiles/', [], []),
        ('/profiles/profiles.ini', '/profiles/', ['s6zuh3tz.default', '2h2h4h.mr_x', '12k4k8.doctor_who'],
         ['mr_x', 'doctor_who'])
    )
    @unpack
    def test_compare_profiles(self, path, profile_folder, profiles_to_create, list_of_recoverables):
        """
        Test that the list of recoverable profiles is computed correctly
        :param path: The path for the profiles.ini file
        :param profile_folder: The profile direcotry in Firefox
        :param profiles_to_create: List of fake profiles to create
        :param list_of_recoverables: Expected set of recoverable profiles
        :return:
        """
        if path is not None:
            path = '%s%s' % (CrawlerTestCase.basedir, path)
        if profile_folder is not None:
            profile_folder = '%s%s' % (CrawlerTestCase.basedir, profile_folder)

        for profile in profiles_to_create:
            create_fake_profile(profile)

        crawler = logic.profile_crawler.ProfileSearcher(ini_path=path, profile_dir=profile_folder)
        crawler.compute_recoverable()
        self.assertEqual(sorted(list_of_recoverables), sorted([current_profile.name for current_profile in crawler.recoverable_profiles]))


    @data(
        ('/profiles/profiles.ini', '/profiles/', ["""
[Profile0]
Name=default
IsRelative=1
Path=s6zuh3tz.default
Default=1
"""]),
    )
    @unpack
    def test_load_from_fs(self, path, profile_folder, stringified_profile):
        """
        Test that the list of recoverable profiles is computed correctly
        :param path: The path for the profiles.ini file
        :param profile_folder: The profile direcotry in Firefox
        :return:
        """
        if path is not None:
            path = '%s%s' % (CrawlerTestCase.basedir, path)
        if profile_folder is not None:
            profile_folder = '%s%s' % (CrawlerTestCase.basedir, profile_folder)

        crawler = logic.profile_crawler.ProfileSearcher(ini_path=path, profile_dir=profile_folder)
        crawler.compute_recoverable()
        print(crawler.present_in_profile_file)
        self.assertEqual(stringified_profile, [current_profile.stringify() for current_profile in crawler.present_in_profile_file.values()])

    @data(
        ('/profiles/profiles.ini', '/profiles/', 1),
    )
    @unpack
    def test_load_from_ini_file(self, path, profile_folder, numer_of_profiles):
        """
        Test that the list of profiles in the ini loads correctly
        :param path: The path for the profiles.ini file
        :param profile_folder: The profile directory in Firefox
        :param numer_of_profiles: the expected number of profiles
        :return:
        """
        if path is not None:
            path = '%s%s' % (CrawlerTestCase.basedir, path)
        if profile_folder is not None:
            profile_folder = '%s%s' % (CrawlerTestCase.basedir, profile_folder)

        crawler = logic.profile_crawler.ProfileSearcher(ini_path=path, profile_dir=profile_folder)
        crawler.compute_recoverable()
        print(crawler.present_in_profile_file)
        self.assertEqual(numer_of_profiles, len(crawler.present_in_profile_file.values()))
