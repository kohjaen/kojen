import unittest

from kojen.LanguagePython import LanguagePython
from kojen.cgen import *

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
        return CGenerator(TestFeatures.workingfolder, TestFeatures.workingfolder, LanguagePython())

    def test_has_TAG(self):
        a = "XXX::blabla<<<something::1>>>"
        b = "XXX::blabla<<something>>"
        self.assertTrue(hasTag(a), "Failed to pick up tag")
        self.assertFalse(hasTag(b), "Failed to ignore tag")

    def test_has_specific_TAG(self):
        a = "XXX::blabla<<<something::1>>>"
        b = "XXX::blabla<<something>>"
        self.assertTrue(hasSpecificTag(a, "<<<something>>>"), "Failed to pick up specific tag")
        self.assertFalse(hasSpecificTag(b, "<<<something>>>"), "Failed to ignore specific tag")
        self.assertFalse(hasSpecificTag(a, "<<<nothing>>>"), "Failed to ignore specific tag")
        self.assertFalse(hasSpecificTag(b, "<<<nothing>>>"), "Failed to ignore specific tag")


    def test_TAG_has_default(self):
        a = "XXX::blabla<<<something::1>>>"
        b = "XXX::blabla<<<something>>>"
        self.assertTrue(hasDefault(a), "Failed to pick up default")
        self.assertFalse(hasDefault(b), "Failed to pick up default")

    def test_extract_default_and_TAG(self):
        a = "XXX::blabla<<<something::1>>>"
        b = "XXX::blabla<<<something>>>"
        c = "XXX::blabla<<something>>"
        res_a = extractDefaultAndTag(a)
        res_b = extractDefaultAndTag(b)
        res_c = extractDefaultAndTag(c)
        self.assertEqual(res_a[0],"<<<something::1>>>", "Wrong tag")
        self.assertEqual(res_a[1],"1", "Wrong default")
        self.assertEqual(res_b[0], "<<<something>>>", "Wrong tag")
        self.assertEqual(res_b[1], "", "Wrong default")
        self.assertEqual(res_c[0], "", "Wrong tag")
        self.assertEqual(res_c[1], "", "Wrong default")

    def test_remove_default(self):
        a = "XXX::blabla<<<something::1>>>"
        b = "XXX::blabla<<<something>>>"
        res_a = removeDefault(a)
        res_b = removeDefault(b)
        self.assertEqual(res_a,res_b, "Failed to remove default")
        self.assertEqual(res_b,res_b, "Failed to remove default")

    def test_alpha(self):
        for i in range(100):
            s = reset_alphabet()
            for j in range(26*2-1):
                s+=get_next_alphabet()
            self.assertEqual(s,"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")


    def test_getWhitespace(self):
        a = "  <<<"
        b = "           <<<"
        res_a = getWhitespace(a)
        res_b = getWhitespace(b)
        self.assertEqual(res_a, "  ", "Failed to extract whitespace")
        self.assertEqual(res_b, "           ", "Failed to extract whitespace")


    def test_SingleExpander(self):
        all_lines = []
        all_lines.append("First")
        all_lines.append("      <<<MAGIC>>>")
        all_lines.append("Last")

        def basicExpansionFunction(output, whitespace):
            output.append(whitespace + "|||")
            output.append(whitespace + "---")
            output.append(whitespace + "***")

        se = SingleExpander("<<<MAGIC>>>")
        all_lines = se.Expand(all_lines, basicExpansionFunction)

        self.assertEqual(len(all_lines), 5, "unexpected input")
        self.assertEqual(all_lines[0], "First", "Unexpected output (1)")
        self.assertEqual(all_lines[1], "      |||", "Unexpected output (2)")
        self.assertEqual(all_lines[2], "      ---", "Unexpected output (3)")
        self.assertEqual(all_lines[3], "      ***", "Unexpected output (4)")
        self.assertEqual(all_lines[4], "Last", "Unexpected output (5)")

    def test_PairExpanderBasic(self):
        all_lines = []
        all_lines.append("First")
        all_lines.append("<<<BEGIN>>>")
        all_lines.append("---")
        all_lines.append(">>>")
        all_lines.append("<<<END>>>")
        all_lines.append("Last")

        def basicExpansionFunction(snippets, output):
            for s in snippets:
                output.append(s + "|||")
                output.append(s + "<<<")

        pe = PairExpander("<<<BEGIN>>>", "<<<END>>>")
        all_lines = pe.Expand(all_lines, basicExpansionFunction)

        self.assertEqual(len(all_lines), 6, "unexpected input")
        self.assertEqual(all_lines[0], "First", "Unexpected output (1)")
        self.assertEqual(all_lines[1], "---|||", "Unexpected output (2)")
        self.assertEqual(all_lines[2], "---<<<", "Unexpected output (3)")
        self.assertEqual(all_lines[3], ">>>|||", "Unexpected output (4)")
        self.assertEqual(all_lines[4], ">>><<<", "Unexpected output (5)")
        self.assertEqual(all_lines[5], "Last", "Unexpected output (6)")

    def test_PairExpanderExtraParam(self):
        all_lines = []
        all_lines.append("First")
        all_lines.append("<<<BEGIN::42>>>")
        all_lines.append("---")
        all_lines.append(">>>")
        all_lines.append("<<<END>>>")
        all_lines.append("Last")

        def extraParamExpansionFunction(snippets, output, extraParam):
            output.append("in : " + extraParam)
            for s in snippets:
                output.append(s + "|||")
                output.append(s + "<<<")

        pe = PairExpander("<<<BEGIN>>>", "<<<END>>>")
        all_lines = pe.Expand(all_lines, extraParamExpansionFunction)

        self.assertEqual(len(all_lines), 7, "unexpected input")
        self.assertEqual(all_lines[0], "First", "Unexpected output (1)")
        self.assertEqual(all_lines[1], "in : 42", "Unexpected output (2)")
        self.assertEqual(all_lines[2], "---|||", "Unexpected output (3)")
        self.assertEqual(all_lines[3], "---<<<", "Unexpected output (4)")
        self.assertEqual(all_lines[4], ">>>|||", "Unexpected output (5)")
        self.assertEqual(all_lines[5], ">>><<<", "Unexpected output (6)")
        self.assertEqual(all_lines[6], "Last", "Unexpected output (7)")

    def test_ForLoopExpanderCSV(self):

        def runTest(self, all_lines):
            test = TestFeatures.get_test_gen()
            output = PairExpander("<<<FOR_BEGIN>>>", "<<<FOR_END>>>").Expand(all_lines, test.innerexpand_for_loop)

            self.assertEqual(len(output), 13, "unexpected input")
            self.assertEqual(output[0], "First", "Unexpected output (1)")
            self.assertEqual(output[1], "fee", "Unexpected output (2)")
            self.assertEqual(output[2], "__fee__", "Unexpected output (3)")
            self.assertEqual(output[3], "A_fee = a", "Unexpected output (4)")
            self.assertEqual(output[4], "A_fee = 0", "Unexpected output (5)")
            self.assertEqual(output[5], "__fie__", "Unexpected output (6)")
            self.assertEqual(output[6], "A_fie = b", "Unexpected output (7)")
            self.assertEqual(output[7], "A_fie = 1", "Unexpected output (8)")
            self.assertEqual(output[8], "__foe__", "Unexpected output (9)")
            self.assertEqual(output[9], "A_foe = c", "Unexpected output (10)")
            self.assertEqual(output[10], "A_foe = 2", "Unexpected output (11)")
            self.assertEqual(output[11], "foe", "Unexpected output (12)")
            self.assertEqual(output[12], "Last", "Unexpected output (13)")

        all_lines = []
        all_lines.append("First")
        all_lines.append("<<<FOR_BEGIN::fee, fie, foe>>>")
        all_lines.append("<<<FIRST>>>")
        all_lines.append("__<<<EACH>>>__")
        all_lines.append("A_<<<EACH>>> = <<<ALPH>>>")
        all_lines.append("A_<<<EACH>>> = <<<NUM>>>")
        all_lines.append("<<<LAST>>>")
        all_lines.append("<<<FOR_END>>>")
        all_lines.append("Last")
        runTest(self, all_lines)
        # additional variants for the same output
        all_lines[1] = "<<<FOR_BEGIN::   fee, fie, foe >>>"
        runTest(self, all_lines)
        all_lines[1] = "<<<FOR_BEGIN:: ,  fee, fie, foe ,>>>"
        runTest(self, all_lines)
        all_lines[1] = "<<<FOR_BEGIN::   fee, fie, foe ,>>>"
        runTest(self, all_lines)
        all_lines[1] = "<<<FOR_BEGIN::  , fee, fie, foe     >>>"
        runTest(self, all_lines)

    def test_ForLoopExpanderNum(self):

        def runTest(self, all_lines):
            test = TestFeatures.get_test_gen()
            output = PairExpander("<<<FOR_BEGIN>>>", "<<<FOR_END>>>").Expand(all_lines, test.innerexpand_for_loop)

            self.assertEqual(len(output), 11, "unexpected input")
            self.assertEqual(output[0], "First", "Unexpected output (1)")
            self.assertEqual(output[1], "___0___", "Unexpected output (2)")
            self.assertEqual(output[2], "A__0_ = a", "Unexpected output (3)")
            self.assertEqual(output[3], "A__0_ = 0", "Unexpected output (4)")
            self.assertEqual(output[4], "___1___", "Unexpected output (5)")
            self.assertEqual(output[5], "A__1_ = b", "Unexpected output (6)")
            self.assertEqual(output[6], "A__1_ = 1", "Unexpected output (7)")
            self.assertEqual(output[7], "___2___", "Unexpected output (8)")
            self.assertEqual(output[8], "A__2_ = c", "Unexpected output (9)")
            self.assertEqual(output[9], "A__2_ = 2", "Unexpected output (10)")
            self.assertEqual(output[10], "Last", "Unexpected output (11)")

        all_lines = []
        all_lines.append("First")
        all_lines.append("<<<FOR_BEGIN::3>>>")
        all_lines.append("__<<<EACH>>>__")
        all_lines.append("A_<<<EACH>>> = <<<ALPH>>>")
        all_lines.append("A_<<<EACH>>> = <<<NUM>>>")
        all_lines.append("<<<FOR_END>>>")
        all_lines.append("Last")
        runTest(self, all_lines)


    ''' TODO : Testing
        - template extending and excluding.
        - user tags
          - only finds defaults after <<<
    '''

if __name__ == '__main__':
    unittest.main()