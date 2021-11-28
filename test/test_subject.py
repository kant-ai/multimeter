import unittest

from multimeter.subject import Subject


class TestSubject(unittest.TestCase):

    def test_same_key_same_hash(self):
        s1 = Subject('my_subject')
        s2 = Subject('my_subject')
        self.assertEqual(hash(s1), hash(s2))

    def test_other_key_other_hash(self):
        s1 = Subject('my_subject')
        s2 = Subject('other_subject')
        self.assertNotEqual(hash(s1), hash(s2))

    def test_same_key_equals(self):
        s1 = Subject('my_subject')
        s2 = Subject('my_subject')
        self.assertEqual(s1, s2)

    def test_other_key_not_equals(self):
        s1 = Subject('my_subject')
        s2 = Subject('other_subject')
        self.assertNotEqual(s1, s2)


if __name__ == '__main__':
    unittest.main()
