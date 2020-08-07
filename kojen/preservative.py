#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'eugene'

import os
from collections import OrderedDict
import unittest
import shutil

'''

    MIT License

    Copyright (c) 2015 Eugene Grobbelaar (email : koh.jaen@yahoo.de)

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

'''
'''
	Preservation works by keeping the same code between two unique tag pairs, in a round trip fashion
	A round-trip is required, so in generation, the 'collect' function should be called before the old generated file is
	overwritten with the newly generated file, and the 'replace' function should be called after the new file has been structured
	and before it is output to disk.

	Any tags no longer present in the new generated file will be lost.

	The TAGs must have a common prefix, with a unique suffix:

	{{{USER_XXX, where XXX is unique throughout the file. This 'XXX' may also be generated in further generations.

	eg:
	{{{USER_MYSTUFF}}}
	// all manual code between these two tags will be preserved between round-trips.
	{{{USER_MYSTUFF}}}

	{{{USER_ is the default prefix tag. It can be replaced with whatever makes writing templates prettier to you.
'''


def CleanUpLine(line):
	return line.replace('\t', '') \
		.replace('\n', '') \
		.replace(r'\t', '') \
		.replace(r'\n', '') \
		.replace(' ', '') \
		.replace('/', '') \
		.replace('*', '') \
		.replace('#', '') \
		.replace('~', '') \
		.replace('`', '') \
		.replace('@', '') \
		.replace('$', '') \
		.replace('%', '') \
		.replace('?', '') \
		.replace('+', '') \
		.replace('}', '') \
		.replace(']', '') \
		.replace('>', '') \
		.replace('=', '')


class Preservative:

	def __init__(self, outputfiledir):
		self._TAG_PREFIX_ = '{{{USER_'
		# {'FileName', {'Tag', [line1, line2,..., lineX]}}
		self.preserved_tags_per_file = {}
		self.preserved_tags_per_file_WAS_USED = {}

		# Does the input exist? (The input is the output of the code generator before it rewrites it)
		if os.path.exists(outputfiledir):
			files = os.listdir(outputfiledir)  # Is the input empty
			if not files:
				print(outputfiledir + " is empty, nothing to preserve")
			else:
				self.Collect(outputfiledir)
		else:
			print(outputfiledir + " does not exist, nothing to preserve")



	def Collect(self, directory):
		for root, dirs, files in os.walk(directory):
			for file in files:
				if file.find('.h') > -1 or file.find('.cpp') > -1 or file.find('.py') > -1 or file.find('.cs') > -1:
					filename_and_path = os.path.join(root, file)
					self.preserved_tags_per_file[filename_and_path] = {}
					self.preserved_tags_per_file_WAS_USED[filename_and_path] = {}
					with open(filename_and_path) as f:
						is_preserving = False
						__current_preservation = None
						__current_preservation_line = ""
						try:  # python 3 gave some sort of decode errors...
							for line in f:
								tag_found = (line.find(self._TAG_PREFIX_) > -1)
								if is_preserving and tag_found:
									# stop
									self.preserved_tags_per_file[filename_and_path][__current_preservation_line] = []
									self.preserved_tags_per_file_WAS_USED[filename_and_path][__current_preservation_line] = False
									for line in __current_preservation:
										self.preserved_tags_per_file[filename_and_path][__current_preservation_line].append(line)
									__current_preservation_line = ""
									is_preserving = False
									tag_found = False
	
								if is_preserving:
									if __current_preservation is None or __current_preservation_line == "":
										raise RuntimeError("Empty preservation...something is wrong...")
									# record
									__current_preservation.append(line)
	
								if not is_preserving and tag_found:
									# start
									is_preserving = True
									__current_preservation_line = CleanUpLine(line)
									__current_preservation = []
						except UnicodeDecodeError:
							print("<Warning> UnicodeDecodeError caught on " + file + ". If this file is not part of the currently preserved files, then ignore.")
						except:
							print("<Warning> Unknown error caught on " + file + ". If this file is not part of the currently preserved files, then ignore.")

	# filenames_to_lines is an ordereddictionary {'filename', [line1, line2 ...] ...}
	def Emplace(self, filenames_to_lines):
		for fn, lines in filenames_to_lines.items():
			# if fn in self.preserved_tags_per_file:  # Preferred py2/3 way of testing for a key in a dictionary.
			for outputfile, tags in self.preserved_tags_per_file.items():
				if outputfile.find(fn) > -1:
					#tags = self.preserved_tags_per_file[fn]
					new_lines = []
					tag_found = False
					tagline = ""
					for line in lines:
						new_lines.append(line)
						cleaned_up_line = CleanUpLine(line)
						if not tag_found and (cleaned_up_line in tags):
							tagline = line
							tag_found = True
							self.preserved_tags_per_file_WAS_USED[outputfile][cleaned_up_line] = True
							for i in tags[cleaned_up_line]:
								new_lines.append(i)
						elif tag_found and (cleaned_up_line in tags):  # 2nd tag...
							tag_found = False
						elif tag_found and not (cleaned_up_line in tags):  # 2nd tag missing...add it
							new_lines.append(tagline)
							tag_found = False
					# replace
					filenames_to_lines[fn] = new_lines

		for outputfile, tags in self.preserved_tags_per_file_WAS_USED.items():
			for tag, was_used in tags.items():
				if not was_used:
					if len(self.preserved_tags_per_file[outputfile][tag]) > 0:
						if not "LostCode.txt" in filenames_to_lines:
							filenames_to_lines["LostCode.txt"] = []
						filenames_to_lines["LostCode.txt"].append(outputfile + "\n")
						filenames_to_lines["LostCode.txt"].append(tag + "\n")
						for i in self.preserved_tags_per_file[outputfile][tag]:
							filenames_to_lines["LostCode.txt"].append(i + "\n")
						filenames_to_lines["LostCode.txt"].append(tag + "\n")
						filenames_to_lines["LostCode.txt"].append("---------------------------------------------" + "\n")

	# Use this to set a custom code preservation tag prefix
	def SetPrefix(self, new_prefix):
		self._TAG_PREFIX_ = new_prefix


class TestPreservative(unittest.TestCase):
	""" Unit test. Not sure how to programmatically test this.
		Its better done by inspection?
	"""
	def setUp(self):
		self.TempFolder = "testpreservative"
		self.HeaderFileName = "TestPreservative.h"
		self.SourceFileName = "TestPreservative.cpp"
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
		with open(os.path.join(self.TempFolder, filename), 'w+') as temp_file:
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


def VisualInspect():
	t = TestPreservative()
	t.setUp()
	t.test_Stuff()
	for filename, linesinfile in t.newFiles.items():
		print("****** "+filename+"  ------")
		for line in linesinfile:
			print(line)
	# t.tearDown()


if __name__ == "__main__":
	# VisualInspect()
	unittest.main()

