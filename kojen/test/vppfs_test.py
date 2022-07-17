import unittest
import os
from kojen.vppfs import *

class TestDBFormat(unittest.TestCase):
    ''' Unit test. These guys might change the format of their DB.
        This hopes to make it easier to catch those changes and adapt to them quickly.
        This also is coded for the fixed number of diagrams in the model I do the dev with...if that changes, this code must change.
    '''
    def setUp(self):
        self.unit_test_model = os.path.join(os.path.abspath(os.path.dirname( __file__ )), "blob.xml")
        self.vppdiagrams = VPPDiagrams(self.unit_test_model)
        self.classdiagrams = self.vppdiagrams.GetClassDiagrams()
        self.statediagrams = self.vppdiagrams.GetStateDiagrams()

    def test_classDiagrams(self):
        expectedIDToName = {u'QcgxGqqFYEAQWAnB': u'ProtocolStack', u'sb74Kw6GAqAA7wjN': u'TestClassDiagram'}

        self.assertEqual(len(self.classdiagrams), 2									, "Expected 2 class diagrams in test project")

        for key,val in expectedIDToName.items():
            self.assertTrue((key in self.classdiagrams)								, "Class diagram '" + val + "' in TestModels.vpp test project ID changed.")
            self.assertEqual(self.classdiagrams[key], val						 	, "Class diagram '" + val + "' in TestModels.vpp test project NAME changed.")
            self.assertEqual(key, self.vppdiagrams.GetIDFromClassDiagramName(val)	, "Error in lookup class diagram " + val)

    def test_stateDiagrams(self):
        expectedIDToName = {u'4C0lKqqFYEAQWAg_': u'TestStateMachine'}

        self.assertEqual(len(self.statediagrams), 1									, "Expected 1 state diagram in test project")

        for key, val in expectedIDToName.items():
            self.assertTrue((key in self.statediagrams)								, "State diagram '" + val + "' in TestModels.vpp test project ID changed.")
            self.assertEqual(self.statediagrams[key], val							, "State diagram '" + val + "' in TestModels.vpp test project NAME changed.")
            self.assertEqual(key, self.vppdiagrams.GetIDFromStateDiagramName(val)	, "Error in lookup state diagram " + val)

    def test_stateDiagramTransitionTable(self):
        vppdiagramelements = VPPDiagramElements(self.unit_test_model)
        vppmodelelements = VPPModelElements(self.unit_test_model)
        elements = vppdiagramelements.GetDiagramElements(self.vppdiagrams.GetIDFromStateDiagramName('TestStateMachine'))

        self.assertEqual(len(elements),  8, "Expected 8 state diagram in elements in TestStateMachine in TestModels.vpp")

        # Create a state diagram with NAME, ID and CHILDREN ELEMENTs
        statediagram = StateDiagram('TestStateMachine', self.vppdiagrams.GetIDFromStateDiagramName('TestStateMachine'), elements, vppmodelelements)
        tt = statediagram.GetTransitionTable()

        self.assertEqual(len(tt), 3,		"Expected 3 rows in transition table from TestStateMachine in TestModels.vpp")

        self.assertTrue(tt[0][0] == 'StateRed' 		and tt[0][1] == 'EventButtonPressed' and tt[0][2] == 'StateOrange' 	and tt[0][3] == 'OnOrange' 	and tt[0][4] == 'GuardCanChangeToOrange', "Error with row 1 of transition table from TestStateMachine in TestModels.vpp")
        self.assertTrue(tt[1][0] == 'StateOrange' 	and tt[1][1] == 'EventButtonPressed' and tt[1][2] == 'StateGreen' 	and tt[1][3] == 'OnGreen' 	and tt[1][4] == 'GuardCanChangeToGreen', "Error with row 2 of transition table from TestStateMachine in TestModels.vpp")
        self.assertTrue(tt[2][0] == 'StateGreen' 	and tt[2][1] == 'EventButtonPressed' and tt[2][2] == 'StateRed' 	and tt[2][3] == 'OnRed' 	and tt[2][4] == 'GuardCanChangeToRed', "Error with row 3 of transition table from TestStateMachine in TestModels.vpp")

if __name__ == "__main__":
    unittest.main()