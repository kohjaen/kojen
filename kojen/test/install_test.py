import unittest
import os
from kojen.Install import *
from filecmp import dircmp

relative_root = "trash"
relative_paths = [
    "nested",
    "nested/nested",
    "nested/nested/nested",
]

class TestInstall(unittest.TestCase):
    def setUp(self):
        """Will create one per path."""
        self.trash_root = os.path.normpath(os.path.join(os.getcwd(), relative_root))
        self.trash_paths = []
        self.relative_file_paths = []
        self.filenames = []
        cnt = 1
        self.trash_paths.append(self.trash_root)
        fn = "file" + str(cnt) + ".py"
        self.relative_file_paths.append(os.path.normpath(fn))
        self.filenames.append(fn)
        cnt = cnt + 1
        for p in relative_paths:
            self.trash_paths.append(os.path.normpath(os.path.join(self.trash_root,p)))
            fn = "file" + str(cnt) + ".py"
            self.relative_file_paths.append(os.path.normpath(os.path.join(p, fn)))
            self.filenames.append(fn)
            cnt = cnt + 1
        cnt = 1
        for p in self.trash_paths:
            if not os.path.exists(p):
                os.makedirs(p)
            filename = os.path.normpath(os.path.join(p, "file" + str(cnt) + ".py"))
            with open(filename, "w") as file:
                file.write("#!/usr/bin/env python\n")
                file.write("import sys\n")
                file.write("sys.exit(0)")
            cnt = cnt + 1

    def tearDown(self):
        shutil.rmtree(self.trash_root)

    def checkDirCmpResult(self, result):
        """Recursive check of file differences in folders"""
        self.assertFalse(result.diff_files)
        for sub_dcmp in result.subdirs.values():
            self.checkDirCmpResult(sub_dcmp)

    def test_InstallTemplates(self):
        InstallTemplates(self.trash_root)
        self.checkDirCmpResult(dircmp(self.trash_root, getUserTemplateRoot()))

    def test_ContainsTemplates(self):
        InstallTemplates(self.trash_root)
        # Found cases
        for p in relative_paths:
            self.assertTrue(ContainsTemplates(p))
        for p in self.filenames:
            self.assertTrue(ContainsTemplates(p))
        for p in self.relative_file_paths:
            self.assertTrue(ContainsTemplates(p))
        # Not found cases
        for p in relative_paths:
            self.assertFalse(ContainsTemplates(p.replace("n","t")))
        for p in self.filenames:
            self.assertFalse(ContainsTemplates(p.replace("py","cs")))
        for p in self.relative_file_paths:
            self.assertFalse(ContainsTemplates(p.replace("py","cs")))
        self.assertFalse(ContainsTemplates("File6.py"))

    def test_UninstallTemplates(self):
        InstallTemplates(self.trash_root)
        UninstallTemplates()
        self.assertFalse(os.path.exists(getUserTemplateRoot()))

