import unittest
import shutil
import os
from kojen.LanguagePython import LanguagePython
from kojen.LanguageCPP import LanguageCPP
from kojen.LanguageCsharp import LanguageCsharp
from kojen.smgen import CStateMachineGenerator
from kojen.kojentypes import Interface, Struct, Message, MessageHeader

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
    def read_lines_of_output_file(cls):
        path = os.path.join(cls.workingfolder, "file.t")
        assert os.path.isfile(path)
        with open(path, 'r') as f:
            return f.readlines()

    @classmethod
    def do_magic(cls, input, interface, tt = [], language=LanguagePython(), namespace_name = "", fsm_name = ""):
        TestFeatures.create_template_file(input)
        smgenerator = CStateMachineGenerator(cls.workingfolder, cls.workingfolder, interface, language, "", "", "")
        smgenerator.Generate(tt, namespace_name, fsm_name, "", False)
        return TestFeatures.read_lines_of_output_file()

    def test_event_custom_params_nosignature(self):
        input = []
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("<<<EVENTSIGNATURE=p1, p2, p3,>>>")
        input.append("<<<PER_EVENT_END>>>")
        s = Struct("somestruct")
        i = Interface('')
        i.AddStruct(s)

        output = TestFeatures.do_magic(input, i)

        self.assertEqual(len(output), 1)
        self.assertEqual(output[0]  , "p1, p2, p3\n")

    def test_event_custom_params_signature1(self):
        input = []
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("<<<EVENTSIGNATURE=p1, p2, p3,>>>")
        input.append("<<<EVENTSIGNATUREWITHDEFAULTS=p1, p2, p3,>>>")
        input.append("<<<PER_EVENT_END>>>")
        s = Struct("somestruct")
        s.AddType("binga","bungaBunga", 0x66)
        i = Interface('')
        i.AddStruct(s)

        output = TestFeatures.do_magic(input, i)

        self.assertEqual(len(output), 2)
        self.assertEqual(output[0], "binga, p1, p2, p3\n") # Python
        self.assertEqual(output[1], "binga, p1, p2, p3\n")

    def test_event_custom_params_signature2(self):
        input = []
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("<<<SIGNATURE>>>")
        input.append("<<<SIGNATUREWITHDEFAULTS>>>")
        input.append("<<<PER_EVENT_END>>>")
        s = Struct("somestruct")
        s.AddType("binga","bungaBunga", "0x66")
        i = Interface('')
        i.AddStruct(s)

        output = TestFeatures.do_magic(input, i)

        self.assertEqual(len(output), 2)
        self.assertEqual(output[0], "binga\n") # Python
        self.assertEqual(output[1], "binga=0x66\n")  # Python

    def test_event_custom_params_signature3(self):
        input = []
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("(some, <<<SIGNATURE>>>)")
        input.append("(some, <<<SIGNATUREWITHDEFAULTS>>>)")
        input.append("<<<PER_EVENT_END>>>")
        s = Struct("s")
        i = Interface('')
        i.AddStruct(s)

        output = TestFeatures.do_magic(input, i)

        self.assertEqual(len(output), 2)
        self.assertEqual(output[0], "(some)\n") # Python
        self.assertEqual(output[1], "(some)\n")

    def test_event_custom_params_signature4(self):
        input = []
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("(<<<SIGNATURE>>> , other)")
        input.append("(<<<SIGNATUREWITHDEFAULTS>>> , other)")
        input.append("<<<PER_EVENT_END>>>")
        s = Struct("s")
        i = Interface('')
        i.AddStruct(s)

        output = TestFeatures.do_magic(input, i)

        self.assertEqual(len(output), 2)
        self.assertEqual(output[0], "(other)\n") # Python
        self.assertEqual(output[1], "(other)\n")

    def test_event_custom_params_signature5(self):
        input = []
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("(some, <<<SIGNATURE>>>)")
        input.append("(some, <<<SIGNATUREWITHDEFAULTS>>>)")
        input.append("<<<PER_EVENT_END>>>")
        s = Struct("s")
        s.AddType("binga","bungaBunga", "0x66")
        i = Interface('')
        i.AddStruct(s)

        output = TestFeatures.do_magic(input, i)

        self.assertEqual(len(output), 2)
        self.assertEqual(output[0], "(some, binga)\n") # Python
        self.assertEqual(output[1], "(some, binga=0x66)\n")

    def test_event_custom_params_signature6(self):
        input = []
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("(<<<SIGNATURE>>>, yo)")
        input.append("(<<<SIGNATUREWITHDEFAULTS>>>, yo)")
        input.append("<<<PER_EVENT_END>>>")
        s = Struct("s")
        s.AddType("binga","bungaBunga", "0x66")
        i = Interface('')
        i.AddStruct(s)

        output = TestFeatures.do_magic(input, i)

        self.assertEqual(len(output), 2)
        self.assertEqual(output[0], "(binga, yo)\n") # Python
        self.assertEqual(output[1], "(binga=0x66, yo)\n")

    def createMsgInputWithDefaults(self):
        input = []
        input.append("<<<PER_MSG_BEGIN>>>")
        input.append("<<<SIGNATURE>>>")
        input.append("<<<SIGNATUREWITHDEFAULTS>>>")
        input.append("<<<PER_MSG_END>>>")
        return input
    
    def createIfNestedMsgWithDefalts(self, allDefaults = True):
        s = Struct("s")
        s.AddType("myApple", "apple", 1)
        s.AddType("myOrange", "orange", 2)
        s.AddType("myBanana", "banana", 3)
        s1 = Struct("FruitSalad")
        s1.AddStruct("myFruits", s)
        s1.AddType("myCustard", "custard", 4 if allDefaults else None)
        s2 = Struct("Breakfast")
        s2.AddStruct("myEdibles", s1)
        s2.AddType("myCoffee", "coffee", 5)
        s2.AddType("myOJ", "OJ", 6 if allDefaults else None)
        m = Message('ThisMorning', 0x02)
        m.AddStruct('myBreakfast', s2)
        m.AddType('myKnife', 'knife', 7)
        m.AddType('myFork', 'fork', 8 if allDefaults else None)
        m.AddType('myNapkin', 'napkin', 9 if allDefaults else None)
        i = Interface('')
        i.AddStruct(s)
        i.AddStruct(s1)
        i.AddStruct(s2)
        i.AddMessage(m)
        return i

    def test_event_params_signature_all_defaults(self):
        input = self.createMsgInputWithDefaults()
        i = self.createIfNestedMsgWithDefalts(True)
        r = {}
        r[LanguageCPP()] = [
            'Breakfast const& myBreakfast, knife myKnife, fork myFork, napkin myNapkin\n',
            'Breakfast const& myBreakfast={{{1,2,3},4},5,6}, knife myKnife=7, fork myFork=8, napkin myNapkin=9\n'
        ]
        #r[LanguagePython()] = None
        r[LanguageCsharp()] = [
            'Breakfast myBreakfast, knife myKnife, fork myFork, napkin myNapkin\n',
            'Breakfast myBreakfast={{{1,2,3},4},5,6}, knife myKnife=7, fork myFork=8, napkin myNapkin=9\n'
        ]

        for lan, res in r.items():
            output = TestFeatures.do_magic(input, i, [], lan)
            self.assertEqual(len(output), 2)
            self.assertEqual(output[0], res[0])
            self.assertEqual(output[1], res[1])

    def test_event_params_signature_some_defaults(self):
        input = self.createMsgInputWithDefaults()
        i = self.createIfNestedMsgWithDefalts(False)
        r = {}
        r[LanguageCPP()] = [
            'Breakfast const& myBreakfast, knife myKnife, fork myFork, napkin myNapkin\n',
            'Breakfast const& myBreakfast={{{1,2,3},{}},5,{}}, knife myKnife=7, fork myFork={}, napkin myNapkin={}\n'
        ]
        #r[LanguagePython()] = None
        r[LanguageCsharp()] = [
            'Breakfast myBreakfast, knife myKnife, fork myFork, napkin myNapkin\n',
            'Breakfast myBreakfast={{{1,2,3},{}},5,{}}, knife myKnife=7, fork myFork={}, napkin myNapkin={}\n'
        ]

        for lan, res in r.items():
            output = TestFeatures.do_magic(input, i, [], lan)
            self.assertEqual(len(output), 2)
            self.assertEqual(output[0], res[0])
            self.assertEqual(output[1], res[1])

    def test_event_members_declare(self):
        input = []
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("<<<MEMBERSDECLARE>>>")
        input.append("<<<PER_EVENT_END>>>")

        s = Struct("s")
        s.AddType("binga", "bungaBunga", "0x66")
        s.AddType("bonga", "bangaBanga")
        i = Interface('')
        i.AddStruct(s)

        output = TestFeatures.do_magic(input, i)#, [], LanguageCsharp())
        self.assertEqual(len(output), 2)
        self.assertEqual(output[0].strip(' '), "binga = 0x66 # bungaBunga\n")
        self.assertEqual(output[1].strip(' '), "bonga = None # bangaBanga\n")

    def test_event_members_instantiate_custom_name(self):
        input = []
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("<<<EVENTMEMBERSLITEINSTANTIATE=hello>>>")
        input.append("<<<PER_EVENT_END>>>")
        s = Struct("somestruct")
        s.AddType("binga", "bungaBunga")
        i = Interface('')
        i.AddStruct(s)

        output = TestFeatures.do_magic(input, i)

        self.assertEqual(len(output), 1)
        self.assertEqual(output[0], "hello.binga = binga\n")

    def test_event_members_instantiate_no_custom_name(self):
        input = []
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("<<<MEMBERSLITEINSTANTIATE>>>")
        input.append("<<<PER_EVENT_END>>>")
        s = Struct("somestruct")
        s.AddType("binga", "bungaBunga")
        i = Interface('')
        i.AddStruct(s)

        output = TestFeatures.do_magic(input, i)

        self.assertEqual(len(output), 1)
        self.assertEqual(output[0], "data.binga = binga\n")

    def test_transitionsperguard_tags(self):
        input = []
        input.append("<<<PER_STATETRANSITION_BEGIN>>>")
        input.append("<<<PER_EVENTTRANSITION_BEGIN>>>")
        input.append("<<<PER_GUARDTRANSITION_BEGIN>>>")
        input.append("<<<GUARDNAME=No Guard>>>")
        #input.append("<<<EVENTNAME=No Event>>>") Hmmm ... need to think more on this.
        input.append("<<<EVENTNAME>>>")
        input.append("<<<STATENAMEIFNEXTSTATE=No Next State>>>")
        input.append("<<<ACTIONNAME=No Action>>>")
        input.append("<<<NEXTSTATENAME=No Next State>>>")
        input.append("<<<PER_GUARDTRANSITION_END>>>")
        input.append("<<<PER_EVENTTRANSITION_END>>>")
        input.append("<<<PER_STATETRANSITION_END>>>")
        tt = [['S1', 'Do', 'S1', 'A1', 'G1']]
        s = Struct("somestruct")
        s.AddType("binga", "bungaBunga")
        i = Interface('')
        i.AddStruct(s)

        output = TestFeatures.do_magic(input, i, tt)

        self.assertEqual(len(output), 5)
        self.assertEqual(output[0], "G1\n")
        self.assertEqual(output[1], "Do\n")
        self.assertEqual(output[2], "S1\n")
        self.assertEqual(output[3], "A1\n")
        self.assertEqual(output[4], "S1\n")

    def test_transitionsperguard_tags_with_custom_defaults(self):
        input = []
        input.append("<<<PER_STATETRANSITION_BEGIN>>>")
        input.append("<<<PER_EVENTTRANSITION_BEGIN>>>")
        input.append("<<<PER_GUARDTRANSITION_BEGIN>>>")
        input.append("<<<GUARDNAME=No Guard>>>")
        input.append("<<<EVENTNAME=No Event>>>")
        input.append("<<<STATENAMEIFNEXTSTATE=No Next State>>>")
        input.append("<<<ACTIONNAME=No Action>>>")
        input.append("<<<NEXTSTATENAME=No Next State>>>")
        input.append("<<<PER_GUARDTRANSITION_END>>>")
        input.append("<<<PER_EVENTTRANSITION_END>>>")
        input.append("<<<PER_STATETRANSITION_END>>>")
        tt = [['S1', 'Do', 'None', 'None', 'None']]
        s = Struct("somestruct")
        s.AddType("binga", "bungaBunga")
        i = Interface('')
        i.AddStruct(s)

        output = TestFeatures.do_magic(input, i, tt)

        self.assertEqual(len(output), 5)
        self.assertEqual(output[0], "No Guard\n")
        self.assertEqual(output[1], "No Event\n")
        self.assertEqual(output[2], "No Next State\n")
        self.assertEqual(output[3], "No Action\n")
        self.assertEqual(output[4], "No Next State\n")

    def test_events(self):
        input = []
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("<<<EVENTNAME>>>")
        input.append("<<<PER_EVENT_END>>>")
        tt = [['S1', "how ya doin'", 'None', 'None', 'None']]
        s = Struct("hello")
        i = Interface('')
        i.AddStruct(s)

        output = TestFeatures.do_magic(input, i, tt)

        self.assertEqual(len(output), 2)
        self.assertEqual(output[1], "hello\n")
        self.assertEqual(output[0], "how ya doin'\n")

    def test_aggregate_initialization_events(self):
        input = []
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("<<<AGGREGATEINITIALIZATION>>>")
        input.append("<<<PER_EVENT_END>>>")
        s = Struct("somestruct")
        s.AddType("binga", "bool")
        s.AddType("bunga","size_t")
        s2 = Struct("somestruct2")
        s2.AddType("bla", "bool")
        s2.AddType("blabla", "size_t")
        i = Interface('')
        i.AddStruct(s)
        i.AddStruct(s2)

        output = TestFeatures.do_magic(input, i, [], LanguageCPP())

        self.assertEqual(len(output), 2)
        self.assertEqual(output[0], "{binga, bunga}\n")
        self.assertEqual(output[1], "{bla, blabla}\n")

    def test_pyattr(self):
        # param, no default
        input = []
        input.append("<<<PER_STRUCT_BEGIN>>>")
        input.append("<<<PyAttr=ninja>>>")
        input.append("<<<PER_STRUCT_END>>>")
        s = Struct("somestruct")
        s.AddType("binga", "bool")
        s.AddType("bunga", "size_t")
        s.ninja = "here"
        s2 = Struct("somestruct2")
        s2.AddType("bla", "bool")
        s2.AddType("blabla", "size_t")
        s2.ninja = 36
        i = Interface('')
        i.AddStruct(s)
        i.AddStruct(s2)
        output = TestFeatures.do_magic(input, i, [], LanguageCPP())
        self.assertEqual(len(output), 2)
        self.assertEqual(output[0], "here\n")
        self.assertEqual(output[1], "36\n")
        # multiple param, no default
        input = []
        input.append("<<<PER_STRUCT_BEGIN>>>")
        input.append("<<<PyAttr=ninja>>> is a big fat <<<PyAttr=ninja>>>")
        input.append("<<<PER_STRUCT_END>>>")
        output = TestFeatures.do_magic(input, i, [], LanguageCPP())
        self.assertEqual(len(output), 2)
        self.assertEqual(output[0], "here is a big fat here\n")
        self.assertEqual(output[1], "36 is a big fat 36\n")
        # no param
        input = []
        input.append("<<<PER_STRUCT_BEGIN>>>")
        input.append("<<<PyAttr=ninja>>>")
        input.append("<<<PER_STRUCT_END>>>")
        s = Struct("somestruct")
        s.AddType("binga", "bool")
        s.AddType("bunga", "size_t")
        s2 = Struct("somestruct2")
        s2.AddType("bla", "bool")
        s2.AddType("blabla", "size_t")
        i = Interface('')
        i.AddStruct(s)
        i.AddStruct(s2)
        output2 = TestFeatures.do_magic(input, i, [], LanguageCPP())
        self.assertEqual(len(output2), 0)
        # param, default
        input = []
        input.append("<<<PER_STRUCT_BEGIN>>>")
        input.append("<<<PyAttr=ninja=yoyo>>>")
        input.append("<<<PER_STRUCT_END>>>")
        s = Struct("somestruct")
        s.AddType("binga", "bool")
        s.AddType("bunga", "size_t")
        s2 = Struct("somestruct2")
        s2.AddType("bla", "bool")
        s2.AddType("blabla", "size_t")
        i = Interface('')
        i.AddStruct(s)
        i.AddStruct(s2)
        output3 = TestFeatures.do_magic(input, i, [], LanguageCPP())
        self.assertEqual(len(output3), 2)
        self.assertEqual(output3[0], "yoyo\n")
        self.assertEqual(output3[1], "yoyo\n")

    def test_Docs(self):
        input = []
        input.append("<<<PER_STRUCT_BEGIN>>>")
        input.append("  *  *  <<<DOCUMENTATION>>>")
        input.append("<<<PER_STRUCT_END>>>")
        s = Struct("somestruct")
        s.AddType("binga", "bool")
        s.AddType("bunga", "size_t")
        s.SetDocumentation("line1\nline2\nline3\n")
        s2 = Struct("somestruct2")
        s2.AddType("bla", "bool")
        s2.AddType("blabla", "size_t")
        s2.SetDocumentation("line4\nline5\nline6")
        i = Interface('')
        i.AddStruct(s)
        i.AddStruct(s2)
        # param, no default
        output = TestFeatures.do_magic(input, i, [], LanguageCPP())
        self.assertEqual(len(output), 6)
        self.assertEqual(output[0], "  *  *  line1\n")
        self.assertEqual(output[1], "  *  *  line2\n")
        self.assertEqual(output[2], "  *  *  line3\n")
        self.assertEqual(output[3], "  *  *  line4\n")
        self.assertEqual(output[4], "  *  *  line5\n")
        self.assertEqual(output[5], "  *  *  line6\n")

    def test_user_if_endif_no_valid_tags(self):
        input = []
        input.append("// 1")
        input.append("<<<IF feefiefoefum>>>")
        input.append("  <<<ThisIsValue>>>")
        input.append("<<<ENDIF>>>")
        input.append("// 2")
        input.append("// 3")
        input.append("<<<IF abracadabra>>>")
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("~~ <<<EVENT_NAME>>> ~~")
        input.append("<<<PER_EVENT_END>>>")
        input.append("<<<ENDIF>>>")
        input.append("// 4")
        
        i = Interface('')
        s = Struct("someStruct")
        s2 = Struct("someOtherStruct")
        i.AddStruct(s)
        i.AddStruct(s2)

        # param, no default
        output = TestFeatures.do_magic(input, i, [], LanguageCPP())
        self.assertEqual(len(output), 4)
        self.assertEqual(output[0], "// 1\n")
        self.assertEqual(output[1], "// 2\n")
        self.assertEqual(output[2], "// 3\n")
        self.assertEqual(output[3], "// 4\n")

    def test_user_if_endif_valid_tags(self):
        input = []
        input.append("// 1")
        input.append("<<<IF feefiefoefum>>>")
        input.append("  <<<ThisIsValue>>>")
        input.append("<<<ENDIF>>>")
        input.append("// 2")
        input.append("// 3")
        input.append("<<<IF abracadabra>>>")
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("~~ <<<EVENT_NAME>>> ~~")
        input.append("<<<PER_EVENT_END>>>")
        input.append("<<<ELSE>>>")
        input.append(" 0xBADFOOD")
        input.append("<<<ENDIF>>>")
        input.append("// 4")
        
        i = Interface('')
        i.AddUserTag("feefiefoefum", None) # None and "" are valid for if control blocks...but not replace.
        i.AddUserTag("abracadabra", None)
        s = Struct("someStruct")
        s2 = Struct("someOtherStruct")
        i.AddStruct(s)
        i.AddStruct(s2)

        # param, no default
        output = TestFeatures.do_magic(input, i, [], LanguageCPP())
        self.assertEqual(len(output), 7)
        self.assertEqual(output[0], "// 1\n")
        self.assertEqual(output[1], "  <<<ThisIsValue>>>\n")
        self.assertEqual(output[2], "// 2\n")
        self.assertEqual(output[3], "// 3\n")
        self.assertEqual(output[4], "~~ some_struct ~~\n")
        self.assertEqual(output[5], "~~ some_other_struct ~~\n")
        self.assertEqual(output[6], "// 4\n")

    def test_user_if_elif_endif_valid_tags(self):
        input = []
        input.append("// 1")
        input.append("<<<IF feefiefoefum>>>")
        input.append("  <<<ThisIsValue>>>")
        input.append("<<<ELSEIF abracadabra>>>")
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("~~ <<<EVENT_NAME>>> ~~")
        input.append("<<<PER_EVENT_END>>>")
        input.append("<<<ELSEIF bbbbbbbbbbb>>>")
        input.append(" >>>>>>   <<<<<<  ")
        input.append("<<<ELSE>>>")
        input.append(" 0xBADFOOD")
        input.append("<<<ENDIF>>>")
        input.append("// 4")
        
        i = Interface('')
        i.AddUserTag("abracadabra", None)
        s = Struct("someStruct")
        s2 = Struct("someOtherStruct")
        i.AddStruct(s)
        i.AddStruct(s2)

        # param, no default
        output = TestFeatures.do_magic(input, i, [], LanguageCPP())
        self.assertEqual(len(output), 4)
        self.assertEqual(output[0], "// 1\n")
        self.assertEqual(output[1], "~~ some_struct ~~\n")
        self.assertEqual(output[2], "~~ some_other_struct ~~\n")
        self.assertEqual(output[3], "// 4\n")

    def test_user_if_elif_endif_multiple_valid_tags1(self):
        input = []
        input.append("// 1")
        input.append("<<<IF feefiefoefum>>>")
        input.append("  <<<ThisIsValue>>>")
        input.append("<<<ELSEIF abracadabra>>>")
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("~~ <<<EVENT_NAME>>> ~~")
        input.append("<<<PER_EVENT_END>>>")
        input.append("<<<ELSEIF bbbbbbbbbbb>>>")
        input.append(" >>>>>>   <<<<<<  ")
        input.append("<<<ELSE>>>")
        input.append(" 0xBADFOOD")
        input.append("<<<ENDIF>>>")
        input.append("// 4")
        
        i = Interface('')
        i.AddUserTag("abracadabra", None)
        i.AddUserTag("feefiefoefum", None)
        s = Struct("someStruct")
        s2 = Struct("someOtherStruct")
        i.AddStruct(s)
        i.AddStruct(s2)

        # param, no default
        output = TestFeatures.do_magic(input, i, [], LanguageCPP())
        self.assertEqual(len(output), 5)
        self.assertEqual(output[0], "// 1\n")
        self.assertEqual(output[1], "  <<<ThisIsValue>>>\n")
        self.assertEqual(output[2], "~~ some_struct ~~\n")
        self.assertEqual(output[3], "~~ some_other_struct ~~\n")
        self.assertEqual(output[4], "// 4\n")

    def test_user_if_elif_endif_multiple_valid_tags2(self):
        input = []
        input.append("// 1")
        input.append("<<<IF feefiefoefum>>>")
        input.append("  <<<ThisIsValue>>>")
        input.append("<<<ELSEIF abracadabra>>>")
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("~~ <<<EVENT_NAME>>> ~~")
        input.append("<<<PER_EVENT_END>>>")
        input.append("<<<ELSEIF bbbbbbbbbbb>>>")
        input.append(" >>>>>>   <<<<<<  ")
        input.append("<<<ELSE>>>")
        input.append(" 0xBADFOOD")
        input.append("<<<ENDIF>>>")
        input.append("// 4")
        
        i = Interface('')
        i.AddUserTag("abracadabra", None)
        i.AddUserTag("bbbbbbbbbbb", None)
        s = Struct("someStruct")
        s2 = Struct("someOtherStruct")
        i.AddStruct(s)
        i.AddStruct(s2)

        # param, no default
        output = TestFeatures.do_magic(input, i, [], LanguageCPP())
        self.assertEqual(len(output), 5)
        self.assertEqual(output[0], "// 1\n")
        self.assertEqual(output[1], "~~ some_struct ~~\n")
        self.assertEqual(output[2], "~~ some_other_struct ~~\n")
        self.assertEqual(output[3], " >>>>>>   <<<<<<  \n")
        self.assertEqual(output[4], "// 4\n")

    def test_user_if_elif_else_endif_invalid_tags(self):
        input = []
        input.append("// 1")
        input.append("<<<IF feefiefoefum>>>")
        input.append("  <<<ThisIsValue>>>")
        input.append("<<<ELSEIF abracadabra>>>")
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("~~ <<<EVENT_NAME>>> ~~")
        input.append("<<<PER_EVENT_END>>>")
        input.append("<<<ELSEIF bbbbbbbbbbb>>>")
        input.append(" >>>>>>   <<<<<<  ")
        input.append("<<<ELSE>>>")
        input.append(" 0xBADFOOD")
        input.append("<<<ENDIF>>>")
        input.append("// 4")
        
        i = Interface('')
        s = Struct("someStruct")
        s2 = Struct("someOtherStruct")
        i.AddStruct(s)
        i.AddStruct(s2)

        # param, no default
        output = TestFeatures.do_magic(input, i, [], LanguageCPP())
        self.assertEqual(len(output), 3)
        self.assertEqual(output[0], "// 1\n")
        self.assertEqual(output[1], " 0xBADFOOD\n")
        self.assertEqual(output[2], "// 4\n")

    def test_if_else_endif_nested_usertags(self):
        
        input = []
        input.append("<<<IF OtherNamespace>>>")
        input.append("namespace <<<OtherNamespace>>> {")
        input.append("<<<ENDIF>>>")
        input.append("class <<<OtherClass>>>;")
        input.append("<<<IF OtherNamespace>>>")
        input.append("} // namespace <<<OtherNamespace>>>")
        input.append("<<<ENDIF>>>")
        input.append("///")
        input.append("<<<IF OtherNamespace>>>")
        input.append("extern template class <<<STATEMACHINENAME>>>StateMachine<<<<OtherNamespace>>>::<<<OtherClass>>>>;")
        input.append("<<<ELSE>>>")
        input.append("extern template class <<<STATEMACHINENAME>>>StateMachine<<<<OtherClass=<<<STATEMACHINENAME>>>Controller>>>>;")
        input.append("<<<ENDIF>>>")
        input.append("// 4")

        #### All user tags with values...
        i = Interface('')
        i.AddUserTag("OtherNamespace", "Banana")
        i.AddUserTag("OtherClass", "FruitSalad")

        output = TestFeatures.do_magic(input, i, [], LanguageCPP(), "", "Strawberry")
        self.assertEqual(len(output), 6)
        self.assertEqual(output[0], "namespace Banana {\n")
        self.assertEqual(output[1], "class FruitSalad;\n")
        self.assertEqual(output[2], "} // namespace Banana\n")
        self.assertEqual(output[3], "///\n")
        self.assertEqual(output[4], "extern template class StrawberryStateMachine<Banana::FruitSalad>;\n")
        self.assertEqual(output[5], "// 4\n")

        #### No user tags with values...
        i = Interface('')
        #i.AddUserTag("OtherNamespace", "Banana")
        #i.AddUserTag("OtherClass", "FruitSalad")

        output = TestFeatures.do_magic(input, i, [], LanguageCPP(), "", "Strawberry")
        self.assertEqual(len(output), 4)
        self.assertEqual(output[0], "class <<<OtherClass>>>;\n")
        self.assertEqual(output[1], "///\n")
        self.assertEqual(output[2], "extern template class StrawberryStateMachine<StrawberryController>;\n")
        self.assertEqual(output[3], "// 4\n")

        #### Empty strings are still valid tags! Allow replacing things with nothing.
        i = Interface('')
        i.AddUserTag("OtherNamespace", "")
        i.AddUserTag("OtherClass", "")

        output = TestFeatures.do_magic(input, i, [], LanguageCPP(), "", "Strawberry")
        self.assertEqual(len(output), 6)
        self.assertEqual(output[0], "namespace  {\n")
        self.assertEqual(output[1], "class ;\n")
        self.assertEqual(output[2], "} // namespace \n")
        self.assertEqual(output[3], "///\n")
        self.assertEqual(output[4], "extern template class StrawberryStateMachine<::>;\n")
        self.assertEqual(output[5], "// 4\n")

        #### NONE are still valid tags! Allow replacing things with nothing.
        i = Interface('')
        i.AddUserTag("OtherNamespace", None)
        i.AddUserTag("OtherClass", None)

        output = TestFeatures.do_magic(input, i, [], LanguageCPP(), "", "Strawberry")
        self.assertEqual(len(output), 6)
        self.assertEqual(output[0], "namespace  {\n")
        self.assertEqual(output[1], "class ;\n")
        self.assertEqual(output[2], "} // namespace \n")
        self.assertEqual(output[3], "///\n")
        self.assertEqual(output[4], "extern template class StrawberryStateMachine<::>;\n")
        self.assertEqual(output[5], "// 4\n")

        #### One user tags with values...
        i = Interface('')
        #i.AddUserTag("OtherNamespace", "Banana")
        i.AddUserTag("OtherClass", "FruitSalad")

        output = TestFeatures.do_magic(input, i, [], LanguageCPP(), "", "Strawberry")
        self.assertEqual(len(output), 4)
        self.assertEqual(output[0], "class FruitSalad;\n")
        self.assertEqual(output[1], "///\n")
        self.assertEqual(output[2], "extern template class StrawberryStateMachine<FruitSalad>;\n")
        self.assertEqual(output[3], "// 4\n")

    def test_duplicate_label_usertags(self):
        input = []
        input.append("[something(IsClean.<<<IsClean=Soap>>>)]")
        i = Interface('')
        i.AddUserTag("IsClean", "Toothpaste")

        output = TestFeatures.do_magic(input, i, [], LanguageCPP(), "", "Strawberry")
        self.assertEqual(len(output), 1)
        self.assertEqual(output[0], "[something(IsClean.Toothpaste)]\n")

        i = Interface('')
        output = TestFeatures.do_magic(input, i, [], LanguageCPP(), "", "Strawberry")
        self.assertEqual(len(output), 1)
        self.assertEqual(output[0], "[something(IsClean.Soap)]\n")


    '''
    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
    '''

if __name__ == '__main__':
    unittest.main()