#!/usr/bin/env python
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
Step 1) Load template files to memory
Step 2) Search and replace these tags in memory (including filenames).

<<<CLASSNAME>>>
<<<AUTHOR>>>
<<<NESTED_NAMESPACE_BEGIN>>>
<<<NESTED_NAMESPACE_END>>>
!!! No need ... already doing this in other code generation... <<<CLASSTYPE>>> -> class, struct, enum
<<<DLL_EXPORT>>>
<<<CLASS_INHERITENCE_HIERARCHY>>>
<<<NOT_FORWARD_DECLARABLE_HEADER_INCLUDES>>> -> all the members that are not primitives and not pointers and can not be forward declared in an H file
<<<FORWARD_DECLARABLE_HEADER_INCLUDES>>> -> all the members that are not primitives and are pointers and can be forward declared in an H file, but must be included in source file
<<<FORWARD_DECLARATIONS>>> -> all the members that are not primitives and that are pointers and thus can be forward declared.
<<<CLASS_DOCUMENTATION>>>

Step 3) Search for the following pairs of tags replacing each tag with the all the parameters according to the UML model.

<<<PUBLIC_ATTRIBUTES_DECLARE>>>
<<<PROTECTED_ATTRIBUTES_DECLARE>>>
<<<PRIVATE_ATTRIBUTES_DECLARE>>>
<<<STATIC_ATTRIBUTES_DECLARE>>>

<<<ATTRIBUTES_GETTER_SETTER_DECLARE>>>
<<<ATTRIBUTES_GETTER_SETTER_IMPLEMENTATION>>>

<<<PUBLIC_ASSOCIATIONS_DECLARE>>>
<<<PROTECTED_ASSOCIATIONS_DECLARE>>>
<<<PRIVATE_ASSOCIATIONS_DECLARE>>>
<<<STATIC_ASSOCIATIONS_DECLARE>>>

<<<PUBLIC_OPERATIONS_DECLARE>>>
<<<PROTECTED_OPERATIONS_DECLARE>>>
<<<PRIVATE_OPERATIONS_DECLARE>>>

<<<OPERATIONS_IMPLEMENTATION>>>

'''

try:
    from cgen import CBASEGenerator, CCodeModel, alpha, __getnextalphabet__, __resetalphabet__, even_space
except (ModuleNotFoundError, ImportError) as e:
    from .cgen import CBASEGenerator, CCodeModel, alpha, __getnextalphabet__, __resetalphabet__, even_space

try:
    from vppclassdiagram import  ExtractClassDiagram, ExtractAllClassDiagrams, ClassDiagram, Class, ClassOperation, ClassAttribute, Package, Association, Inheritance
except  (ModuleNotFoundError, ImportError) as e:
    from .vppclassdiagram import ExtractClassDiagram, ExtractAllClassDiagrams, ClassDiagram, Class, ClassOperation, ClassAttribute, Package, Association, Inheritance

try:
    from LanguageCPP import LanguageCPP
except  (ModuleNotFoundError, ImportError) as e:
    from .LanguageCPP import LanguageCPP

try:
    from LanguageCsharp import LanguageCsharp
except  (ModuleNotFoundError, ImportError) as e:
    from .LanguageCsharp import LanguageCsharp

try:
    from preservative import *
except (ModuleNotFoundError, ImportError) as e:
    from .preservative import *

import os

class CUMLGenerator(CBASEGenerator):

    def __init__(self, outputfiledir, language=None, author='Anonymous', group='', brief='', namespace_to_folders = False, templatefiledir="", vp_classdiagramname=""):
        if not templatefiledir.strip():
            if "LanguageCsharp" in str(type(language)):
                templatefiledir = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.join("classdiagram_templates", "C#"))
            elif "LanguageCPP" in str(type(language)):
                templatefiledir = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.join("classdiagram_templates", "CPP"))
        CBASEGenerator.__init__(self, templatefiledir, outputfiledir, language, author, group, brief, namespace_to_folders)
        self.classdiagramname = vp_classdiagramname

    # Load Template and do 1st round of filtering.
    # Returns {filename,[lines]}
    def __loadtemplates_firstfiltering__(self, classdiagram, declspc):
        """
        See baseclass implementation. This just prepares the dictionary of things to replace
        for this type of codegeneration.

        @param smmodel:
        @return: cgen.CCodeModel, a dictionary -> {filename,[lines]}
        """
        if len(declspc.strip()) > 0:
            declspc = declspc.strip() + " "

        if isinstance(classdiagram, ClassDiagram):
            result = CCodeModel()
            for class_uid, classobj in classdiagram.classes.items():
                # CLASS -> not enum, struct, autogen(coms) or interface
                if not classobj.IS_ENUM and not classobj.IS_STRUCT and not classobj.AUTOGEN and not classobj.PURE_VIRTUAL_INTERFACE:
                    dict_to_replace_lines = {}
                    dict_to_replace_lines["<<<CLASSNAME>>>"] = classobj.NAME
                    dict_to_replace_lines["<<<AUTHOR>>>"] = self.author
                    dict_to_replace_lines["<<<GROUP>>>"] = self.group
                    dict_to_replace_lines["<<<BRIEF>>>"] = self.brief
                    dict_to_replace_lines["<<<PYIFGENNAME>>>"] = self.vpp_filename
                    dict_to_replace_lines["<<<NESTED_NAMESPACE_BEGIN>>>"] = self.language.GetFormatNestedNamespaceBegin(classobj)
                    dict_to_replace_lines["<<<NESTED_NAMESPACE_END>>>"] = self.language.GetFormatNestedNamespaceEnd(classobj)
                    dict_to_replace_lines["<<<DLL_EXPORT>>>"] = declspc
                    dict_to_replace_lines["<<<CLASS_DOCUMENTATION>>>"] = self.language.FormatLongComment(classobj.USER_COMMENTS.strip())
                    dict_to_replace_lines["<<<CLASS_INHERITENCE_HIERARCHY>>>"] = self.language.GetFormatClassInheritence(classobj, classdiagram.inheritence)
                    dict_to_replace_lines["<<<NOT_FORWARD_DECLARABLE_HEADER_INCLUDES>>>"] = self.language.GetNotForwardDeclarableHeaderIncludes(classobj, self.NAMESPACE_TO_GO_TO_OWN_FOLDER, True, True)
                    dict_to_replace_lines["<<<FORWARD_DECLARABLE_HEADER_INCLUDES>>>"] = self.language.GetForwardDeclarableHeaderIncludes(classobj, self.NAMESPACE_TO_GO_TO_OWN_FOLDER, True)
                    dict_to_replace_lines["<<<FORWARD_DECLARATIONS>>>"] = self.language.GetForwardDeclarations(classobj)
                    dict_to_replace_lines["<<<PUBLIC_ATTRIBUTES_DECLARE>>>"] = self.language.GetAttributeDeclarationsPerVisibility(classobj,"public")
                    dict_to_replace_lines["<<<PROTECTED_ATTRIBUTES_DECLARE>>>"] = self.language.GetAttributeDeclarationsPerVisibility(classobj,"protected")
                    dict_to_replace_lines["<<<PRIVATE_ATTRIBUTES_DECLARE>>>"] = self.language.GetAttributeDeclarationsPerVisibility(classobj,"private")
                    dict_to_replace_lines["<<<PUBLIC_ASSOCIATIONS_DECLARE>>>"] = self.language.GetAssociationDeclarationsPerVisibility(classobj, "public")
                    dict_to_replace_lines["<<<PROTECTED_ASSOCIATIONS_DECLARE>>>"] = self.language.GetAssociationDeclarationsPerVisibility(classobj, "protected")
                    dict_to_replace_lines["<<<PRIVATE_ASSOCIATIONS_DECLARE>>>"] = self.language.GetAssociationDeclarationsPerVisibility(classobj, "private")
                    dict_to_replace_lines["<<<STATIC_ATTRIBUTES_DECLARE>>>"] = self.language.GetStaticAttributeDefinitions(classobj)
                    dict_to_replace_lines["<<<STATIC_ASSOCIATIONS_DECLARE>>>"] = self.language.GetStaticAssociationDefinitions(classobj)
                    dict_to_replace_lines["<<<PUBLIC_OPERATIONS_DECLARE>>>"] = self.language.GetOperationPerVisibility(classobj, False, "public")
                    dict_to_replace_lines["<<<PROTECTED_OPERATIONS_DECLARE>>>"] = self.language.GetOperationPerVisibility(classobj, False, "protected")
                    dict_to_replace_lines["<<<PRIVATE_OPERATIONS_DECLARE>>>"] = self.language.GetOperationPerVisibility(classobj, False, "private")
                    dict_to_replace_lines["<<<OPERATIONS_IMPLEMENTATION>>>"] = self.language.GetOperationPerVisibility(classobj, True, "all")
                    dict_to_replace_lines["<<<ATTRIBUTES_ASSOCIATIONS_GETTER_SETTER_DECLARE>>>"] = self.language.GetAttributeAssociationGetterSetter(classobj, False)
                    dict_to_replace_lines["<<<ATTRIBUTES_ASSOCIATIONS_GETTER_SETTER_IMPLEMENTATION>>>"] = self.language.GetAttributeAssociationGetterSetter(classobj, True)
                    dict_to_replace_lines["<<<CONSTRUCTORS_DECLARE>>>"] = self.language.GetConstructor(classobj, False)
                    dict_to_replace_lines["<<<CONSTRUCTORS_IMPLEMENTATION>>>"] = self.language.GetConstructor(classobj, True)

                    dict_to_replace_filenames = {}
                    dict_to_replace_filenames["ClassTemplate"] = classobj.NAME
                    dict_to_replace_filenames['.ty'] = '.py'
                    dict_to_replace_filenames['.t'] = '.h'
                    dict_to_replace_filenames['.hpp'] = '.cpp'

                    tmp_res = CBASEGenerator.__loadtemplates_firstfiltering__(self, dict_to_replace_lines, dict_to_replace_filenames, "Class")
                    tmp_res = self.__update_filename_path_from_namespace(classobj.NAMESPACE, tmp_res)
                    result.filenames_to_lines.update(tmp_res.filenames_to_lines)
                # INTERFACE
                elif not classobj.IS_ENUM and not classobj.IS_STRUCT and not classobj.AUTOGEN and classobj.PURE_VIRTUAL_INTERFACE:
                    dict_to_replace_lines = {}
                    dict_to_replace_lines["<<<CLASSNAME>>>"] = classobj.NAME
                    dict_to_replace_lines["<<<AUTHOR>>>"] = self.author
                    dict_to_replace_lines["<<<GROUP>>>"] = self.group
                    dict_to_replace_lines["<<<BRIEF>>>"] = self.brief
                    dict_to_replace_lines["<<<PYIFGENNAME>>>"] = self.vpp_filename
                    dict_to_replace_lines["<<<NESTED_NAMESPACE_BEGIN>>>"] = self.language.GetFormatNestedNamespaceBegin(classobj)
                    dict_to_replace_lines["<<<NESTED_NAMESPACE_END>>>"] = self.language.GetFormatNestedNamespaceEnd(classobj)
                    dict_to_replace_lines["<<<DLL_EXPORT>>>"] = declspc
                    dict_to_replace_lines["<<<CLASS_DOCUMENTATION>>>"] = self.language.FormatLongComment(classobj.USER_COMMENTS)
                    dict_to_replace_lines["<<<CLASS_INHERITENCE_HIERARCHY>>>"] = self.language.GetFormatClassInheritence(classobj, classdiagram.inheritence)
                    dict_to_replace_lines["<<<NOT_FORWARD_DECLARABLE_HEADER_INCLUDES>>>"] = self.language.GetNotForwardDeclarableHeaderIncludes(classobj, self.NAMESPACE_TO_GO_TO_OWN_FOLDER, True, True)
                    #dict_to_replace_lines["<<<FORWARD_DECLARABLE_HEADER_INCLUDES>>>"] = language.GetForwardDeclarableHeaderIncludes(classobj, self.NAMESPACE_TO_GO_TO_OWN_FOLDER, True)
                    dict_to_replace_lines["<<<FORWARD_DECLARATIONS>>>"] = self.language.GetForwardDeclarations(classobj)
                    #dict_to_replace_lines["<<<PUBLIC_ATTRIBUTES_DECLARE>>>"] = language.GetAttributeDeclarationsPerVisibility(classobj,"public")
                    #dict_to_replace_lines["<<<PROTECTED_ATTRIBUTES_DECLARE>>>"] = language.GetAttributeDeclarationsPerVisibility(classobj,"protected")
                    #dict_to_replace_lines["<<<PRIVATE_ATTRIBUTES_DECLARE>>>"] = language.GetAttributeDeclarationsPerVisibility(classobj,"private")
                    #dict_to_replace_lines["<<<PUBLIC_ASSOCIATIONS_DECLARE>>>"] = language.GetAssociationDeclarationsPerVisibility(classobj, "public")
                    #dict_to_replace_lines["<<<PROTECTED_ASSOCIATIONS_DECLARE>>>"] = language.GetAssociationDeclarationsPerVisibility(classobj, "protected")
                    #dict_to_replace_lines["<<<PRIVATE_ASSOCIATIONS_DECLARE>>>"] = language.GetAssociationDeclarationsPerVisibility(classobj, "private")
                    #dict_to_replace_lines["<<<STATIC_ATTRIBUTES_DECLARE>>>"] = language.GetStaticAttributeDefinitions(classobj)
                    #dict_to_replace_lines["<<<STATIC_ASSOCIATIONS_DECLARE>>>"] = language.GetStaticAssociationDefinitions(classobj)
                    dict_to_replace_lines["<<<PUBLIC_OPERATIONS_DECLARE>>>"] = self.language.GetOperationPerVisibility(classobj, False, "public")
                    dict_to_replace_lines["<<<PROTECTED_OPERATIONS_DECLARE>>>"] = self.language.GetOperationPerVisibility(classobj, False, "protected")
                    dict_to_replace_lines["<<<PRIVATE_OPERATIONS_DECLARE>>>"] = self.language.GetOperationPerVisibility(classobj, False, "private")
                    #dict_to_replace_lines["<<<OPERATIONS_IMPLEMENTATION>>>"] = language.GetOperationPerVisibility(classobj, True, "all")
                    #dict_to_replace_lines["<<<ATTRIBUTES_ASSOCIATIONS_GETTER_SETTER_DECLARE>>>"] = language.GetAttributeAssociationGetterSetterDeclarations(classobj)
                    #dict_to_replace_lines["<<<ATTRIBUTES_ASSOCIATIONS_GETTER_SETTER_IMPLEMENTATION>>>"] = language.GetAttributeAssociationGetterSetterImplementations(classobj)

                    dict_to_replace_filenames = {}
                    dict_to_replace_filenames["InterfaceTemplate"] = classobj.NAME
                    dict_to_replace_filenames['.ty'] = '.py'
                    dict_to_replace_filenames['.t'] = '.h'
                    dict_to_replace_filenames['.hpp'] = '.cpp'

                    tmp_res = CBASEGenerator.__loadtemplates_firstfiltering__(self,dict_to_replace_lines,dict_to_replace_filenames, "Interface")
                    tmp_res = self.__update_filename_path_from_namespace(classobj.NAMESPACE, tmp_res)
                    result.filenames_to_lines.update(tmp_res.filenames_to_lines)
                # ENUM
                elif classobj.IS_ENUM and not classobj.IS_STRUCT:
                    dict_to_replace_lines = {}
                    dict_to_replace_lines["<<<CLASSNAME>>>"] = classobj.NAME
                    dict_to_replace_lines["<<<AUTHOR>>>"] = self.author
                    dict_to_replace_lines["<<<GROUP>>>"] = self.group
                    dict_to_replace_lines["<<<BRIEF>>>"] = self.brief
                    dict_to_replace_lines["<<<PYIFGENNAME>>>"] = self.vpp_filename
                    dict_to_replace_lines["<<<NESTED_NAMESPACE_BEGIN>>>"] = self.language.GetFormatNestedNamespaceBegin(classobj)
                    dict_to_replace_lines["<<<NESTED_NAMESPACE_END>>>"] = self.language.GetFormatNestedNamespaceEnd(classobj)
                    dict_to_replace_lines["<<<DLL_EXPORT>>>"] = declspc
                    dict_to_replace_lines["<<<CLASS_DOCUMENTATION>>>"] = self.language.FormatLongComment(classobj.USER_COMMENTS)
                    dict_to_replace_lines["<<<ENUM_EXPAND>>>"] = self.language.GetEnumLiterals(classobj)

                    dict_to_replace_filenames = {}
                    dict_to_replace_filenames["EnumTemplate"] = classobj.NAME
                    dict_to_replace_filenames['.ty'] = '.py'
                    dict_to_replace_filenames['.t'] = '.h'
                    dict_to_replace_filenames['.hpp'] = '.cpp'
                    tmp_res = CBASEGenerator.__loadtemplates_firstfiltering__(self, dict_to_replace_lines, dict_to_replace_filenames, "Enum")
                    tmp_res = self.__update_filename_path_from_namespace(classobj.NAMESPACE, tmp_res)
                    result.filenames_to_lines.update(tmp_res.filenames_to_lines)
                # STRUCT
                elif not classobj.IS_ENUM and classobj.IS_STRUCT:
                    dict_to_replace_lines = {}
                    dict_to_replace_lines["<<<CLASSNAME>>>"] = classobj.NAME
                    dict_to_replace_lines["<<<AUTHOR>>>"] = self.author
                    dict_to_replace_lines["<<<GROUP>>>"] = self.group
                    dict_to_replace_lines["<<<BRIEF>>>"] = self.brief
                    dict_to_replace_lines["<<<PYIFGENNAME>>>"] = self.vpp_filename
                    dict_to_replace_lines["<<<NESTED_NAMESPACE_BEGIN>>>"] = self.language.GetFormatNestedNamespaceBegin(classobj)
                    dict_to_replace_lines["<<<NESTED_NAMESPACE_END>>>"] = self.language.GetFormatNestedNamespaceEnd(classobj)
                    dict_to_replace_lines["<<<DLL_EXPORT>>>"] = declspc
                    dict_to_replace_lines["<<<CLASS_DOCUMENTATION>>>"] = self.language.FormatLongComment(classobj.USER_COMMENTS)
                    dict_to_replace_lines["<<<NOT_FORWARD_DECLARABLE_HEADER_INCLUDES>>>"] = self.language.GetNotForwardDeclarableHeaderIncludes(classobj, self.NAMESPACE_TO_GO_TO_OWN_FOLDER, True, True)
                    dict_to_replace_lines["<<<FORWARD_DECLARATIONS>>>"] = self.language.GetForwardDeclarations(classobj)
                    dict_to_replace_lines["<<<STRUCT_EXPAND>>>"] = self.language.GetStructMembers(classobj)
                    dict_to_replace_lines["<<<PACK_BEGIN>>>"] = self.language.GetPacked(classobj, True)
                    dict_to_replace_lines["<<<PACK_END>>>"] = self.language.GetPacked(classobj, False)

                    dict_to_replace_filenames = {}
                    dict_to_replace_filenames["StructTemplate"] = classobj.NAME
                    dict_to_replace_filenames['.ty'] = '.py'
                    dict_to_replace_filenames['.t'] = '.h'
                    dict_to_replace_filenames['.hpp'] = '.cpp'

                    tmp_res = CBASEGenerator.__loadtemplates_firstfiltering__(self, dict_to_replace_lines, dict_to_replace_filenames, "Struct")
                    tmp_res = self.__update_filename_path_from_namespace(classobj.NAMESPACE, tmp_res)
                    result.filenames_to_lines.update(tmp_res.filenames_to_lines)

            ### PROJECT FILES
            namespaces_in_project = {}
            if self.NAMESPACE_TO_GO_TO_OWN_FOLDER:
                namespaces_in_project = classdiagram.GetNamespaceDependencies()
            else:
                if self.classdiagramname: # not empty -> rename 'Project.xxxx' to 'classdiagramname.xxxx'
                    namespaces_in_project[self.classdiagramname] = set()
                else:
                    namespaces_in_project["Project"] = set()

            for namespace, dependency_set in namespaces_in_project.items():
                if len(dependency_set) > 0:
                    print(" <!!!!!!!>", namespace, " depends on ", dependency_set)
                try:
                    dict_to_replace_lines = {}
                    dict_to_replace_filenames = {}
                    dict_to_replace_lines["<<<PROJECT_REFERENCE_INCLUDES>>>"] = self.language.GetProjectIncludes(dependency_set)
                    dict_to_replace_filenames["Project"] = namespace
                    tmp_res = CBASEGenerator.__loadtemplates_firstfiltering__(self, dict_to_replace_lines, dict_to_replace_filenames, "Project")
                    tmp_res = self.__update_filename_path_from_namespace(namespace, tmp_res)
                    result.filenames_to_lines.update(tmp_res.filenames_to_lines)
                except:
                    pass
            ### PROJECT FILES end
            return result
        else:
            raise Exception( str(classdiagram) + " is not of type ClassDiagram")

    def __update_filename_path_from_namespace(self, fully_qualified_namespace, codemodel):
        """
        Will return a CodeModels' filenames with a path built up from a fully qualified namespace.
        For example: 'Filename.cpp', and input namespace of 'XNamespace1::XNamespace2'
        will change to XNamespace1\\XNamespace2\\Filename.cpp

        @param fully_qualified_namespace: 'XNamespace1::XNamespace2'
        @param codemodel:
        @return: codemodel with filenames modified as described.
        """
        if self.NAMESPACE_TO_GO_TO_OWN_FOLDER:
            namespace_subpath = fully_qualified_namespace.replace("::", os.path.sep)
            if namespace_subpath:
                new_tmp_res = {}
                for k, v in codemodel.filenames_to_lines.items():
                    new_tmp_res[os.path.join(namespace_subpath, k.replace(self.input_template_file_dir,""))] = v
                codemodel.filenames_to_lines = new_tmp_res
        return codemodel

def GenerateUML(umlgenerator, classdiagram, dclspc=""):
    cm = umlgenerator.__loadtemplates_firstfiltering__(classdiagram,dclspc)
    # Preserve user tags.
    umlgenerator.__preserve_usertags_in_files__(cm)
    '''
    # Round-trip Code Preservation. Will load the code to p
    preservation = Preservative(umlgenerator.output_gen_file_dir)
    preservation.Emplace(cm.filenames_to_lines)
    '''
    # Write output to file.
    umlgenerator.__createoutput__(cm.filenames_to_lines)

def Generate(vp_project_path, vp_classdiagramname, outputdir, language, author, group, brief, namespace_to_folders, dclspc="", templatefiledir = ""):

    if not os.path.isfile(vp_project_path):
        print("Error : file '" + vp_project_path + "' does not exist. Aborting.")
        return

    print("*************************************")
    print("******* UMLGen **********************")
    print("*************************************")
    print(" Output Dir    : " + outputdir)
    print(" Class Diagram : " + vp_classdiagramname)
    print(" Executing in  : " + os.path.realpath(__file__))
    print("*************************************")

    class_diagram = ExtractClassDiagram(vp_classdiagramname, vp_project_path)
    umlGen = CUMLGenerator(outputdir, language, author, group, brief, namespace_to_folders,templatefiledir,vp_classdiagramname)
    umlGen.vpp_filename = os.path.basename(vp_project_path)
    GenerateUML(umlGen,class_diagram,dclspc)

def TestCPP():
    #two class diagrams "ProtocolStack", "TestClassDiagram"
    language = LanguageCPP()
    Generate(r"C:\Code\homedev\TestModels.vpp","TestClassDiagram", r'C:\Code\homedev\autogen\test_uml_gen_cpp', language, 'koh.jaen@yahoo.de', True, "", "")

def TestCSharp():
    #two class diagrams "ProtocolStack", "TestClassDiagram"
    language = LanguageCsharp()
    Generate(r"C:\Code\homedev\TestModels.vpp","TestClassDiagram", r'C:\Code\homedev\autogen\test_uml_gen_csharp', language, 'koh.jaen@yahoo.de', False, "", "")

if __name__ == "__main__":
    #'''
    TestCSharp()
    '''
    import sys
    import getpass
    if len(sys.argv) < 2:
        print("Usage : python umlgen <output_dir> <uml_model_file> optional <class_diagram_name> optional <author> optional <namespace_to_folders> optional <declspec> optional <templatefiledir>")
    else:
        output_dir = str(sys.argv[1])
        uml_model_file = str(sys.argv[2])
        class_diagram_name = ""
        if len(sys.argv) >= 4:
            class_diagram_name = str(sys.argv[3])
        author = getpass.getuser()
        if len(sys.argv) >= 5:
            author = str(sys.argv[4])
        namespace_to_folders = True
        if len(sys.argv) >= 6:
            namespace_to_folders = bool(sys.argv[5])
        declspec = ""
        if len(sys.argv) >= 7:
            declspec = bool(sys.argv[6])
        templatefiledir = ""
        if len(sys.argv) >= 8:
            templatefiledir = bool(sys.argv[7])

        language = LanguageCPP()

        allCDs = []
        if not class_diagram_name.strip():
            allCDs = ExtractAllClassDiagrams(uml_model_file)
        else:
            class_diagram = ExtractClassDiagram(class_diagram_name, uml_model_file)
            allCDs.append(class_diagram)

        for cd in allCDs:
            umlGen = CUMLGenerator(output_dir, language, author, namespace_to_folders, templatefiledir)
            GenerateUML(umlGen, cd, declspec)

    #'''