import unittest
import shutil
import os
from kojen.LanguagePython import LanguagePython
from kojen.LanguageCPP import LanguageCPP
from kojen.LanguageCsharp import LanguageCsharp
from kojen.smgen import CStateMachineGenerator
from kojen.kojentypes import Interface, Struct

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
    def do_magic(cls, input, interface, tt = [], language=LanguagePython()):
        TestFeatures.create_template_file(input)
        smgenerator = CStateMachineGenerator(cls.workingfolder, cls.workingfolder, interface, language, "", "", "")
        smgenerator.Generate(tt, "", "", "", False)
        return TestFeatures.read_lines_of_output_file()

    def test_event_custom_params_nosignature(self):
        input = []
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("<<<EVENTSIGNATURE::p1, p2, p3,>>>")
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
        input.append("<<<EVENTSIGNATURE::p1, p2, p3,>>>")
        input.append("<<<EVENTSIGNATUREWITHDEFAULTS::p1, p2, p3,>>>")
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
        input.append("<<<EVENTSIGNATURE>>>")
        input.append("<<<EVENTSIGNATUREWITHDEFAULTS>>>")
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
        input.append("(some, <<<EVENTSIGNATURE>>>)")
        input.append("(some, <<<EVENTSIGNATUREWITHDEFAULTS>>>)")
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
        input.append("(<<<EVENTSIGNATURE>>> , other)")
        input.append("(<<<EVENTSIGNATUREWITHDEFAULTS>>> , other)")
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
        input.append("(some, <<<EVENTSIGNATURE>>>)")
        input.append("(some, <<<EVENTSIGNATUREWITHDEFAULTS>>>)")
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
        input.append("(<<<EVENTSIGNATURE>>>, yo)")
        input.append("(<<<EVENTSIGNATUREWITHDEFAULTS>>>, yo)")
        input.append("<<<PER_EVENT_END>>>")
        s = Struct("s")
        s.AddType("binga","bungaBunga", "0x66")
        i = Interface('')
        i.AddStruct(s)

        output = TestFeatures.do_magic(input, i)

        self.assertEqual(len(output), 2)
        self.assertEqual(output[0], "(binga, yo)\n") # Python
        self.assertEqual(output[1], "(binga=0x66, yo)\n")

    def test_event_members_declare(self):
        input = []
        input.append("<<<PER_EVENT_BEGIN>>>")
        input.append("<<<EVENTMEMBERSDECLARE>>>")
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
        input.append("<<<EVENTMEMBERSLITEINSTANTIATE::hello>>>")
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
        input.append("<<<EVENTMEMBERSLITEINSTANTIATE>>>")
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
        input.append("<<<GUARDNAME::No Guard>>>")
        #input.append("<<<EVENTNAME::No Event>>>") Hmmm ... need to think more on this.
        input.append("<<<EVENTNAME>>>")
        input.append("<<<STATENAMEIFNEXTSTATE::No Next State>>>")
        input.append("<<<ACTIONNAME::No Action>>>")
        input.append("<<<NEXTSTATENAME::No Next State>>>")
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
        input.append("<<<GUARDNAME::No Guard>>>")
        input.append("<<<EVENTNAME::No Event>>>")
        input.append("<<<STATENAMEIFNEXTSTATE::No Next State>>>")
        input.append("<<<ACTIONNAME::No Action>>>")
        input.append("<<<NEXTSTATENAME::No Next State>>>")
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