import unittest
from collections import OrderedDict
import shutil
from kojen.preservative import *

class TestPreservative(unittest.TestCase):
    """ Unit test. Not sure how to programmatically test this.
        Its better done by inspection?
    """
    def setUp(self):
        self.TempFolder = "testpreservative"
        self.HeaderFileName = os.path.join(self.TempFolder, "TestPreservative.h")
        self.SourceFileName = os.path.join(self.TempFolder, "TestPreservative.cpp")
        self.Preserve1 = "aabbccddeeffgghh"
        self.Preserve2 = "1122334455667788"
        self.Preserve3 = "howdydooody"
        self.removeDir()
        self.makeDir()
        self.makeFile(self.HeaderFileName)
        self.makeFile(self.SourceFileName)

    def tearDown(self):
        self.removeDir()

    def removeDir(self):
        if os.path.exists(self.TempFolder):
            try:
                shutil.rmtree(self.TempFolder)
            except OSError:
                print("Deletion of the directory %s failed" % self.TempFolder)

    def makeDir(self):
        try:
            os.mkdir(self.TempFolder)
        except OSError:
            print("Creation of the directory %s failed" % self.TempFolder)

    def makeFile(self, filename):
        with open(filename, 'w+') as temp_file:
            for i in range(10):
                temp_file.write('1' + i*"1" + '\n')
            temp_file.write('{{{USER_STUFF_1\n')
            temp_file.write(self.Preserve1 + '\n')
            temp_file.write(self.Preserve1 + '\n')
            temp_file.write(self.Preserve1 + '\n')
            temp_file.write('{{{USER_STUFF_1\n')
            for i in range(20):
                temp_file.write(10*'2' + i*"2" + '\n')
            temp_file.write('{{{USER_STUFF_2\n')
            temp_file.write(self.Preserve2 + '\n')
            temp_file.write(self.Preserve2 + '\n')
            temp_file.write(self.Preserve2 + '\n')
            temp_file.write('{{{USER_STUFF_2\n')
            for i in range(30):
                temp_file.write(20*'3' + i*"3" + '\n')
            temp_file.write('{{{USER_STUFF_3\n')
            temp_file.write(self.Preserve3 + '\n')
            temp_file.write(self.Preserve3 + '\n')
            temp_file.write(self.Preserve3 + '\n')
            temp_file.write('{{{USER_STUFF_3\n')

    def test_Stuff(self):
        jam = Preservative(self.TempFolder)
        self.newFiles = OrderedDict()
        self.newFiles[self.HeaderFileName] = ['bla bla', '{{{USER_STUFF_2', '{{{USER_STUFF_2', 'crap', 'crap', 'crap', '{{{USER_STUFF_3', '{{{USER_STUFF_3', '{{{USER_STUFF_1', '{{{USER_STUFF_1', 'dang', ]
        self.newFiles[self.SourceFileName] = ['{{{USER_STUFF_3', '{{{USER_STUFF_3', 'bla bla', 'crap', 'crap', 'crap', '{{{USER_STUFF_1', '{{{USER_STUFF_1', '{{{USER_STUFF_2', '{{{USER_STUFF_2', 'dang', ]

        oldHeaderSize = len(self.newFiles[self.HeaderFileName])
        oldSourceSize = len(self.newFiles[self.SourceFileName])

        jam.Emplace(self.newFiles)

        # for each set of tags, the same text should be replaced 3 time...
        self.assertTrue((oldHeaderSize + 9) == len(self.newFiles[self.HeaderFileName]), "Expected at 9 more lines in " + self.HeaderFileName)
        self.assertTrue((oldSourceSize + 9) == len(self.newFiles[self.SourceFileName]), "Expected at 9 more lines in " + self.SourceFileName)

        # Check that the preserved text matches what is expected...
        self.assertIn(self.HeaderFileName, jam.preserved_tags_per_file, "Missing h")
        self.assertIn("{{{USER_STUFF_1", jam.preserved_tags_per_file[self.HeaderFileName], "Missing tag .h(1)")
        self.assertIn("{{{USER_STUFF_2", jam.preserved_tags_per_file[self.HeaderFileName], "Missing tag .h(2)")
        self.assertIn("{{{USER_STUFF_3", jam.preserved_tags_per_file[self.HeaderFileName], "Missing tag .h(3)")
        self.assertEqual(len(jam.preserved_tags_per_file[self.HeaderFileName]["{{{USER_STUFF_1"]), 3, "Wrong size of preserved data .h(1)")
        self.assertEqual(len(jam.preserved_tags_per_file[self.HeaderFileName]["{{{USER_STUFF_2"]), 3, "Wrong size of preserved data .h(2)")
        self.assertEqual(len(jam.preserved_tags_per_file[self.HeaderFileName]["{{{USER_STUFF_3"]), 3, "Wrong size of preserved data .h(3)")
        for line in jam.preserved_tags_per_file[self.HeaderFileName]["{{{USER_STUFF_1"]:
            self.assertTrue(line.find(self.Preserve1) != -1)
        for line in jam.preserved_tags_per_file[self.HeaderFileName]["{{{USER_STUFF_2"]:
            self.assertTrue(line.find(self.Preserve2) != -1)
        for line in jam.preserved_tags_per_file[self.HeaderFileName]["{{{USER_STUFF_3"]:
            self.assertTrue(line.find(self.Preserve3) != -1)

        self.assertIn(self.SourceFileName, jam.preserved_tags_per_file, "Missing cpp")
        self.assertIn("{{{USER_STUFF_1", jam.preserved_tags_per_file[self.SourceFileName], "Missing tag .cpp(1)")
        self.assertIn("{{{USER_STUFF_2", jam.preserved_tags_per_file[self.SourceFileName], "Missing tag .cpp(2)")
        self.assertIn("{{{USER_STUFF_3", jam.preserved_tags_per_file[self.SourceFileName], "Missing tag .cpp(3)")
        self.assertEqual(len(jam.preserved_tags_per_file[self.SourceFileName]["{{{USER_STUFF_1"]), 3, "Wrong size of preserved data .cpp(1)")
        self.assertEqual(len(jam.preserved_tags_per_file[self.SourceFileName]["{{{USER_STUFF_2"]), 3, "Wrong size of preserved data .cpp(2)")
        self.assertEqual(len(jam.preserved_tags_per_file[self.SourceFileName]["{{{USER_STUFF_3"]), 3, "Wrong size of preserved data .cpp(3)")
        for line in jam.preserved_tags_per_file[self.SourceFileName]["{{{USER_STUFF_1"]:
            self.assertTrue(line.find(self.Preserve1) != -1)
        for line in jam.preserved_tags_per_file[self.SourceFileName]["{{{USER_STUFF_2"]:
            self.assertTrue(line.find(self.Preserve2) != -1)
        for line in jam.preserved_tags_per_file[self.SourceFileName]["{{{USER_STUFF_3"]:
            self.assertTrue(line.find(self.Preserve3) != -1)

        # Todo : check that the 'output' has the same stuff? Doing once by inspection is actually ok...however...

if __name__ == "__main__":
    unittest.main()