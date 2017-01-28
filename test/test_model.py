import unittest
import model.models


class ModelTestCase(unittest.TestCase):
    def setUp(self):
       self.profile = model.models.Profile()

    def test_default_constructor(self):
        self.assertEqual(-1, self.profile.id, 'mismatched id')
        self.assertEqual(False, self.profile.isDefault, 'The profile is set to be default')
        self.assertEqual(False, self.profile.isRelative, 'The profile is set to be relative')
        self.assertEqual(None, self.profile.name, 'Name is not None')
        self.assertEqual(None, self.profile.path, 'Path is not None')

    def test_profile_stringify(self):
        stringify = self.profile.stringify()
        self.assertMultiLineEqual("""
[Profile-1]
Name=None
IsRelative=0
Path=None
Default=0
""", stringify, "Stringigy did not work")

    def test_profile_stringify_override_id(self):
        stringify = self.profile.stringify(override_id=4)
        self.assertMultiLineEqual(
"""
[Profile4]
Name=None
IsRelative=0
Path=None
Default=0
""", stringify, "Stringigy did not work")

    def test_profile_stringify_loaded(self):
        self.profile.load(name='pippo', isRelative=True, path='asdasdasd.mine', isDefault=True)
        stringify = self.profile.stringify(3)
        self.assertMultiLineEqual(
"""
[Profile3]
Name=pippo
IsRelative=1
Path=asdasdasd.mine
Default=1
""", stringify, "Stringigy did not work")