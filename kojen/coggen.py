#!/usr/bin/env python3
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

__TAG_AUTHOR__              = '<<<AUTHOR>>>'
__TAG_NAMESPACE__           = '<<<NAMESPACE>>>'
__TAG_CLASS_NAME__          = '<<<CLASSNAME>>>'
__TAG_PyIFGen_NAME__        = '<<<PYIFGENNAME>>>'
__TAG_GROUP__               = '<<<GROUP>>>'
__TAG_BRIEF__               = '<<<BRIEF>>>'
__TAG_DECLSPEC_DLL_EXPORT__ = '<<<DLL_EXPORT>>>'

try:
    from .preservative import *
except (ModuleNotFoundError, ImportError) as e:
    from preservative import *

try:
    from .cgen import CGenerator, CCodeModel, FileCopyUtil, snake_case, setFilenameReplace
except (ModuleNotFoundError, ImportError) as e:
    from cgen import CGenerator, CCodeModel, FileCopyUtil, snake_case, setFilenameReplace

from cogapp import *
import shutil

class CCogCodeModel:
    def __init__(self):
        self.namespacename    = ""
        self.declspecdllexport = ""
        self.pythoninterfacegeneratorfilename = ""
        self.classname = ""
        self.group = ""
        self.brief = ""

class CCogGenerator(CGenerator):
    def __init__(self, inputfiledir, outputfiledir,  classname, language=None, author='Anonymous', group='', brief=''):
        CGenerator.__init__(self, inputfiledir, outputfiledir, language, author, group, brief)
        self.dict_to_replace_filenames = {}
        setFilenameReplace(self.dict_to_replace_filenames, classname)

    def loadtemplates_firstfiltering(self, ccmodel):
        """
        See baseclass implementation. This just prepares the dictionary of things to replace
        for this type of codegeneration.

        @param smmodel:
        @return: cgen.CCodeModel, a dictionary -> {filename,[lines]}
        """

        dict_to_replace_lines = {}
        dict_to_replace_lines[__TAG_CLASS_NAME__] = ccmodel.classname
        dict_to_replace_lines[__TAG_PyIFGen_NAME__] = ccmodel.pythoninterfacegeneratorfilename.replace('.py','')  # hack : for tcpgen simple templates,
        dict_to_replace_lines[__TAG_NAMESPACE__] = ccmodel.namespacename
        dict_to_replace_lines[__TAG_AUTHOR__] = self.author
        dict_to_replace_lines[__TAG_DECLSPEC_DLL_EXPORT__] = ccmodel.declspecdllexport
        dict_to_replace_lines[__TAG_GROUP__] = ccmodel.group
        dict_to_replace_lines[__TAG_BRIEF__] = ccmodel.brief

        return CGenerator.loadtemplates_firstfiltering(self, dict_to_replace_lines, self.dict_to_replace_filenames)

    def generate_filenames_from_templates(self, file) -> str:
        return CGenerator.generate_filenames_from_templates(self,file, self.dict_to_replace_filenames)

    def Generate(self, pythoninterfacegeneratorfilename, namespacenname, classname, group, brief, preserve_dir="",dclspc="") -> list:
        sm = CCogCodeModel()
        sm.pythoninterfacegeneratorfilename = pythoninterfacegeneratorfilename
        sm.namespacename = namespacenname
        sm.declspecdllexport = dclspc
        sm.classname = classname
        sm.group = group
        sm.brief = brief

        self.cm = self.loadtemplates_firstfiltering(sm)

        # Preserve user code.
        self.preserve_usercode_in_files(self.cm,preserve_dir)

        # Write output to file, and return filenames.
        return self.createoutput(self.cm.filenames_to_lines)

def PreCogCopyFileAndInsertPythonImport(file_from, file_to, python_import):
    # Need to put the correct python file for cog to import!
    with open(file_from, "rt") as fin:
        with open(file_to, "wt") as fout:
            for line in fin:
                fout.write(line.replace(__TAG_PyIFGen_NAME__, python_import))

def GenerateFile(output_dir, pythonfile, cog_template_file, author, namespacename, classname, group, brief, dclspc="") -> list:
    cog_template_file = cog_template_file.strip()
    if os.path.isdir(cog_template_file):
        return GenerateDirectory(output_dir, pythonfile, cog_template_file, author, namespacename, classname, group, brief, dclspc)
    if not os.path.isfile(cog_template_file):
        print("Error : file '" + cog_template_file + "' does not exist. Aborting.")
        return []

    print("*************************************")
    print("******* CogGen (file)****************")
    print("*************************************")
    print(" Template File: " + cog_template_file)
    print(" Output Dir   : " + output_dir)
    print(" Python File  : " + pythonfile)
    print(" Executing in : " + os.path.realpath(__file__))
    print("*************************************")

    cog_template_dir = os.path.dirname(cog_template_file)
    cogged_template_dir = os.path.join(cog_template_dir, "cogged")
    if not os.path.exists(cogged_template_dir):
        os.makedirs(cogged_template_dir)
    # copy the python file to the cogged directory, pre-cog...
    tmp_python_file = os.path.join(cogged_template_dir, os.path.basename(pythonfile))
    shutil.copy(pythonfile, tmp_python_file)
    # copy the cog template to the cogged directory, pre-cog...and rename it as such. This is the first pass.
    file_to_cog = os.path.join(cogged_template_dir,os.path.basename(cog_template_file))
    PreCogCopyFileAndInsertPythonImport(cog_template_file, file_to_cog + ".PreCog", os.path.splitext(os.path.basename(tmp_python_file))[0])
    # Create a generator
    gen = CCogGenerator(cogged_template_dir, output_dir, classname, None, author)
    with open(os.path.join(cogged_template_dir, "files.txt"), 'w') as writer:
        writer.write('"' + file_to_cog + ".PreCog" + '" -o "' + file_to_cog + '"\r\n')
    # Invoke Cog on intermediate dir
    c = Cog()
    c.callableMain(['cog', '-d', '@' + os.path.join(cogged_template_dir, "files.txt")])
    # clean up cog file and python file
    os.remove(os.path.join(cogged_template_dir, "files.txt"))
    os.remove(tmp_python_file)
    os.remove(file_to_cog + ".PreCog")
    # Do rest...i.e. replace some stuff...preserve...
    res = gen.Generate(pythonfile, namespacename, classname, group, brief, output_dir, dclspc)
    # Finally : delete the cogged folder
    shutil.rmtree(cogged_template_dir)
    return res

def GenerateDirectory(output_dir, pythonfile, cog_template_dir, author, namespacename, classname, group, brief, dclspc="") -> list:
    cog_template_dir = cog_template_dir.strip()
    if os.path.isfile(cog_template_dir):
        return GenerateFile(output_dir, pythonfile, cog_template_dir, author, namespacename, classname, group, brief, dclspc)
    if not os.path.isdir(cog_template_dir):
        print("Error : dir '" + cog_template_dir + "' does not exist. Aborting.")
        return []

    print("*************************************")
    print("******* CogGen (directory) **********")
    print("*************************************")
    print(" Template Dir : " + cog_template_dir)
    print(" Output Dir   : " + output_dir)
    print(" Python File  : " + pythonfile)
    print(" Executing in : " + os.path.realpath(__file__))
    print("*************************************")

    cogged_template_dir = os.path.join(cog_template_dir, "cogged")
    if not os.path.exists(cogged_template_dir):
        os.makedirs(cogged_template_dir)
    # copy the python file to the cogged directory, pre-cog...
    tmp_python_file = os.path.join(cogged_template_dir, os.path.basename(pythonfile))
    shutil.copy(pythonfile, tmp_python_file)
    # copy the cog templates to the cogged directory, pre-cog...and rename it as such. This is the first pass.
    files_to_cog = []
    for root, dirs, files in os.walk(cog_template_dir):
        if  "cogged" in dirs:
            dirs.remove("cogged")
        for file in files:
            file_to_cog = os.path.join(cogged_template_dir,os.path.basename(file))
            PreCogCopyFileAndInsertPythonImport(os.path.join(cog_template_dir,file),file_to_cog+".PreCog",os.path.splitext(os.path.basename(tmp_python_file))[0])
            files_to_cog.append(file_to_cog)

    # Create a generator
    gen = CCogGenerator(cogged_template_dir, output_dir, classname, None, author)
    # Create Cog Input
    with open(os.path.join(cogged_template_dir, "files.txt"), 'w') as writer:
        for f in files_to_cog:
            writer.write('"' + f + ".PreCog" + '" -o "' + f + '"\r\n')
    # Invoke Cog on intermediate dir
    c = Cog()
    c.callableMain(['cog', '-d', '@' + os.path.join(cogged_template_dir, "files.txt")])
    # clean up cog file and python file
    os.remove(os.path.join(cogged_template_dir, "files.txt"))
    os.remove(tmp_python_file)
    for f in files_to_cog:
        os.remove(f + ".PreCog")
    # Do rest...i.e. replace some stuff...preserve...
    res = gen.Generate(pythonfile, namespacename, classname, group, brief, output_dir, dclspc)
    # Finally : delete the cogged folder
    shutil.rmtree(cogged_template_dir)
    return res