#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'eugene'

from collections import OrderedDict
import os, shutil
import datetime
import sys
import time
from pathlib import Path
from typing import List

try:
    from .kojentypes import Interface
except (ModuleNotFoundError, ImportError) as e:
    from kojen.kojentypes import Interface
try:
	from .preservative import *
except (ModuleNotFoundError, ImportError) as e:
	from preservative import *

try:
	from .boolean import parse_tag_expression, eval_parsed_expr
except (ModuleNotFoundError, ImportError) as e:
	from boolean import parse_tag_expression, eval_parsed_expr

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


def extract_block(lines, start_tag, end_tag):
    """
    Extracts sublists between the first occurrence of each begin/end tag,
    matching by substring (not exact equality).

    Returns:
      list of lines between the first occurrence of start_tag and end_tag
    """
    start_idx = None
    for i, s in enumerate(lines):
        if start_tag in s:
            start_idx = i
            break
    if start_idx is None:
        return []

    end_idx = None
    for j in range(start_idx, len(lines)):
        if end_tag in lines[j]:
            end_idx = j
            break
    if end_idx is None:
        end_idx = len(lines) - 1

    return lines[start_idx:end_idx + 1]


def replace_block(lines, new_block, start_tag, end_tag):
    """
    Replaces the first block in `lines` that starts with a line containing `start_tag`
    and ends with a line containing `end_tag`.
    The replacement includes the begin/end tag lines from the original.
    """
    # find start
    start_idx = None
    for i, s in enumerate(lines):
        if start_tag in s:
            start_idx = i
            break
    if start_idx is None:
        return lines  # nothing to replace

    # find end (after start)
    end_idx = None
    for j in range(start_idx, len(lines)):
        if end_tag in lines[j]:
            end_idx = j
            break
    if end_idx is None:
        end_idx = start_idx  # or return lines; depends on your preference

    # splice replace
    return lines[:start_idx] + new_block + lines[end_idx + 1:]


def is_deeply_empty(data):
    """Returns True if the container or all its nested elements are empty."""
    if isinstance(data, dict):
        # An empty dict is empty; otherwise check if all its values are deeply empty
        return not data or all(is_deeply_empty(v) for v in data.values())
    if isinstance(data, (list, tuple, set)):
        # An empty list is empty; otherwise check if all its items are deeply empty
        return not data or all(is_deeply_empty(item) for item in data)

    # If it's a primitive value (like an int, string, etc.), it is NOT empty
    return False


'''------------------------------------------------------------------------------------------------------'''

class IfProcessor:
    def __init__(self, start_tag = __TAG_IF__) -> None:
        self.start_tag = start_tag

    def Expand(self, all_lines, if_test_function, not_processing_if_function, processing_if_function, *args) -> List[str]:
        if self.start_tag == __TAG_IF__:
            return self.Expand_SingleConditionIf(all_lines, if_test_function, not_processing_if_function, processing_if_function, *args)
        else:
            return self.Expand_PyAttr(all_lines, if_test_function, not_processing_if_function, processing_if_function, *args)

    def Expand_PyAttr(self, all_lines, if_test_function, not_processing_if_function, processing_if_function, *args) -> List[str]:
        # No nesting ... will process all that match ... so if/else if will all get processed if conditions passed. Used for PyAttr.
        new_lines = []
        is_processing_if = False
        can_process_else = True
        can_append_line = True
        for line in all_lines:
            if is_processing_if:
                has_elseif       = hasSpecificTag(line, __TAG_ELSEIF__)
                has_else         = hasSpecificTag(line, __TAG_ELSE__) and not has_elseif
                has_endif        = hasSpecificTag(line, __TAG_ENDIF__)
                if not has_elseif and not has_else and not has_endif:
                    line = processing_if_function(line, *args) # still processing if ...
                if has_elseif and not has_else and not has_endif:
                    conditions = parse_tag_expression(line, prefix=cleanTag(__TAG_ELSEIF__))
                    try:
                        can_append_line = eval_parsed_expr(conditions, if_test_function,*args)
                    except ValueError as e:
                        print(f"Error evaluating condition in line: {line}. Error: {e}")
                        can_append_line = False
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
                has_if = hasSpecificIfTag(line, self.start_tag)
                if has_if:
                    is_processing_if = True
                    conditions = parse_tag_expression(line, prefix=cleanTag(self.start_tag))
                    try:
                        can_append_line = eval_parsed_expr(conditions, if_test_function,*args)
                    except ValueError as e:
                        print(f"Error evaluating condition in line: {line}. Error: {e}")
                        can_append_line = False
                    can_process_else = not can_append_line and can_process_else# -> if a usertag is not found in an if.
                    continue
                else:
                    line = not_processing_if_function(line, *args)
            if can_append_line:
                new_lines.append(line)
        return new_lines

    def Expand_SingleConditionIf(self, all_lines, if_test_function, not_processing_if_function, processing_if_function, *args) -> List[str]:
        # Allows nesting of if/else if/else ... and, like conditional operator in a programming language, will only proces one.
        new_lines = []
        is_processing_conditional_operator = []
        can_process_else = []
        has_elseif = []
        has_else = []
        has_endif = []
        if_condition = []
        elseif_condition = []
        can_append_line = [True]

        def can_append_line_all():
            return bool(can_append_line) and all(can_append_line)

        for line in all_lines:
            if is_processing_conditional_operator and is_processing_conditional_operator[-1]:
                has_elseif[-1]   = hasSpecificTag(line, __TAG_ELSEIF__)
                has_else[-1]     = hasSpecificTag(line, __TAG_ELSE__) and not has_elseif[-1]
                has_endif[-1]    = hasSpecificTag(line, __TAG_ENDIF__)
                has_nested_if    = hasSpecificIfTag(line, self.start_tag) and not has_endif[-1] and not has_elseif[-1]

                if has_nested_if:
                    is_processing_conditional_operator.append(True)
                    has_elseif.append(False)
                    has_else.append(False)
                    has_endif.append(False)
                    conditions = parse_tag_expression(line, prefix=cleanTag(self.start_tag))
                    try:
                        if_condition.append(eval_parsed_expr(conditions, if_test_function,*args))
                    except ValueError as e:
                        print(f"Error evaluating condition in line: {line}. Error: {e}")
                        if_condition.append(False)
                    elseif_condition.append([False]) # can be multiple
                    can_append_line.append(if_condition[-1])
                    can_process_else.append(not can_append_line_all())
                    continue
                else:
                    if not has_elseif[-1] and not has_else[-1] and not has_endif[-1]:
                        line = processing_if_function(line, *args) # still processing if ...
                    elif has_elseif[-1] and not has_else[-1] and not has_endif[-1]:
                        conditions = parse_tag_expression(line, prefix=cleanTag(__TAG_ELSEIF__))
                        try:
                            passed = eval_parsed_expr(conditions, if_test_function,*args)
                        except ValueError as e:
                            print(f"Error evaluating condition in line: {line}. Error: {e}")
                            passed = False
                        can_append_line[-1] = passed and not any(elseif_condition[-1]) and not if_condition[-1]
                        elseif_condition[-1].append(passed)
                        continue
                    elif not has_elseif[-1] and has_else[-1] and not has_endif[-1]:
                        can_append_line[-1] = not any(elseif_condition[-1]) and not if_condition[-1]
                        continue
                    elif not has_elseif[-1] and not has_else[-1] and has_endif[-1]: # End ...
                        is_processing_conditional_operator.pop()
                        can_process_else.pop()
                        can_append_line.pop()
                        has_elseif.pop()
                        has_else.pop()
                        has_endif.pop()
                        elseif_condition.pop()
                        if_condition.pop()
                        continue
            else:
                has_if = hasSpecificIfTag(line, self.start_tag)
                if has_if:
                    is_processing_conditional_operator.append(True)
                    has_elseif.append(False)
                    has_else.append(False)
                    has_endif.append(False)
                    conditions = parse_tag_expression(line, prefix=cleanTag(self.start_tag))
                    try:
                        if_condition.append(eval_parsed_expr(conditions, if_test_function,*args))
                    except ValueError as e:
                        print(f"Error evaluating condition in line: {line}. Error: {e}")
                        if_condition.append(False)
                    elseif_condition.append([False]) # can be multiple
                    can_append_line.append(if_condition[-1])
                    can_process_else.append(not can_append_line_all())
                    continue
                else:
                    line = not_processing_if_function(line, *args)
            if can_append_line_all():
                new_lines.append(line)
        return new_lines


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

tag_pattern = re.compile(r'<<<(.*?)>>>')

def getAllTags(s: str) -> List[str]:
    return re.findall(r'(<<<.*?>>>)', s, flags=re.DOTALL)

def hasTag(a) -> bool:
    b = getAllTags(a)
    return len(b) > 0

def hasSpecificTag(a, tag) -> bool:
    # allows for defaults : BEWARE also allows for partial matching so order is important in such a case.
    res = hasTag(a)
    if res:
        res = cleanTag(tag) in a
    return res

def hasSpecificIfTag(a, tag) -> bool:
    # allows for defaults : BEWARE also allows for partial matching so order is important in such a case.
    res = hasTag(a)
    if res:
        res = tag.replace(">>>","") in a
    return res

def hasDefault(a, delimiter = "=") -> bool:
    b = tag_pattern.findall(a)
    r = any(delimiter in string for string in b)
    return r

def extractDefaultAndTag(a, delimiter = "=") -> List[str]:
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
        return [outermost_tag, default_value.strip()]
    return ['', '']

def extractDefaultAndTagNamed(a, named) -> List[str]:
    all = a.split(">>>")
    for b in all:
        if named in b:
            return extractDefaultAndTag(b + ">>>")
    raise Exception(named + " not found.")

def convert_empty_to_none(s):
    return None if s.strip() == "" else s

def extractTagAndAandBandC(a, default_tag, delimiter = "=") -> List[str]:
    t = default_tag.replace(">>>", "")
    pos = a.find(t)
    if pos != -1:
        tag = a[pos:a.find(">>>", pos) + len(">>>")]
        r = a[pos + len("<<<"):a.find(">>>", pos)].split(delimiter)
        A = None if len(r) < 2 else convert_empty_to_none(r[1])
        B = None if len(r) < 3 else convert_empty_to_none(r[2])
        C = None if len(r) < 4 else convert_empty_to_none(r[3])
        return [tag, A, B, C]
    return [default_tag, None, None, None]

def replaceUserTags(line, dict_key_vals) -> str:
    is_defined = [key for key in dict_key_vals if key in line]
    if not is_defined and not hasDefault(line): # if its not defined (even None or '') then leave it.
        return line

    all_tags = getAllTags(line)

    for a_tag in all_tags:
        taganddefault    = extractDefaultAndTag(a_tag)
        line             = removeDefault(line)
        taganddefault[0] = removeDefault(taganddefault[0])

        for u_tag, value in dict_key_vals.items():
            if value == None: # None is allowed ... it should be '' and not 'None'.
                value = ""
            line = line.replace(f'<<<{u_tag}>>>', str(value))
        if taganddefault[1].strip():
            line = line.replace(taganddefault[0], taganddefault[1])

    line = cleanTag(line)
    return line

def removeDefault2(a, default, delimiter = "=") -> str:
    return a.replace(default,"").replace(delimiter, "")

def removeDefault(a, delimiter = "=") -> str:
    matches = tag_pattern.findall(a)
    for m in matches:
        parts = m.split(delimiter, 1)
        tag_without_default = parts[0]
        new_tag = f'<<<{tag_without_default}>>>'
        # Replace the old tag with the new tag in the input string
        return a.replace(f'<<<{m}>>>', new_tag)
    return a


def replaceDefault(a, b, delimiter = "=") -> str:
    default = a[a.find(delimiter, a.find("<<<")):a.rfind(">>>")]
    default = default.strip(delimiter)
    return a.replace(default, b)


def cleanTag(a) -> str:
    return a.replace("<<<","").replace(">>>","")


def getWhitespace(a) -> str:
    return a[0:a.find("<<<")]


def setFilenameReplace(dictionary_of_search_replace_tags_for_filename, desired_template_name) -> None:
    """
    'Template' in a filename can have the following forms, which will effect the output filename.
    NOTE: In Python, when you pass a dictionary (or any mutable object) to a function, it is passed by reference
    """
    dictionary_of_search_replace_tags_for_filename["TEMPLATE"] = desired_template_name              # As given
    dictionary_of_search_replace_tags_for_filename["_template"] = snake_case(desired_template_name) # Snakecase
    dictionary_of_search_replace_tags_for_filename["template"] = desired_template_name.lower()      # Lowercase
    dictionary_of_search_replace_tags_for_filename["temPlate"] = camel_case_small(desired_template_name)  # camelCapsSmall



'''------------------------------------------------------------------------------------------------------'''

def getNumericDefault(lines_to_expand) -> int:
    """ Utility function to extract the desired start numeric value for the FIRST <<<NUM>>> tag, that
        will be incremented. If not found, will return 0.
    """
    for l in lines_to_expand:
        if hasSpecificTag(l, __TAG_123__):
            res = extractDefaultAndTagNamed(l, cleanTag(__TAG_123__))
            if res[1] and res[1].strip().isnumeric():
                return int(res[1].strip())
    return 0


class CGenerator:

    def __init__(self, inputfiledir, outputfiledir, events_interface:Interface = None, language=None, author='Anonymous', group='', brief='',namespace_to_folders = False):
        self.input_template_file_dir = inputfiledir
        self.output_gen_file_dir = outputfiledir
        self.language = language
        self.author = author
        self.group = group
        self.brief = brief
        self.events_interface = events_interface
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
    def filter_multiple_newlines(self,list_of_lines_in_file) -> List[str]:
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


    def innerexpand_for_loop(self, to_expand, output, for_loop_param) -> None:

        def __process(csv_item_str, to_expand, output):
            alpha = reset_alphabet()
            first_processed = False
            last_processed = False
            first = None
            last = None
            items = csv_item_str.strip().lstrip(",").rstrip(",").split(',')
            to_add = []
            cnt = getNumericDefault(to_expand)
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
                        l = l.replace(__TAG_EACH__, i.strip()) \
                            .replace(__TAG_EACH_CAMELCAPS__, camel_case_small(i.strip())) \
                            .replace(__TAG_ABC__, alphabet_to_string(alpha))
                        if hasSpecificTag(l,__TAG_123__):
                            line_member = extractDefaultAndTagNamed(l, cleanTag(__TAG_123__))
                            l = l.replace(line_member[0], str(cnt))
                        to_add.append(l)
                cnt += 1
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


    def processExtends(self, path_to_parent_folder, inner_template_file, ignore_lines_with, ignore_lines_between) -> List[str]:
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

    def processLine(self, dict_to_replace_lines, lines, line) -> None:
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

    def loadtemplates_firstfiltering(self, dict_to_replace_lines, dict_to_replace_filenames, filter_files_containing_in_name = "") -> CCodeModel:
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

    def preserve_leading_tagwhitespace_in_multiline_searchandreplace(self, line, tag, desired_text) -> str:
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



    def do_user_tags(self, codemodel, dict_key_vals, delimiter="=") -> None:

        def if_test_function(user_tag) -> bool:
            return user_tag in dict_key_vals

        def not_processing_if_function(line) -> str:
            has_tag      = hasTag(line)
            has_for      = hasSpecificTag(line, __TAG_FOR_BEGIN__)
            if has_tag and not has_for:
                line = replaceUserTags(line, dict_key_vals)
            elif has_tag and has_for:
                taganddefault = extractDefaultAndTag(line)
                key = cleanTag(removeDefault("<<<" + taganddefault[1] + ">>>"))
                if key in dict_key_vals:
                    line = replaceDefault(line, dict_key_vals[key])
                elif key in defaults_in_files_FOR:
                    line = replaceDefault(line, defaults_in_files_FOR[key])
                else:
                    line = "//POO"
            return line

        def processing_if_function(line) -> str:
            return replaceUserTags(line, dict_key_vals)

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
            new_lines = IfProcessor().Expand(lines, if_test_function, not_processing_if_function, processing_if_function)
            # replace
            codemodel.filenames_to_lines[fn] = new_lines



    def do_for(self, codemodel) -> None:
        for fn, lines in codemodel.filenames_to_lines.items():
            new_lines = PairExpander(__TAG_FOR_BEGIN__, __TAG_FOR_END__).Expand(lines, self.innerexpand_for_loop)
            # replace
            codemodel.filenames_to_lines[fn] = new_lines

    '''Will use the base-class configured 'output directory' if no preserve directory is passed in. '''
    def preserve_usercode_in_files(self, codemodel, preserve_dir = "") -> None:
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


def FileCopyUtil(dir_from, dir_to, list_of_filenames) -> None:
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
