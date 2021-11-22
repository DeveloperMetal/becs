from unittest import TestCase
from becs.tag import TagMixin

class Test(TagMixin):
    pass

class TagTests(TestCase):
    def test_getter(self):
        t = Test()

        self.assertIsNone(t.tag)

        t.tag = "mytag"

        self.assertEqual(t.tag, "mytag")

        t.tag = None

        self.assertIsNone(t.tag)
