#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'eugene'
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
import os, shutil
import fnmatch
import sys

# Python2 -> 3 shennanigans...try support both
try:
	from smgen import *		# py2
except (ModuleNotFoundError, ImportError) as e:
	from .smgen import *	# py3

from cogapp import *

def GetDir(rootdir, dir):
	matches = []
	for root, dirnames, filenames in os.walk(rootdir):
		for filename in fnmatch.filter(dirnames, dir):
			matches.append(os.path.join(root, filename))
	return matches
			

def GetFile(rootdir, file):
	matches = []
	for root, dirnames, filenames in os.walk(rootdir):
		for filename in fnmatch.filter(filenames, file):
			matches.append(os.path.join(root, filename))


def Generate(output_dir, pythonfile, namespacename, classname, declspec="", template_dir=""):

	if not template_dir.strip():
		template_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "protocol_templates")

	print("*************************************")
	print("******* Protogen ********************")
	print("*************************************")
	print(" Template Dir : " + template_dir)
	print(" Output Dir   : " + output_dir)
	print(" Python File  : " + pythonfile)
	print(" Executing in : " + os.path.realpath(__file__))
	print("*************************************")
	
	# Use the directory THIS file is in as the intermediate path
	intermediate_dir = os.path.dirname(os.path.realpath(__file__))

	# copy the python file to this directory...
	tmp_python_file = os.path.join(intermediate_dir, "Tmp.py")
	shutil.copy(pythonfile,tmp_python_file)

	# Customize the templates with your interface file, namespace names, classnames, declspecs
	smgen = CStateMachineGenerator(template_dir, intermediate_dir)
	#filenames = smgen.GenerateProtocol(pythonfile, namespacename, classname, declspec, output_dir)
	filenames = smgen.GenerateProtocol("Tmp.py", namespacename, classname, declspec, output_dir)

	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	# Create Cog Input
	writer = open(os.path.join(intermediate_dir, "files.txt"), 'w')
	for f in filenames:
		writer.write(os.path.abspath(os.path.join(intermediate_dir, f)) + " -o " + os.path.abspath(os.path.join(output_dir, f)) + "\r\n")
	writer.close()
	
	'''
	# Invoke cog on intermediate dir
	'''

	c = Cog()
	c.callableMain(['cog', '-d', '@' + os.path.join(intermediate_dir, "files.txt")])

	'''
	# Copy all files (except files.txt) to output dir
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	for f in filenames:
		os.rename(os.path.join(intermediate_dir,f),os.path.join(output_dir,f))
	'''

	# Delete all files from intermediate dir
	os.remove(os.path.join(intermediate_dir, "files.txt"))
	for f in filenames:
		os.remove(os.path.join(intermediate_dir, f))
	os.remove(tmp_python_file)


if __name__ == "__main__":
	import sys
	if len(sys.argv) < 5:
		print("Usage : python protogen <output dir> <python if file> <namespace> <class> optional <declspec> optional <template dir>")
	else:
		output_dir = str(sys.argv[1])
		pythonfile = str(sys.argv[2])
		namespacename = str(sys.argv[3])
		classname = str(sys.argv[4])
		declspec = ""
		if len(sys.argv) >= 6:
			declspec = str(sys.argv[5])
		template_dir = ""
		if len(sys.argv) >= 7:
			template_dir = str(sys.argv[6])

		Generate(output_dir, pythonfile, namespacename, classname, declspec, template_dir)
