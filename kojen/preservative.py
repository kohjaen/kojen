#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'eugene'

import os

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

    def __init__(self, outputfile_OR_dir):
        self._TAG_PREFIX_ = '{{{USER_'
        # {'FileName', {'Tag', [line1, line2,..., lineX]}}
        self.preserved_tags_per_file = {}
        self.preserved_tags_per_file_WAS_USED = {}

        # Does the input exist? (The input is the output of the code generator before it rewrites it)
        if os.path.exists(outputfile_OR_dir):
            if os.path.isdir(outputfile_OR_dir):
                # Its a directory
                files = os.listdir(outputfile_OR_dir)  # Is the input empty
                if not files:
                    print(outputfile_OR_dir + " is empty, nothing to preserve")
                else:
                    self.Collect(outputfile_OR_dir)
            elif os.path.isfile(outputfile_OR_dir):
                # Its a file
                self.CollectFile(outputfile_OR_dir)
        else:
            print(outputfile_OR_dir + " does not exist, nothing to preserve")

    def CollectFile(self, filename_and_path) -> None:
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
                print(
                    "<Warning> UnicodeDecodeError caught on " + filename_and_path + ". If this file is not part of the currently preserved files, then ignore.")
            except:
                print(
                    "<Warning> Unknown error caught on " + filename_and_path + ". If this file is not part of the currently preserved files, then ignore.")

    def Collect(self, directory) -> None:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.find('.h') > -1 or file.find('.cpp') > -1 or file.find('.py') > -1 or file.find('.cs') > -1:
                    self.CollectFile(os.path.join(root, file))

    # filenames_to_lines is an ordereddictionary {'filename', [line1, line2 ...] ...}
    def Emplace(self, filenames_to_lines, replace=False) -> None:
        """
        Will emplace previously cached code between tags into same tags found in 'filenames_to_lines'.
        - typically the tags in the 'output' have no code in them.

        If a tag is no longer in the 'output', a ".LostCode.txt" is created with the code that is no longer output.

        If 'replace' is false, and tags within 'filenames_to_lines' have code in them, behaviour is undefined, as
        two sets of preservations are merged.

        If 'replace' is true, and tags within 'filenames_to_lines' have code in them, tags that are
        previously cached will replace tags that are in 'filenames_to_lines'...essentially cloning them.

        @param filenames_to_lines: treated as an 'out' parameter. Code between tags loaded when creating this object
                                   will be placed here.
        @param replace: will replace any code between tags in 'filenames_to_lines' with code between tags loaded when
                        creating this object (and ignore what may be there).
        """
        for fn, lines in filenames_to_lines.items():
            for outputfile, tags in self.preserved_tags_per_file.items():
                if outputfile.find(fn) > -1:
                    new_lines = []
                    tag_found = False
                    tagline = ""
                    for line in lines:
                        cleaned_up_line = CleanUpLine(line)
                        if not replace or (replace and (not tag_found or (cleaned_up_line in tagline and self._TAG_PREFIX_ in cleaned_up_line))):
                            new_lines.append(line)
                        if not tag_found and (cleaned_up_line in tags):
                            tagline = line
                            tag_found = True
                            self.preserved_tags_per_file_WAS_USED[outputfile][cleaned_up_line] = True
                            for i in tags[cleaned_up_line]:
                                new_lines.append(i)
                        elif tag_found and (cleaned_up_line in tags):  # 2nd tag...
                            tag_found = False
                            tagline = ""
                    filenames_to_lines[fn] = new_lines

        for outputfile, tags in self.preserved_tags_per_file_WAS_USED.items():
            for tag, was_used in tags.items():
                if not was_used:
                    if len(self.preserved_tags_per_file[outputfile][tag]) > 0:
                        Lost_Code_TXT_filename = outputfile + ".LostCode.txt"
                        if not Lost_Code_TXT_filename in filenames_to_lines:
                            filenames_to_lines[Lost_Code_TXT_filename] = []
                        filenames_to_lines[Lost_Code_TXT_filename].append(outputfile + "\n")
                        filenames_to_lines[Lost_Code_TXT_filename].append(tag + "\n")
                        for i in self.preserved_tags_per_file[outputfile][tag]:
                            filenames_to_lines[Lost_Code_TXT_filename].append(i + "\n")
                        filenames_to_lines[Lost_Code_TXT_filename].append(tag + "\n")
                        filenames_to_lines[Lost_Code_TXT_filename].append("---------------------------------------------" + "\n")

    # Use this to set a custom code preservation tag prefix
    def SetPrefix(self, new_prefix):
        self._TAG_PREFIX_ = new_prefix

