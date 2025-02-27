#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'eugene'

from collections import OrderedDict
import os, shutil
import datetime
import sys
import time
from pathlib import Path
try:
	from .preservative import *
except (ModuleNotFoundError, ImportError) as e:
	from preservative import *

import os
import re

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

''' This forms the base for some sorts of code generation.

    Step 1) Load template files to memory
    Step 2) Search and replace passed-in tags in memory (including filenames).

'''

__TAG_DATETIME__           = '<<<DATETIME>>>'
__TAG_PLATFORM__           = '<<<PLATFORM>>>'
__TAG_EXTENDS__            = '<<<EXTENDS>>>'
__TAG_EXCLUDE__            = '<<<EXCLUDE>>>'
__TAG_FOR_BEGIN__          = "<<<FOR_BEGIN>>>"
__TAG_EACH__               = "<<<EACH>>>"
__TAG_EACH_CAMELCAPS__     = "<<<each>>>"
__TAG_FIRST__              = "<<<FIRST>>>"
__TAG_LAST__               = "<<<LAST>>>"
__TAG_FOR_END__            = "<<<FOR_END>>>"
__TAG_ABC__                = '<<<ALPH>>>'
__TAG_123__                = '<<<NUM>>>'
# User tag
__TAG_IF__                 = '<<<IF>>>'
__TAG_ELSEIF__             = '<<<ELSEIF>>>'
__TAG_ELSE__               = '<<<ELSE>>>'
__TAG_ENDIF__              = '<<<ENDIF>>>'


'''------------------------------------------------------------------------------------------------------'''


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def warning(text) -> None:
    print(Colors.WARNING + "Warning : " + text + Colors.ENDC)


def info(text) -> None:
    print(Colors.OKGREEN + "Info : " + text + Colors.ENDC)


def error(text) -> None:
    print(Colors.FAIL + "Error : " + text + Colors.ENDC)


'''------------------------------------------------------------------------------------------------------'''


class CCodeModel:
    def __init__(self):
        self.filenames_to_lines = OrderedDict()

    def Merge(self, codemodel) -> None:
        """
        Will merge the input codemodel with this.

        @param codemodel: a CCodeModel object
        """
        self.filenames_to_lines.update(codemodel.filenames_to_lines)


'''------------------------------------------------------------------------------------------------------'''


class SingleExpander:
    def __init__(self, tag):
        self.tag = tag

    def Expand(self, all_lines, expansion_func, *args):
        all_lines_expanded = []
        for line in all_lines:
            if hasSpecificTag(line, self.tag):
                expansion_func(all_lines_expanded, getWhitespace(line), *args)
            else:
                all_lines_expanded.append(line)
        return all_lines_expanded


class PairExpander:
    def __init__(self, start_tag, end_tag):
        self.start_tag = start_tag
        self.end_tag = end_tag

    def Expand(self,  all_lines, expansion_func, *args):
        all_lines_expanded = []
        within_tags        = False
        snippet_to_expand  = []
        param              = None
        for line in all_lines:
            begin       = hasSpecificTag(line, self.start_tag)
            end         = hasSpecificTag(line, self.end_tag)
            within_tags = begin or within_tags
            if begin and hasDefault(line):
                param = extractDefaultAndTag(line)[1]
            if not within_tags and not end:
                all_lines_expanded.append(line)
            if within_tags and end:
                if param:
                    expansion_func(snippet_to_expand, all_lines_expanded, *args, param)
                else:
                    expansion_func(snippet_to_expand, all_lines_expanded, *args)
                snippet_to_expand = []
                within_tags = False
            if within_tags and not begin:
                snippet_to_expand.append(line)
        return all_lines_expanded


'''------------------------------------------------------------------------------------------------------'''


def get_next_alphabet(alpha) -> int:
    alpha = alpha + 1
    if alpha == 123:
        alpha = 65
    if alpha == 91:
        alpha = 97
    return alpha


def reset_alphabet() -> int:
    return 97

def alphabet_to_string(alpha) -> str:
    return chr(alpha)


def even_space(a, nospaces=35) -> str:
    return a + (nospaces - len(a)) * " "


def camel_case(str) -> str:
    """A function to convert a string to CamelCase"""
    return str.title()


def camel_case_small(a) -> str:
    """A function to convert a string to camelCase"""
    if a:
        return a[0].lower() + a[1:]
    return ""

def snake_case(a) -> str:
    """A function to convert a string to snake_case."""
    # Replace hyphens and dots with underscores
    s = re.sub(r'[-.]+', '_', a)
    # Replace spaces with underscores
    s = s.replace(' ', '_')
    # Insert underscores before uppercase letters (only if preceded by a lowercase letter)
    s = re.sub(r'(?<=[a-z])(?=[A-Z])', '_', s)
    # Convert to lowercase
    s = s.lower()
    # Remove leading and trailing underscores
    s = s.strip('_')
    # Remove consecutive underscores
    s = re.sub(r'__+', '_', s)
    return s


def caps(a) -> str:
    return a.upper()

tag_pattern = re.compile(r'<<<([^<>]*)>>>')
def hasTag(a):
    b = tag_pattern.findall(a)
    return len(b) > 0

def hasSpecificTag(a, tag):
    # allows for defaults : BEWARE also allows for partial matching so order is important in such a case.
    res = hasTag(a)
    if res:
        res = tag.replace("<<<", "").replace(">>>", "") in a
    return res

def hasDefault(a, delimiter = "="):
    b = tag_pattern.findall(a)
    r = any(delimiter in string for string in b)
    return r

def extractDefaultAndTag(a, delimiter = "="):
    #default = a[a.find(delimiter, a.find("<<<")):a.rfind(">>>")].replace(delimiter,"", 1)
    #tag = a[a.find("<<<"):a.rfind(">>>")+len(">>>")]
    #return [tag, default]
    #matches = tag_pattern.findall(a)
    #if matches:
    #    # Get the last match to handle nested or multiple <<<...>>> patterns
    #    last_match = matches[-1]
    #    tag = f'<<<{last_match}>>>'
    #    parts = last_match.split(delimiter, 1)
    #    default_value = parts[1] if len(parts) > 1 else ''
    #    return [tag, default_value]
    #return ['', '']
    istart = -1
    iend = -1
    start = []
    end = []
    for i in range(len(a)):
        if a[i:i+3] == '<<<':
            istart = i
        else:
            if istart != -1:
                start.append(istart)
                istart = -1
        if a[i:i+3] == '>>>':
            if iend == -1:
                iend = i+3
                end.append(iend)
        else:
            iend = -1
    if start and end:
        outermost_tag = a[start[0]:end[-1]]
        inner_content = a[start[0]+3:end[-1]-3]
        parts = inner_content.split(delimiter, 1)
        default_value = parts[1] if len(parts) > 1 else ''
        return [outermost_tag, default_value]
    return ['', '']

def extractDefaultAndTagNamed(a, named):
    all = a.split(">>>")
    for b in all:
        if named in b:
            return extractDefaultAndTag(b + ">>>")
    raise Exception(named + " not found.")

def extractTagAndAandB(a, delimiter = "="):
    #[tag, default] = extractDefaultAndTag(a, delimiter)
    #r = default.split(delimiter)
    #A = None if len(r) < 1 else r[0]
    #B = None if len(r) < 2 else r[1]
    #return [tag, A, B]
    tag = a[a.find("<<<"):a.find(">>>") + len(">>>")]
    r = a[a.find("<<<") + len("<<<"):a.find(">>>")].split(delimiter)
    A = None if len(r) < 2 else r[1]
    B = None if len(r) < 3 else r[2]
    return [tag, A, B]

def replaceUserTags(line, dict_key_vals):
    is_defined = [key for key in dict_key_vals if key in line]
    if not is_defined and not hasDefault(line): # if its not defined (even None or '') then leave it.
        return line

    taganddefault    = extractDefaultAndTag(line)
    line             = removeDefault(line)#removeDefault2(line, taganddefault[1])
    taganddefault[0] = removeDefault(taganddefault[0])

    for tag, value in dict_key_vals.items():
        if value == None: # None is allowed ... it should be '' and not 'None'.
            value = ""
        line = line.replace(f'<<<{tag}>>>', str(value))
    if taganddefault[1].strip():
        line = line.replace(taganddefault[0], taganddefault[1])
    line = line.replace('<<<','').replace('>>>','')
    return line

def removeDefault2(a, default, delimiter = "="):
    return a.replace(default,"").replace(delimiter, "")

def removeDefault(a, delimiter = "="):
    matches = tag_pattern.findall(a)
    if matches:
        # Get the last match to handle nested or multiple <<<...>>> patterns
        last_match = matches[-1]
        parts = last_match.split(delimiter, 1)
        tag_without_default = parts[0]
        new_tag = f'<<<{tag_without_default}>>>'
        # Replace the old tag with the new tag in the input string
        return a.replace(f'<<<{last_match}>>>', new_tag)
    return a


def replaceDefault(a, b, delimiter = "="):
    default = a[a.find(delimiter, a.find("<<<")):a.rfind(">>>")]
    default = default.strip(delimiter)
    return a.replace(default, b)


def cleanTag(a):
    return a.replace("<<<","").replace(">>>","")


def getWhitespace(a):
    return a[0:a.find("<<<")]


def setFilenameReplace(dictionary_of_search_replace_tags_for_filename, desired_template_name):
    """
    'Template' in a filename can have the following forms, which will effect the output filename.
    NOTE: In Python, when you pass a dictionary (or any mutable object) to a function, it is passed by reference
    """
    dictionary_of_search_replace_tags_for_filename["TEMPLATE"] = desired_template_name              # As given
    dictionary_of_search_replace_tags_for_filename["_template"] = snake_case(desired_template_name) # Snakecase
    dictionary_of_search_replace_tags_for_filename["template"] = desired_template_name.lower()      # Lowercase
    dictionary_of_search_replace_tags_for_filename["temPlate"] = camel_case_small(desired_template_name)  # camelCapsSmall



'''------------------------------------------------------------------------------------------------------'''


class CGenerator:

    def __init__(self, inputfiledir, outputfiledir, language=None, author='Anonymous', group='', brief='',namespace_to_folders = False):
        self.input_template_file_dir = inputfiledir
        self.output_gen_file_dir = outputfiledir
        self.language = language
        self.author = author
        self.group = group
        self.brief = brief
        self.NAMESPACE_TO_GO_TO_OWN_FOLDER = namespace_to_folders
        # Does the input exist
        if not os.path.exists(inputfiledir):
            raise Exception("Directory '" + inputfiledir + "' does not exist.")
        else:
            files = None
            if os.path.isdir(inputfiledir):
                files = os.listdir(inputfiledir)
            if os.path.isfile(inputfiledir):
                files = inputfiledir
            # Is the input empty
            if not files:
                raise Exception("Directory '" + inputfiledir + "' is empty.")
            else:
                # Check the output dir
                if not os.path.exists(outputfiledir):
                    os.makedirs(outputfiledir)
                    info("Directory '" + outputfiledir + "' does not exist...created.")

    def generate_filenames_from_templates(self, file, dict_to_replace_filenames) -> str:
        for tag, desired_text in dict_to_replace_filenames.items():
            file = file.replace(tag, desired_text)
        return file

    ''' This will remove multiple newlines directly after each, leaving only 1'''
    def filter_multiple_newlines(self,list_of_lines_in_file):
        last = ''
        for i in range(len(list_of_lines_in_file)):
            was_filtered = False
            current = list_of_lines_in_file[i].replace(" ", "")
            if i > 0:
                if current == last and last == '\n':
                    list_of_lines_in_file[i] = ''
                    was_filtered = True
            if not was_filtered:
                last = current
        return list_of_lines_in_file


    def innerexpand_for_loop(self, to_expand, output, for_loop_param):

        def __process(csv_item_str, to_expand, output):
            alpha = reset_alphabet()
            cnt = 0
            first_processed = False
            last_processed = False
            first = None
            last = None
            items = csv_item_str.strip().lstrip(",").rstrip(",").split(',')
            to_add = []
            for i in items:
                for l in to_expand:
                    has_first = hasSpecificTag(l, __TAG_FIRST__)
                    has_last = hasSpecificTag(l, __TAG_LAST__)
                    if has_first and not first_processed:
                        first = l.replace(__TAG_FIRST__, items[0].strip())
                        first_processed = True
                    elif has_last and not last_processed:
                        last = l.replace(__TAG_LAST__, items[-1].strip())
                        last_processed = True
                    elif not has_first and not has_last:
                        to_add.append(l.replace(__TAG_EACH__, i.strip())
                                  .replace(__TAG_EACH_CAMELCAPS__, camel_case_small(i.strip()))
                                  .replace(__TAG_123__, str(cnt))
                                  .replace(__TAG_ABC__, alphabet_to_string(alpha)))
                cnt = cnt + 1
                alpha = get_next_alphabet(alpha)
            if first:
                to_add.insert(0, first)
            if last:
                to_add.append(last)
            output.extend(to_add)

        is_csv = for_loop_param.find(",") > -1
        is_numeric = for_loop_param.strip().isnumeric()
        if is_csv and not is_numeric:
            __process(for_loop_param, to_expand, output)
        elif not is_csv and is_numeric:
            number = int(for_loop_param.strip())
            new_for_loop_params = ""
            for i in range(number):
                new_for_loop_params += "_" + str(i) + "_" + ","
            __process(new_for_loop_params, to_expand, output)
        else:
            raise Exception("Unsupported FOR args.")


    def processExtends(self, path_to_parent_folder, inner_template_file, ignore_lines_with, ignore_lines_between):
        result = []

        templateFilePath = Path(inner_template_file)
        if not os.path.isabs(templateFilePath):
            templateFilePath = path_to_parent_folder / templateFilePath
        if not os.path.isfile(templateFilePath):
            warning("path '" + inner_template_file + "' does not exist. Ignoring.")
        else:
            with open(templateFilePath) as f:
                extended_lines = []
                isBetween = False
                isBetween_end = ''
                for l in f:
                    if not isBetween:
                        for start, end in ignore_lines_between:
                            if start in l:
                                isBetween = True
                                isBetween_end = end
                                break
                    if not isBetween:
                        if hasSpecificTag(l, __TAG_EXTENDS__): # nested extension
                            [unused, ext_rel_filepath] = extractDefaultAndTag(l)
                            if ext_rel_filepath:
                                nested_ext = self.processExtends(os.path.dirname(templateFilePath),ext_rel_filepath,ignore_lines_with, ignore_lines_between)
                                extended_lines.extend(nested_ext)
                        else:
                            extended_lines.append(l)
                    if isBetween:
                        if isBetween_end in l:
                            isBetween = False
                for l in extended_lines:
                    if not any(excl in l for excl in ignore_lines_with):
                        result.append(l)
        return result

    def processLine(self, dict_to_replace_lines, lines, line):
        for tag, desired_text in dict_to_replace_lines.items():
            desired_text = self.preserve_leading_tagwhitespace_in_multiline_searchandreplace(line, tag, desired_text)
            line = line.replace(tag, desired_text)
        # split multi-line-in-one-string to multi line. Code preservation does not work otherwise.
        if line.count('\n') > 1:
            lines_in_line = line.rstrip('\n').split('\n')
            for l in lines_in_line:
                lines.append(l + '\n')  # could do
        else:
            lines.append(line)

    def loadtemplates_firstfiltering_FILE(self, filepath, dict_to_replace_lines, dict_to_replace_filenames, filter_files_containing_in_name = "") -> CCodeModel:
        result = CCodeModel()
        if os.path.exists(filepath):
            file_without_path = os.path.basename(filepath)
            with open(filepath) as f:
                lines = []
                extended_filenames = []
                ignore_lines_with = []
                ignore_lines_between = []

                # Get all exclude tags...no matter what order they exist in the file.
                for line in f:
                    if hasSpecificTag(line, __TAG_EXCLUDE__):
                        [unused, exclude_line_with] = extractDefaultAndTag(line)
                        if exclude_line_with:
                            start_begin = exclude_line_with.split(",")
                            if len(start_begin) < 2:
                                ignore_lines_with.append(exclude_line_with)
                            elif len(start_begin) == 2:
                                ignore_lines_between.append(start_begin)
                            else:
                                warnings.warn("Tags '" + exclude_line_with + "' is not supported. Ignoring.")
                f.seek(0)
                for line in f:
                    if hasSpecificTag(line, __TAG_EXTENDS__):
                        [unused, ext_rel_filepath] = extractDefaultAndTag(line)
                        if ext_rel_filepath:
                            extension = self.processExtends(os.path.dirname(filepath), ext_rel_filepath, ignore_lines_with, ignore_lines_between)
                            for ex_l in extension:
                                # Replace the key:value pairs per line...
                                self.processLine(dict_to_replace_lines, lines, ex_l)
                            if extension:
                                # Replace the key:value pairs per filename...
                                self.processLine(dict_to_replace_filenames, extended_filenames, os.path.basename(ext_rel_filepath))
                    elif hasSpecificTag(line, __TAG_EXCLUDE__):
                        pass
                    else:
                        # Replace the key:value pairs per line...
                        self.processLine(dict_to_replace_lines, lines, line)

                # Replace any template names (extended) in the files by making them empty
                for i, l in enumerate(lines):
                    for ext_fn in extended_filenames:
                        if l.find(ext_fn) > -1:
                            lines[i] = ''

                # Replace the key:value pairs per filename...
                for tag, desired_text in dict_to_replace_filenames.items():
                    file_without_path = file_without_path.replace(tag, desired_text)
                # Remove multiple newlines
                lines = self.filter_multiple_newlines(lines)
                result.filenames_to_lines[file_without_path] = lines

                # would be great if user-tags and for loop processing could happen here
                # but that has problems with user-tags-without defaults
        return result

    def loadtemplates_firstfiltering(self, dict_to_replace_lines, dict_to_replace_filenames, filter_files_containing_in_name = ""):
        """
        Load Template and do 1st round of filtering. The filtering will replace the TAG

        @param dict_to_replace_lines: a dictionary of keys:values to replace per line
        @param dict_to_replace_filenames:  a dictionary of keys:values to replace per templatefilename. This includes extension.
        @param filter_files_containing_in_name:  fill process only files that contain this text in the name...or "" for all.
        @return: CCodeModel, a dictionary -> {filename,[lines]}
        """
        template_file_found = False
        result = CCodeModel()
        CWD = self.input_template_file_dir
        dict_to_replace_lines[__TAG_DATETIME__] = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        dict_to_replace_lines[__TAG_PLATFORM__] = sys.platform + ' python ' + sys.version
        if os.path.isfile(self.input_template_file_dir):
            template_file_found = True
            cm = self.loadtemplates_firstfiltering_FILE(self.input_template_file_dir, dict_to_replace_lines, dict_to_replace_filenames, filter_files_containing_in_name)
            result.Merge(cm)
        else:
            for root, dirs, files in os.walk(CWD):
                for file in files:
                    if (file.lower().find(filter_files_containing_in_name.lower()) > -1 or not filter_files_containing_in_name.strip()) and not file.lower().find(".removed") > -1 :
                        template_file_found = True
                        cm = self.loadtemplates_firstfiltering_FILE(os.path.join(root, file), dict_to_replace_lines, dict_to_replace_filenames, filter_files_containing_in_name)
                        result.Merge(cm)

            if not template_file_found:
                raise Exception("Directory '" + self.input_template_file_dir + "' contains no templates.")

        return result

    def preserve_leading_tagwhitespace_in_multiline_searchandreplace(self, line, tag, desired_text):
        """
        For the case where the 'desired_text' that should replace the 'tag' in the 'line', if it is a multi-line
        replace, it will keep the leading spaces across all lines...otherwise simply returns the input desired_text
        @param line:
        @param tag:
        @param desired_text:
        @return:
        """
        if line.find(tag) != -1:
            desired_text_as_lines = desired_text.rstrip('\n').split('\n')
            if len(desired_text_as_lines) > 1:
                leading_spaces = (len(line) - len(line.lstrip(' '))) * " "
                desired_text = ""
                for d in desired_text_as_lines:
                    if not desired_text:
                        desired_text = d + "\n"
                    else:
                        desired_text = desired_text + leading_spaces + d + "\n"
                desired_text = desired_text.rstrip('\n')

        return desired_text

    def createoutput(self, filenames_to_lines) -> list:
        for f in filenames_to_lines:
            print("+++++++++ ", f)
            filename = os.path.join(self.output_gen_file_dir, f)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as writer:
                for line in filenames_to_lines[f]:
                    line = line.replace('\t',"    ") # Last filter! Convert tabs to 4 spaces...
                    writer.write(line)
        return list(filenames_to_lines.keys())



    def do_user_tags(self, codemodel, dict_key_vals, delimiter="="):
        # get defaults : for loop processing introduces multiple uses of tags across multiple files.
        # first is the law!
        defaults_in_files_FOR = {}
        for fn, lines in codemodel.filenames_to_lines.items():
            for line in lines:
                has_tag = hasTag(line)
                has_for = hasSpecificTag(line, __TAG_FOR_BEGIN__)
                if has_tag and has_for:
                    fortaganddefault = extractDefaultAndTag(line)
                    if fortaganddefault[1].find(delimiter) > -1:
                        hack = cleanTag(__TAG_FOR_BEGIN__)
                        hack = fortaganddefault[0].replace(hack + delimiter,"")
                        if hasDefault(hack):
                            taganddefault = extractDefaultAndTag(hack)
                            key = cleanTag(removeDefault(taganddefault[0]))
                            if not taganddefault[1] in defaults_in_files_FOR:
                                defaults_in_files_FOR[key] = taganddefault[1]

        for fn, lines in codemodel.filenames_to_lines.items():
            new_lines = []

            is_processing_if = False
            can_process_else = True
            can_append_line = True

            # this should be called last, so at this point any tags should be user defined.
            for line in lines:
                if is_processing_if:
                    has_elseif       = hasSpecificTag(line, __TAG_ELSEIF__)
                    has_else         = hasSpecificTag(line, __TAG_ELSE__) and not has_elseif
                    has_endif        = hasSpecificTag(line, __TAG_ENDIF__)
                    if not has_elseif and not has_else and not has_endif:
                        line = replaceUserTags(line, dict_key_vals) # still processing if ...
                    if has_elseif and not has_else and not has_endif:
                        [unused, user_tag] = extractDefaultAndTag(line, " ")
                        can_append_line = user_tag in dict_key_vals
                        can_process_else = not can_append_line and can_process_else # -> if a usertag is not found in an if.
                        continue
                    elif not has_elseif and has_else and not has_endif:
                        can_append_line = can_process_else
                        continue
                    elif not has_elseif and not has_else and has_endif: # End ...
                        is_processing_if = False
                        can_append_line = True
                        can_process_else = True
                        continue
                else:
                    can_append_line = True
                    has_tag      = hasTag(line)
                    has_for      = hasSpecificTag(line, __TAG_FOR_BEGIN__)
                    has_if       = hasSpecificTag(line, __TAG_IF__)
                    if has_tag and not has_for and not has_if:
                        line = replaceUserTags(line, dict_key_vals)
                    elif has_tag and has_for and not has_if:
                        taganddefault = extractDefaultAndTag(line)
                        key = cleanTag(removeDefault("<<<" + taganddefault[1] + ">>>"))
                        if key in dict_key_vals:
                            line = replaceDefault(line, dict_key_vals[key])
                        elif key in defaults_in_files_FOR:
                            line = replaceDefault(line, defaults_in_files_FOR[key])
                        else:
                            line = "//POO"
                    elif has_tag and not has_for and has_if:
                        is_processing_if = True
                        # get the expression in the IF ... delimiter is ' '.
                        [unused, user_tag] = extractDefaultAndTag(line, " ")
                        can_append_line = user_tag in dict_key_vals
                        can_process_else = not can_append_line and can_process_else# -> if a usertag is not found in an if.
                        continue

                if can_append_line:
                    new_lines.append(line)
            # replace
            codemodel.filenames_to_lines[fn] = new_lines


    def do_for(self, codemodel):
        for fn, lines in codemodel.filenames_to_lines.items():
            new_lines = PairExpander(__TAG_FOR_BEGIN__, __TAG_FOR_END__).Expand(lines, self.innerexpand_for_loop)
            # replace
            codemodel.filenames_to_lines[fn] = new_lines

    '''Will use the base-class configured 'output directory' if no preserve directory is passed in. '''
    def preserve_usercode_in_files(self, codemodel, preserve_dir = ""):
        copy_filename_to_lines = codemodel.filenames_to_lines.copy() # prevent mutation whilst iteration.
        for filename_nopath in copy_filename_to_lines:
            file_to_preserve = ""
            if preserve_dir == "":
                file_to_preserve = os.path.join(self.output_gen_file_dir, filename_nopath)
            else:
                file_to_preserve = os.path.join(preserve_dir, filename_nopath)
            preservation = Preservative(file_to_preserve)
            preservation.Emplace(codemodel.filenames_to_lines)
'''------------------------------------------------------------------------------------------------------'''


def FileCopyUtil(dir_from, dir_to, list_of_filenames):
    """
    Will copy each file from list_of_filenames in dir_from to dir_to.
    Will create dir_to (even if its a tree) if it does not exist.

    @param dir_from: The directory from, where the list of files reside.
    @param dir_to: The directory the list of files should be copied to.
    @param list_of_filenames: The list [] of filenames to be copied.
    """
    try:
        os.makedirs(dir_to, exist_ok=True)
        for filename in list_of_filenames:
            try:
                shutil.copy(os.path.join(dir_from, filename), os.path.join(dir_to, filename))
            except OSError:
                warning("Copy of the file %s failed" % os.path.join(dir_from, filename))
    except OSError:
        warning("Creation of the directory %s failed" % dir_to)

def FilePreservationSyncUtil(file_from, file_to) -> None:
    """
    Will synchronize code in preservation tags from 'file_from' to 'file_to',
    if these tags exist in 'file_to'.

    Tags that exist exclusively in 'file_to' will remain untouched if they do not
    exist in 'file_from'.
    """
    if not os.path.isfile(file_from):
        error("File '" + file_from + "' does not exist. Aborting.")
        return
    if not os.path.isfile(file_to):
        error("File '" + file_to + "' does not exist. Aborting.")
        return

    print("*************************************")
    print("******* Sync (file)  ****************")
    print("*************************************")
    print(" From file    : " + file_from)
    print(" To file      : " + file_to)
    print(" Executing in : " + os.path.realpath(__file__))
    print("*************************************")

    bg = CGenerator(os.path.dirname(file_from), os.path.dirname(file_to))
    cm = bg.loadtemplates_firstfiltering_FILE(file_to, {}, {})
    p  = Preservative(file_from)
    p.preserved_tags_per_file[file_to]          = p.preserved_tags_per_file.pop(file_from)
    p.preserved_tags_per_file_WAS_USED[file_to] = p.preserved_tags_per_file_WAS_USED.pop(file_from)
    p.Emplace(cm.filenames_to_lines, True)
    bg.createoutput(cm.filenames_to_lines)
