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
    
    def test_setFilenameReplace(self):
        items = {}
        setFilenameReplace(items, "thisIsIt")
        self.assertEqual(len(items), 4, "Wrong length")
        k = [key for key in items]
        self.assertEqual(k[0],"TEMPLATE", "Wrong tag")
        self.assertEqual(k[1],"template", "Wrong tag")
        self.assertEqual(k[2],"tem_plate", "Wrong tag")
        self.assertEqual(k[3],"temPlate", "Wrong tag")
        self.assertEqual(items["TEMPLATE"], "thisIsIt", "Wrong tag")
        self.assertEqual(items["template"], "thisisit", "Wrong tag")
        self.assertEqual(items["tem_plate"], "this_is_it", "Wrong tag")
        self.assertEqual(items["temPlate"], "thisIsIt", "Wrong tag")

    def test_has_TAG(self):
        a = "XXX::blabla<<<something=1>>>"
        b = "XXX::blabla<<something>>"
        self.assertTrue(hasTag(a), "Failed to pick up tag")
        self.assertFalse(hasTag(b), "Failed to ignore tag")

    def test_has_specific_TAG(self):
        a = "XXX::blabla<<<something=1>>>"
        b = "XXX::blabla<<something>>"
        self.assertTrue(hasSpecificTag(a, "<<<something>>>"), "Failed to pick up specific tag")
        self.assertFalse(hasSpecificTag(b, "<<<something>>>"), "Failed to ignore specific tag")
        self.assertFalse(hasSpecificTag(a, "<<<nothing>>>"), "Failed to ignore specific tag")
        self.assertFalse(hasSpecificTag(b, "<<<nothing>>>"), "Failed to ignore specific tag")
        c = "<<<EXCLUDE=abcdefghijklmnopqrstuvwxyz>>>"
        self.assertTrue(hasSpecificTag(c, "<<<EXCLUDE>>>"), "Failed to pick up specific tag")


    def test_TAG_has_default(self):
        a = "XXX::blabla<<<something=1>>>"
        b = "XXX::blabla<<<something>>>"
        self.assertTrue(hasDefault(a), "Failed to pick up default")
        self.assertFalse(hasDefault(b), "Failed to pick up default")

    def test_extract_default_and_TAG(self):
        a = "XXX::blabla<<<something=1>>>"
        b = "XXX::blabla<<<something>>>"
        c = "XXX::blabla<<something>>"
        d = "XXX::blabla<<<something=this=and=this>>>"
        e = "XXX::blabla<<<<something=sSs>>>>"
        f = "<<<EXCLUDE=#if <<<SSS>>>_A_B,#e>>>"
        res_a = extractDefaultAndTag(a)
        res_b = extractDefaultAndTag(b)
        res_c = extractDefaultAndTag(c)
        res_d = extractDefaultAndTag(d)
        res_e = extractDefaultAndTag(e)
        res_f = extractDefaultAndTag(f)
        self.assertEqual(res_a[0],"<<<something=1>>>", "Wrong tag")
        self.assertEqual(res_a[1],"1", "Wrong default")
        self.assertEqual(res_b[0], "<<<something>>>", "Wrong tag")
        self.assertEqual(res_b[1], "", "Wrong default")
        self.assertEqual(res_c[0], "", "Wrong tag")
        self.assertEqual(res_c[1], "", "Wrong default")
        self.assertEqual(res_d[0], "<<<something=this=and=this>>>", "Wrong tag")
        self.assertEqual(res_d[1], "this=and=this", "Wrong default")
        self.assertEqual(res_e[0], "<<<something=sSs>>>", "Wrong tag")
        self.assertEqual(res_e[1], "sSs", "Wrong default")
        self.assertEqual(res_f[0], "<<<EXCLUDE=#if <<<SSS>>>_A_B,#e>>>", "Wrong tag")
        self.assertEqual(res_f[1], "#if <<<SSS>>>_A_B,#e", "Wrong default")

    def test_extract_default_and_TAG_multiple(self):
        a = "XXX::blabla<<<something=1>>> !@#!@$ <<<else=2>>>"
        res_a = extractDefaultAndTagNamed(a, "something")
        res_b = extractDefaultAndTagNamed(a, "else")
        self.assertEqual(res_a[0], "<<<something=1>>>", "Wrong tag")
        self.assertEqual(res_a[1], "1", "Wrong default")
        self.assertEqual(res_b[0], "<<<else=2>>>", "Wrong tag")
        self.assertEqual(res_b[1], "2", "Wrong default")

    def test_extract_TAG_and_A_and_B(self):
        a = "blab @#$KLF!WEFJ <<<some=thing=here>>>"
        b = "blab @#$KLF!WEFJ <<<some=thing>>>"
        res_a = extractTagAndAandB(a)
        self.assertEqual(len(res_a), 3, "Wrong length")
        self.assertEqual(res_a[0], "<<<some=thing=here>>>", "Wrong tag")
        self.assertEqual(res_a[1], "thing", "Wrong A")
        self.assertEqual(res_a[2], "here", "Wrong B")
        res_b = extractTagAndAandB(b)
        self.assertEqual(len(res_b), 3, "Wrong length")
        self.assertEqual(res_b[0], "<<<some=thing>>>", "Wrong tag")
        self.assertEqual(res_b[1], "thing", "Wrong A")
        self.assertEqual(res_b[2], None, "Wrong B")

    def test_extract_TAG_and_A_and_B_multiple(self):
        a = "blab @#$KLF!WEFJ <<<some=thing>>> 123498123481234 <<<some=thing>>>"
        res_a = extractTagAndAandB(a)
        self.assertEqual(len(res_a), 3, "Wrong length")
        self.assertEqual(res_a[0], "<<<some=thing>>>", "Wrong tag")
        self.assertEqual(res_a[1], "thing", "Wrong A")
        self.assertEqual(res_a[2], None, "Wrong B")

    def test_remove_default(self):
        a = "XXX::blabla<<<something=1>>>"
        b = "XXX::blabla<<<something>>>"
        res_a = removeDefault(a)
        res_b = removeDefault(b)
        self.assertEqual(res_a,res_b, "Failed to remove default")
        self.assertEqual(res_b,res_b, "Failed to remove default")

    def test_alpha(self):
        for i in range(100):
            a = reset_alphabet()
            s = alphabet_to_string(a)
            for j in range(26*2-1):
                a = get_next_alphabet(a)
                s+=alphabet_to_string(a)
            self.assertEqual(s,"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

    def test_even_space(self):
        a = "someWord"
        len_a = len(a)
        b = even_space(a, int(len_a/2))
        self.assertEqual(b, "someWord")
        b = even_space(a, len_a)
        self.assertEqual(b, "someWord")
        b = even_space(a, len_a * 2)
        self.assertEqual(b, "someWord        ")


    def test_camel_case(self):
        a = camel_case("bla")
        self.assertEqual(a, "Bla")
        a = camel_case("Bla")
        self.assertEqual(a, "Bla")
        a = camel_case("BlaBla")
        self.assertEqual(a, "Blabla")
        a = camel_case("blaBla")
        self.assertEqual(a, "Blabla")

    def test_camel_case_small(self):
        a = camel_case_small("bla")
        self.assertEqual(a, "bla")
        a = camel_case_small("Bla")
        self.assertEqual(a, "bla")
        a = camel_case_small("BlaBla")
        self.assertEqual(a, "blaBla")
        a = camel_case_small("blaBla")
        self.assertEqual(a, "blaBla")

    def test_snake_case(self):
        all1 = []
        all1.append('Bar')
        all1.append('-Bar')
        all1.append('_bar')
        all1.append('--.bar')
        all1.append('-BAR')
        all1.append('BAR')
        all1.append(' bar')
        for a in all1:
            self.assertEqual("bar", snake_case(a), f"Function 'snake_case' failed (1) -> {a}")

        all2 = []
        all2.append('FooBar')
        all2.append('Foo-Bar')
        all2.append('foo_bar')
        all2.append('--foo.bar')
        all2.append('Foo-BAR')
        #all2.append('fooBAR')
        all2.append('foo bar')
        for a in all2:
            self.assertEqual("foo_bar", snake_case(a), f"Function 'snake_case' failed (2) -> {a}")

        all3 = []
        all3.append('FooBarFoo')
        all3.append('Foo-Bar-Foo')
        all3.append('foo_bar_foo')
        all3.append('--foo.bar.foo-')
        all3.append('Foo-BAR_Foo')
        #all3.append('fooBARfoo')
        all3.append('foo bar foo')
        for a in all3:
            self.assertEqual("foo_bar_foo", snake_case(a), f"Function 'snake_case' failed (3) -> {a}")

        all4 = []
        all4.append('FooBarFooBar')
        all4.append('Foo-Bar-Foo-Bar')
        all4.append('foo_bar_foo_bar')
        all4.append('--foo.bar--foo.bar')
        all4.append('Foo-BAR.Foo-BAR')
        #all4.append('fooBARfooBAR')
        all4.append('foo bar foo bar')
        for a in all4:
            self.assertEqual("foo_bar_foo_bar", snake_case(a), f"Function 'snake_case' failed (4) -> {a}.")


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
        all_lines.append("<<<BEGIN=42>>>")
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
        all_lines.append("<<<FOR_BEGIN=fee, fie, foe>>>")
        all_lines.append("<<<FIRST>>>")
        all_lines.append("__<<<EACH>>>__")
        all_lines.append("A_<<<EACH>>> = <<<ALPH>>>")
        all_lines.append("A_<<<EACH>>> = <<<NUM>>>")
        all_lines.append("<<<LAST>>>")
        all_lines.append("<<<FOR_END>>>")
        all_lines.append("Last")
        runTest(self, all_lines)
        # additional variants for the same output
        all_lines[1] = "<<<FOR_BEGIN=   fee, fie, foe >>>"
        runTest(self, all_lines)
        all_lines[1] = "<<<FOR_BEGIN= ,  fee, fie, foe ,>>>"
        runTest(self, all_lines)
        all_lines[1] = "<<<FOR_BEGIN=   fee, fie, foe ,>>>"
        runTest(self, all_lines)
        all_lines[1] = "<<<FOR_BEGIN=  , fee, fie, foe     >>>"
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
        all_lines.append("<<<FOR_BEGIN=3>>>")
        all_lines.append("__<<<EACH>>>__")
        all_lines.append("A_<<<EACH>>> = <<<ALPH>>>")
        all_lines.append("A_<<<EACH>>> = <<<NUM>>>")
        all_lines.append("<<<FOR_END>>>")
        all_lines.append("Last")
        runTest(self, all_lines)

    def test_replaceUserTags(self):
        user_tags = {"A" :"1", "B":"2", "C":"3"}

        all_lines = []
        all_lines.append("<<<H=0>>>")
        all_lines.append("<<<A>>>")
        all_lines.append("<<<A>>><<<B>>>")
        all_lines.append("<<<A>>><<<B>>><<<C>>>")
        all_lines.append("<<<H>>> = <<<H>>>")
        all_lines.append("<<<G>>>")
        all_lines.append("Done")

        transformed = []
        for l in all_lines:
            transformed.append(replaceUserTags(l, user_tags))
        
        self.assertEqual(transformed[0], "0")
        self.assertEqual(transformed[1], "1")
        self.assertEqual(transformed[2], "12")
        self.assertEqual(transformed[3], "123")
        self.assertEqual(transformed[4], "<<<H>>> = <<<H>>>")
        self.assertEqual(transformed[5], "<<<G>>>")
        self.assertEqual(transformed[6], "Done")


    ''' TODO : Testing
        - template extending and excluding.
        - user tags
          - only finds defaults after <<<
    '''

if __name__ == '__main__':
    unittest.main()