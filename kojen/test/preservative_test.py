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

    def checkOutput(self, ordered_dictionary_of_outputs):
        for name, f in ordered_dictionary_of_outputs.items():
            user1 = False
            user2 = False
            user3 = False
            self.assertIn("{{{USER_STUFF_1", f, "Missing tag (1) in output")
            self.assertIn("{{{USER_STUFF_2", f, "Missing tag (2) in output")
            self.assertIn("{{{USER_STUFF_3", f, "Missing tag (3) in output")
            for i in range(len(f)):
                line = f[i]
                if not user1 and "{{{USER_STUFF_1" in line:
                    user1 = True
                    self.assertTrue(f[i + 1].find(self.Preserve1) != -1)
                    self.assertTrue(f[i + 2].find(self.Preserve1) != -1)
                    self.assertTrue(f[i + 3].find(self.Preserve1) != -1)
                    self.assertTrue(f[i + 4].find("{{{USER_STUFF_1") != -1)
                if not user2 and "{{{USER_STUFF_2" in line:
                    user2 = True
                    self.assertTrue(f[i + 1].find(self.Preserve2) != -1)
                    self.assertTrue(f[i + 2].find(self.Preserve2) != -1)
                    self.assertTrue(f[i + 3].find(self.Preserve2) != -1)
                    self.assertTrue(f[i + 4].find("{{{USER_STUFF_2") != -1)
                if not user3 and "{{{USER_STUFF_3" in line:
                    user3 = True
                    self.assertTrue(f[i + 1].find(self.Preserve3) != -1)
                    self.assertTrue(f[i + 2].find(self.Preserve3) != -1)
                    self.assertTrue(f[i + 3].find(self.Preserve3) != -1)
                    self.assertTrue(f[i + 4].find("{{{USER_STUFF_3") != -1)

    def checkPreservative(self, jam):
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

    def test_UseCase_FreshTemplateFromFileOnDisk(self):
        jam = Preservative(self.TempFolder)
        newFiles = OrderedDict()
        newFiles[self.HeaderFileName] = ['bla bla', '{{{USER_STUFF_2', '{{{USER_STUFF_2', 'crap', 'crap', 'crap', '{{{USER_STUFF_3', '{{{USER_STUFF_3', '{{{USER_STUFF_1', '{{{USER_STUFF_1', 'dang', ]
        newFiles[self.SourceFileName] = ['{{{USER_STUFF_3', '{{{USER_STUFF_3', 'bla bla', 'crap', 'crap', 'crap', '{{{USER_STUFF_1', '{{{USER_STUFF_1', '{{{USER_STUFF_2', '{{{USER_STUFF_2', 'dang', ]

        oldHeaderSize = len(newFiles[self.HeaderFileName])
        oldSourceSize = len(newFiles[self.SourceFileName])

        jam.Emplace(newFiles)

        # for each set of tags, the same text should be replaced 3 time...
        self.assertTrue((oldHeaderSize + 9) == len(newFiles[self.HeaderFileName]), "Expected at 9 more lines in " + self.HeaderFileName)
        self.assertTrue((oldSourceSize + 9) == len(newFiles[self.SourceFileName]), "Expected at 9 more lines in " + self.SourceFileName)

        # Check that the preserved text matches what is expected...
        self.checkPreservative(jam)
        # Check that the 'output' has the same expected things...
        self.checkOutput(newFiles)

    def test_UseCase_CloneFromOneFileToAnother(self):
        jam = Preservative(self.TempFolder)
        newFiles = OrderedDict()
        newFiles[self.HeaderFileName] = ['bla bla', '{{{USER_STUFF_2', "thisshouldgo2" ,'{{{USER_STUFF_2', 'crap', 'crap', 'crap', '{{{USER_STUFF_3', "thisshouldgo3" ,'{{{USER_STUFF_3', '{{{USER_STUFF_1', "thisshouldgo" , '{{{USER_STUFF_1', 'dang', ]
        newFiles[self.HeaderFileName].extend(["fish", "{{{USER_NOT_IN_OTHER", "BUTTHISSHOULDREMAIN", "{{{USER_NOT_IN_OTHER", "paste"])
        newFiles[self.SourceFileName] = ['{{{USER_STUFF_3', "thisshouldgo3" , '{{{USER_STUFF_3', 'bla bla', 'crap', 'crap', 'crap', '{{{USER_STUFF_1', "thisshouldgo" , '{{{USER_STUFF_1', '{{{USER_STUFF_2', "thisshouldgo2" , '{{{USER_STUFF_2', 'dang', ]
        newFiles[self.SourceFileName].extend(["fish", "{{{USER_NOT_IN_OTHER", "BUTTHISSHOULDREMAIN", "{{{USER_NOT_IN_OTHER", "paste"])

        oldHeaderSize = len(newFiles[self.HeaderFileName])
        oldSourceSize = len(newFiles[self.SourceFileName])

        jam.Emplace(newFiles, True)

        # for each set of tags, the same text should be replaced 3 time...but we replaced 1 line per tag
        self.assertTrue((oldHeaderSize + 9 - 3) == len(newFiles[self.HeaderFileName]), "Expected at 6 more lines in " + self.HeaderFileName)
        self.assertTrue((oldSourceSize + 9 - 3) == len(newFiles[self.SourceFileName]), "Expected at 6 more lines in " + self.SourceFileName)

        # Check that the preserved text matches what is expected...
        self.checkPreservative(jam)
        # Check that the unique tags are not in the preservative
        self.assertNotIn("{{{USER_NOT_IN_OTHER", jam.preserved_tags_per_file[self.HeaderFileName], "Unexpected tag .h(4)")
        self.assertNotIn("{{{USER_NOT_IN_OTHER", jam.preserved_tags_per_file[self.SourceFileName], "Unexpected tag .cpp(4)")
        # Check that the 'output' has the same expected things...
        self.checkOutput(newFiles)
        # Check that the things that were not in the source are still in the destination (and preserved)
        for name, f in newFiles.items():
            notClone = False
            self.assertIn("{{{USER_NOT_IN_OTHER", f, "Missing tag (unique) in output")
            for i in range(len(f)):
                line = f[i]
                if not notClone and "{{{USER_NOT_IN_OTHER" in line:
                    notClone = True
                    self.assertTrue(f[i + 1].find("BUTTHISSHOULDREMAIN") != -1)
                    self.assertTrue(f[i + 2].find("{{{USER_NOT_IN_OTHER") != -1)

    def test_SubstringFilenameIsNotMistakenForAnotherFile(self):
        """A generated filename that is a substring of another (e.g. "Sample.cpp" inside
        "Test.Sample.cpp") must never have its preserved code cross-applied to that other file: a
        substring test on the filename (outputfile.find(fn) > -1) would wrongly match both, bleeding
        one file's hand-written code into the other whenever they happen to share a tag name.

        Collection order is set up explicitly (short file first, long file second) rather than via a
        directory walk, so the cross-match -- when present -- deterministically overwrites the short
        file's correct result with the long file's, instead of depending on filesystem listing order.
        """
        short_name = "Sample.cpp"
        long_name = "Test.Sample.cpp"
        short_path = os.path.join(self.TempFolder, short_name)
        long_path = os.path.join(self.TempFolder, long_name)
        with open(short_path, 'w+') as temp_file:
            temp_file.write("{{{USER_INCLUDES\n")
            temp_file.write("FROM_SHORT_FILE\n")
            temp_file.write("{{{USER_INCLUDES\n")
        with open(long_path, 'w+') as temp_file:
            temp_file.write("{{{USER_INCLUDES\n")
            temp_file.write("FROM_LONG_FILE\n")
            temp_file.write("{{{USER_INCLUDES\n")

        jam = Preservative(short_path)  # single-file constructor: collects short_path only
        jam.CollectFile(long_path)  # then long_path, explicitly second -- guarantees insertion order
        newFiles = OrderedDict()
        newFiles[short_name] = ['{{{USER_INCLUDES', '{{{USER_INCLUDES']
        newFiles[long_name] = ['{{{USER_INCLUDES', '{{{USER_INCLUDES']

        jam.Emplace(newFiles)

        self.assertTrue(any("FROM_SHORT_FILE" in line for line in newFiles[short_name]))
        self.assertFalse(any("FROM_LONG_FILE" in line for line in newFiles[short_name]))
        self.assertTrue(any("FROM_LONG_FILE" in line for line in newFiles[long_name]))
        self.assertFalse(any("FROM_SHORT_FILE" in line for line in newFiles[long_name]))

    def test_TagMentionedInProseIsNotTreatedAsAMarker(self):
        """A comment that merely *mentions* a tag by name (not as a real, line-leading marker) must
        not be collected as a marker: doing so desyncs the collector's open/close toggle and makes it
        swallow everything up to the next real marker as that bogus tag's "body", which then grows
        without bound on every later regeneration (re-inserted on top of the same static prose line).
        """
        filename = os.path.join(self.TempFolder, "Prose.h")
        with open(filename, 'w+') as temp_file:
            temp_file.write("// Scenario tests belong in {{{USER_TESTS}}}, written once.\n")
            temp_file.write("#include <cstdint>\n")
            temp_file.write("{{{USER_TESTS\n")
            temp_file.write("real_hand_written_code();\n")
            temp_file.write("{{{USER_TESTS\n")

        jam = Preservative(filename)

        self.assertIn("{{{USER_TESTS", jam.preserved_tags_per_file[filename])
        preserved_body = jam.preserved_tags_per_file[filename]["{{{USER_TESTS"]
        self.assertEqual(len(preserved_body), 1, "Should only preserve the one real hand-written line")
        self.assertTrue(preserved_body[0].find("real_hand_written_code();") != -1)
        # The '#include' line between the false-positive prose and the real marker must not have been
        # swallowed into any preserved tag's body.
        for body in jam.preserved_tags_per_file[filename].values():
            self.assertFalse(any("#include" in line for line in body))

    def test_RegenerationWithProseMentionDoesNotGrowUnbounded(self):
        """Regenerating a file whose static template text mentions a tag in prose must not grow the
        file on every round-trip."""
        filename = os.path.join(self.TempFolder, "Prose.cpp")
        static_lines = [
            "// Scenario tests belong in {{{USER_TESTS}}}, written once.\n",
            "#include <cstdint>\n",
            "{{{USER_TESTS\n",
            "{{{USER_TESTS\n",
        ]
        with open(filename, 'w+') as temp_file:
            temp_file.writelines(static_lines)

        for _ in range(5):
            jam = Preservative(filename)
            newFiles = OrderedDict()
            newFiles[filename] = list(static_lines)
            jam.Emplace(newFiles)
            with open(filename, 'w') as temp_file:
                temp_file.writelines(newFiles[filename])

        with open(filename) as temp_file:
            self.assertEqual(len(temp_file.readlines()), len(static_lines))

if __name__ == "__main__":
    unittest.main()
