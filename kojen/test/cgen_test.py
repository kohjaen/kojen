import unittest
import os
import shutil

from kojen.LanguagePython import LanguagePython
from kojen.cgen import CBASEGenerator, reset_alphabet, get_next_alphabet

class TestFeatures(unittest.TestCase):

    workingfolder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "test")

    @classmethod
    def setUpClass(cls):
        os.makedirs(cls.workingfolder, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.workingfolder)

    @classmethod
    def create_template_file(cls, list_of_lines):
        assert os.path.isdir(cls.workingfolder)
        with open(os.path.join(cls.workingfolder, "file.t"), 'w') as f:
            for l in list_of_lines:
                f.write("%s\n" % l)

    @classmethod
    def get_test_gen(cls):
        TestFeatures.create_template_file(["Dummy"])
        return CBASEGenerator(TestFeatures.workingfolder, TestFeatures.workingfolder, LanguagePython())

    def test_has_TAG(self):
        test = TestFeatures.get_test_gen()
        a = "XXX::blabla<<<something::1>>>"
        b = "XXX::blabla<<something>>"
        self.assertTrue(test.hasTag(a), "Failed to pick up tag")
        self.assertFalse(test.hasTag(b), "Failed to ignore tag")

    def test_has_specific_TAG(self):
        test = TestFeatures.get_test_gen()
        a = "XXX::blabla<<<something::1>>>"
        b = "XXX::blabla<<something>>"
        self.assertTrue(test.hasSpecificTag(a, "<<<something>>>"), "Failed to pick up specific tag")
        self.assertFalse(test.hasSpecificTag(b, "<<<something>>>"), "Failed to ignore specific tag")
        self.assertFalse(test.hasSpecificTag(a, "<<<nothing>>>"), "Failed to ignore specific tag")
        self.assertFalse(test.hasSpecificTag(b, "<<<nothing>>>"), "Failed to ignore specific tag")


    def test_TAG_has_default(self):
        test = TestFeatures.get_test_gen()
        a = "XXX::blabla<<<something::1>>>"
        b = "XXX::blabla<<<something>>>"
        self.assertTrue(test.hasDefault(a), "Failed to pick up default")
        self.assertFalse(test.hasDefault(b), "Failed to pick up default")

    def test_extract_default_and_TAG(self):
        test = TestFeatures.get_test_gen()
        a = "XXX::blabla<<<something::1>>>"
        b = "XXX::blabla<<<something>>>"
        c = "XXX::blabla<<something>>"
        res_a = test.extractDefaultAndTag(a)
        res_b = test.extractDefaultAndTag(b)
        res_c = test.extractDefaultAndTag(c)
        self.assertEqual(res_a[0],"<<<something::1>>>", "Wrong tag")
        self.assertEqual(res_a[1],"1", "Wrong default")
        self.assertEqual(res_b[0], "<<<something>>>", "Wrong tag")
        self.assertEqual(res_b[1], "", "Wrong default")
        self.assertEqual(res_c[0], "", "Wrong tag")
        self.assertEqual(res_c[1], "", "Wrong default")

    def test_remove_default(self):
        test = TestFeatures.get_test_gen()
        a = "XXX::blabla<<<something::1>>>"
        b = "XXX::blabla<<<something>>>"
        res_a = test.removeDefault(a)
        res_b = test.removeDefault(b)
        self.assertEqual(res_a,res_b, "Failed to remove default")
        self.assertEqual(res_b,res_b, "Failed to remove default")

    def test_alpha(self):
        for i in range(100):
            s = reset_alphabet()
            for j in range(26*2-1):
                s+=get_next_alphabet()
            self.assertEqual(s,"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

    ''' TODO : Testing
        - template extending and excluding.
        - user tags
          - only finds defaults after <<<
    '''

if __name__ == '__main__':
    unittest.main()