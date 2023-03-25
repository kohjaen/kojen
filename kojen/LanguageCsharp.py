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
import datetime
import sys
import time
from string import Template

try:
    from kojentypes import *
except (ModuleNotFoundError, ImportError) as e:
    from .kojentypes import *

try:
    from vppclassdiagram import *
except (ModuleNotFoundError, ImportError) as e:
    from .vppclassdiagram import *

from .Language import *

class LanguageCsharp(Language):

    '''USED'''
    def ByteStreamTypeSharedPtr(self):
        return self.SharedPtrToType(self.ByteStreamType())

    '''USED'''
    def ByteStreamTypeRawPtr(self):
        return self.RawPtrToType("uint8")

    '''USED'''
    def ByteStreamType(self):
        return 'std::vector<uint8>'

    '''USED'''
    def TypedefSharedPtrToType(self, typename):
        return 'typedef ' + self.SharedPtrToType(typename) + " " + self.PtrToTypeName(typename)

    '''USED'''
    def TypedefRawPtrToType(self, typename):
        return 'typedef ' + self.RawPtrToType(typename) + " " + self.PtrToTypeName(typename)

    def PtrToTypeName(self, typename):
        return typename + '_ptr'

    '''USED'''
    # Convenience
    def SharedPtrToType(self, typename):
        return 'justaplain_shared_ptr<' + typename + '>'

    def RawPtrToType(self, typename):
        return typename + '*'

    # parameters need to be a list of (type, name).
    def ParameterString(self, parameters=None) -> str:
        if parameters is None:
            parameters = []

        if str(type(parameters)) == "<type 'list'>" or str(type(parameters)) == "<class 'list'>":  # Python2 gives the first, python3 the second!
            parameter_string = ''
            size = len(parameters)
            cnt = 0
            for param in parameters:
                if HasDefault(param):
                    parameter_string += param[0] + ' ' + param[1] + "=" + param[2]
                else:
                    parameter_string += param[0] + ' ' + param[1]
                if cnt != (size - 1):
                    parameter_string += ', '
                cnt += 1
            return parameter_string

        raise Exception("Please use OrderedDict when passing parameters into 'ParameterString'")
    '''USED'''
    def DeclareFunction(self, returntype, classname, functionname, is_impl, parameters=None, virtual=False, is_static=False, is_const=False) -> str:
        if parameters is None:
            parameters = []

        if str(type(parameters)) == "<type 'list'>" or str(type(parameters)) == "<class 'list'>":  # Python2 gives the first, python3 the second!
            parameter_string = self.ParameterString(parameters)

            #if is_impl:
            #    if classname.replace(' ', '') != '':
            #        return returntype + ' ' +  functionname + '(' + parameter_string + ')' + (" const" if is_const else "")
            #    return returntype + ' ' + functionname + '(' + parameter_string + ')' + (" const" if is_const else "")

            if virtual and not is_static:  # don't allow static.
                return 'virtual ' + returntype + ' ' + functionname + '(' + parameter_string + ')' + (" const" if is_const else "")

            return ("static " if is_static else "") + returntype + ' ' + functionname + '(' + parameter_string + ')' + (" const" if is_const else "")

        raise Exception("Please use list when passing parameters into 'DeclareFunction'")

    '''USED'''
    def GetFactoryCreateParams(self, struct, interface, with_defaults=False) -> list:
        # C++ copy/paste
        def _processDefaults(default) -> str:
            res = ""
            if str(type(default)) == "<class 'list'>":
                res += "{"
                for i in default:
                    if HasDefault(i):
                        res += _processDefaults(i[2]) + ","
                    else:
                        res += "{},"
                res = res.rstrip(",")
                res += "}"
            else:
                res += default
            return res

        structmembers = struct.Decompose()
        factoryparams = []
        for mem in structmembers:
            isMessage = interface.IsMessageStruct(mem[0])
            isStruct = struct.IsStruct(mem[1])
            if not interface.IsProtocolStruct(mem[0]):
                ref = ""#" const&" if isStruct or isMessage else ""
                if mem[0] in interface:
                    factoryparams.append(((self.SharedPtrToType(mem[0]) if isMessage else mem[0]) + ref,
                                          (mem[1] + "=" + _processDefaults(mem[2])) if (with_defaults and HasDefault(mem)) else mem[1]))
                else:
                    if with_defaults:
                        if HasDefault(mem):
                            factoryparams.append((mem[0] + ref, mem[1], _processDefaults(mem[2])))
                        else:
                            factoryparams.append((mem[0] + ref, mem[1], "{}"))
                    else:
                        factoryparams.append((mem[0] + ref, mem[1]))
        return factoryparams

    '''USED
    Declares the guts of a struct declaration
    '''
    def DeclareStructMembers(self, struct, interface, whitespace, attr_packed=True) -> list:
        structmembers = struct.Decompose()
        result = []
        for mem in structmembers:
            ptr = ""
            if mem[0] in interface:
                result.append(whitespace + "public " + self.InstantiateType(mem[0], mem[1]) + ";")
            else:
                result.append(whitespace + "public " + self.InstantiateType(mem[0] + ptr, mem[1], mem[2] if HasDefault(mem) else "", is_attr_packed=False) + ";")
        return result
    '''USED'''
    def InstantiateStructMembers(self, struct, interface, whitespace, instancename, accessor = ".") -> list:
        structmembers = struct.Decompose()
        result = []
        for mem in structmembers:
            isStruct = interface.IsStruct(mem[1])
            isProtocol = interface.IsProtocolStruct(mem[0])
            instance_accessor = whitespace + instancename + accessor

            if not isProtocol or isStruct:
                result.append(instance_accessor + self.InstantiateType('', mem[1], mem[1]) + ";")
            elif isProtocol and not isStruct:
                s = Template("sizeof(${this}) - sizeof(${header})")
                # Aggregate initializer
                new = instance_accessor + self.InstantiateType("", mem[1], "{" + struct[mem[1]].GetDefaultsAsString(s.substitute(this=struct.Name, header=mem[0])) + "};")
                result.append(new)
            else:
                print("WTF : InstantiateStructMembers")

        return result

    '''USED'''

    def InstantiatePtrToType(self, typename, instancename, typepointername=""):
        return (typepointername if typepointername else self.PtrToTypeName(typename)) + ' ' + instancename + '(new ' + typename + ')'

    '''USED'''
    def InstantiateArray(self, typename, instancename, noelements):
        return instancename + ' = new ' + typename + '['+noelements+']'

    '''USED

        Instantiate/declare a basic type, with optional initializer. Only declarations can use 'attribute packed' directives.
        use typename = '' to make it a known variable initialization
    '''
    def InstantiateType(self, typename, instancename, initialevalue='', is_attr_packed=False, is_static=False, is_const=False) -> str:
        # declaration...i.e. in class or struct. no initial value, can be packed
        if initialevalue.replace(' ', '') == '':
            decl = typename + ' ' + instancename
            if is_static:
                decl = 'static ' + decl
            if is_const:
                decl = 'readonly ' + decl
            if is_attr_packed:
                return self.AddAttributePackedToDecl(decl)
            return decl

        # local variable decl/instantiation or known variable instantiation
        if typename.replace(' ', '') == '':
            return instancename + ' = ' + initialevalue

        res = typename + ' ' + instancename + ' = ' + initialevalue
        if is_static:
            res = 'static ' + res
        if is_const:
            res = 'const ' + res
        return res

    # Braces
    '''USED'''
    def OpenBrace(self):
        return '{'

    '''USED'''
    def CloseBrace(self):
        return '}'

    # Connection type
    def ConnectionType(self):
        return 'IConnection'

    def ConnectionTypePtr(self):
        return 'IConnection_ptr'

    # Member access / dereference
    '''USED'''
    def Accessor(self, is_ptr):
        if is_ptr:
            return '->'
        return '.'

    # Bytestream access / dereference
    def BytestreamAccessor(self):
        return '->'

    # Packedness
    def AddAttributePackedToDecl(self, declaration):
        """
        ws = ' '
        len_declaration = len(declaration)
        trailingspacecnt = 50 - len_declaration
        for i in range(trailingspacecnt):
            ws = ws + ' '
        result = declaration + ws + '__attribute__ ((packed))'
        """
        return declaration

    def DeleteArray(self, instancename):
        return 'delete[] ' + instancename + ';\n'

    def DeletePtrToType(self, instancename):
        return 'delete ' + instancename + ';\n'

    def DeclareClass(self, classname, declspec=''):
        if declspec.replace(' ', '') != '':
            return 'class ' + declspec + ' ' + classname + '\n'
        return 'class ' + classname + '\n'

    def ForwareDeclareClass(self, classname):
        return 'CGEN_DECL_CLASS_PTR(' + classname + ');\n'

    def DeclareStruct(self, structname, declspec=''):
        if declspec.replace(' ', '') != '':
            return 'struct ' + declspec + ' ' + structname + '\n'
        return 'struct ' + structname + '\n'

    def DeclareEnum(self, enum, whitespace) -> str:
        result = self.FormatComment(enum.documentation) + "\n"
        result += "public enum " + enum.Name + " : byte {\n"
        for descriptionName, val in enum.items():
            result += whitespace + str(descriptionName) + " = " + str(val) + ",\n"
        result = result[:len(result)-2] + "\n"  # items from the beginning through end-1 (i.e. remove last character which is a ','
        result +=  "};\n"
        return result

    def DeclareHashDefine(self, name, val):
        return "#define " + name + " " + str(val)

    def DeclareNamespace(self, namespacename):
        return 'namespace ' + namespacename + '\n'

    def UsingNamespace(self, namespacename):
        return 'using namespace ' + namespacename + ';\n'
    '''USED'''
    def FormatComment(self, commenttext):
        if commenttext:
            return '// ' + commenttext
        return ""

    def FormatLongComment(self, commenttext):
        if commenttext:
            return '/**' + commenttext + '*/\n'
        return ""

    # The includes that each generated file needs to have from the provided mini framework
    def LanguageSpecificFrameWorkIncludes(self):
        return ['"../../allplatforms/basetypes.h"']

    def AddInclude(self, filename):  # for python we can simply replace .h with''
        return '#include ' + filename

    def PrintError(self, message):
        return 'printf( ' + message + ');'
    '''USED'''
    def PrintMessage(self, message):
        return 'printf(' + message + ');'

    def BooleanTrue(self):
        return 'true'

    def BooleanFalse(self):
        return 'false'

    '''USED'''
    def NullPtr(self):
        return 'nullptr'

    def PublicAccessSpecifier(self):
        return 'public:\n'

    def ProtectedAccessSpecifier(self):
        return 'protected:\n'

    def PrivateAccessSpecifier(self):
        return 'private:\n'

    def If(self, statement):
        return 'if('+statement+')'

    def ElseIf(self, statement):
        return 'else if('+statement+')'

    def Else(self):
        return 'else'

    def This(self):
        return 'this->'

    def LicenseAgreement(self):
        product_name = "'KoJen'"
        result = []
        result.append("--------------------------------------------------------------------------------")
        result.append("")
        result.append('    ' + "This file is part of " + product_name + ".")
        result.append("")
        result.append('    ' + product_name + " is free software: you can redistribute it and/or modify")
        result.append('    ' + "it under the terms of the GNU General Public License as published by")
        result.append('    ' + "the Free Software Foundation, either version 3 of the License, or")
        result.append('    ' + "(at your option) any later version.")
        result.append("")
        result.append('    ' + product_name + " is distributed in the hope that it will be useful,")
        result.append('    ' + "but WITHOUT ANY WARRANTY; without even the implied warranty of")
        result.append('    ' + "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the")
        result.append('    ' + "GNU General Public License for more details.")
        result.append("")
        result.append('    ' + "You should have received a copy of the GNU General Public License")
        result.append('    ' + "along with " + product_name + ".  If not, see <http://www.gnu.org/licenses/>.")
        result.append('    ' + "For any queries please contact : koh.jaen@yahoo.de.")
        result.append("\n")
        result.append('        ' + "This file was generated using : " + sys.platform + ".")
        result.append('        ' + "This file was generated by a machine. Do not modify it by hand.")
        result.append("")
        result.append("--------------------------------------------------------------------------------")
        return result

    ''' Additions that were added for class diagram
    '''

    def GetFormatNestedNamespaceBegin(self, classObj):
        """
        Returns the C++ format string for a nested namespace declaration on one line...
        @param classObj: class information from vppclassdiagram.Class
        @return: string i.e. "namespace XFullStack { namespace XProtocol {"
        """
        # Nested NAMESPACE of the classobj is i.e. 'XFullStack::XProtocol'
        if isinstance(classObj, Class):
            result = _getFormatNestedNamespaceBegin(classObj.NAMESPACE)
            return result
        else:
            raise RuntimeError("Language Feature Not Implemented")

    def GetFormatNestedNamespaceEnd(self, classObj):
        """
        Returns the C++ format string for a nested namespace end-declaration on one line...

        @param classObj: class information from vppclassdiagram.Class
        @return: string i.e. for "namespace XFullStack { namespace XProtocol {" will return "} }"
        """
        # Nested NAMESPACE of the classobj is i.e. 'XFullStack::XProtocol'
        if isinstance(classObj, Class):
            result = _getFormatNestedNamespaceEnd(classObj.NAMESPACE)
            return result + " // end namespace " + classObj.NAMESPACE
        else:
            raise RuntimeError("classObj Not of type Class")

    def GetFormatClassInheritence(self, classObj, dictOfInheritance):
        """
        Returns the C# format string for class inheritence based on objects
        returned by parsing the class diagram in e.g. our favourite UML tool.

        Note : For C#, Base classes must come before interfaces ... and only a single class is allowed to be inherited in C# (but multiple interfaces).
        We leave that up to the software designer using this tool ... he should know that.

        @param classObj: class information from vppclassdiagram.Class
        @param dictOfInheritance: a dictionary of inheritence info : {'id': vppclassdiagram.Inheritance}
        @return: string with the C++ inheritance for this class, e.g. " : public Parent1, public Parent2"
        for "class Child : public Parent1, public Parent2"
        """
        result = ""
        _classes_str = ""
        _interfaces_str = ""
        if isinstance(classObj, Class) and isinstance(dictOfInheritance, dict):
            for id, inheritance in dictOfInheritance.items():
                if isinstance(inheritance, Inheritance):
                    if inheritance.CLASS_TO_ID.find(classObj.ID) > -1:
                        # classes before interfaces in inheritance hierarchy
                        fixed_name = inheritance.CLASS_FROM.replace(classObj.NAMESPACE + "::","")
                        if classObj.parent_classDiagram.classes[inheritance.CLASS_FROM_ID].PURE_VIRTUAL_INTERFACE:
                            _interfaces_str = _interfaces_str + ' ' + fixed_name + ", "
                        else:
                            _classes_str = _classes_str + ' ' + fixed_name + ", "
                else:
                    raise RuntimeError("dictOfInheritance contains item not of type 'Inheritance'")
        else:
            raise RuntimeError("classObj not of type 'Class' OR dictOfInheritance not of type 'dict'")

        result = _classes_str + _interfaces_str
        if len(result) > 0:
            # remove last ','
            result = result.strip().rstrip(',')
            # add " : "
            result = " : " + result
        return result.replace("::",".")

    # Typically what goes into a H file, when the items can NOT be forward declared in H file.
    def GetNotForwardDeclarableHeaderIncludes(self, classObj, namespace_to_folders = False, filter_out_type_not_in_model = False, include_vector_if_needed = False):
        """
            For Header files. Given a class object, and class diagram, will return a multi-line string containing all header includes
            for types that can not be forward declared (ie. to reduce include dependencies) in a header file.

            If 'namespace_to_folders' is set, then that assumes the code is output into a separate folder per namespace.

            @param classObj: the 'vppclassdiagram.Class' object that we are working out the not-forward-declarable-type header includes.
            @param namespace_to_folders: This option implies that code is generated nested, in folders, named after namespace. This affects how header files are addressed.
            @param filter_out_type_not_in_model:  Will filter out includes of classes that do not exist in the class diagram.
            @return:
        """
        if isinstance(classObj, Class):
            #filter = classObj.GetNotForwardDeclarableNonPrimitiveTypesLinkedToThis()
            #namespace_to_classes = _getNamespaceToClassesFromFullyQualifiedNames(classObj, filter, True)
            #if filter_out_type_not_in_model:
            #    namespace_to_classes = _filterOutTypesNotInModel(namespace_to_classes, classObj.parent_classDiagram)
            #result = _getIncludeStringFromNamespaceToClassMap(namespace_to_classes,namespace_to_folders)

            # Check multiplicity of attributes / operation parameters / associations for 'array'...and include that if it needs.
            #if include_vector_if_needed:
            result = ""
            if classObj.DoAttributesAssociationsReturnTypesOrFunctionParametersRequireVector():
                result = result + 'using System.Collections.Generic;\n'
            return result
        else:
            raise RuntimeError("classObj not of type 'Class'")

    # Typically what goes into a CPP file, when the items can be forward declared in H file.
    def GetForwardDeclarableHeaderIncludes(self, classObj, namespace_to_folders = False, filter_out_type_not_in_model = False):
        """
            For SOURCE files. Given a class object, and class diagram, will return a multi-line string containing all header includes
            for types that can be forward declared (ie. to reduce include dependencies) in a header file.

            If 'namespace_to_folders' is set, then that assumes the code is output into a separate folder per namespace.

            @param classObj: the 'vppclassdiagram.Class' object that we are working out the forward-declarable-type header includes.
            @param namespace_to_folders: This option implies that code is generated nested, in folders, named after namespace. This affects how header files are addressed.
        """
        if isinstance(classObj, Class):
            filter = classObj.GetForwardDeclarableNonPrimitiveTypesLinkedToThis()
            namespace_to_classes = _getNamespaceToClassesFromFullyQualifiedNames(classObj, filter, True)
            if filter_out_type_not_in_model:
                namespace_to_classes = _filterOutTypesNotInModel(namespace_to_classes, classObj.parent_classDiagram)
            result = _getIncludeStringFromNamespaceToClassMap(namespace_to_classes,namespace_to_folders)
            return result
        else:
            raise RuntimeError("classObj not of type 'Class' OR classDiagram not of type 'ClassDiagram'")

    # Typically what goes into a H file, when the items can be forward declared in H file.
    def GetForwardDeclarations(self, classObj):
        """
        For HEADER files. Given a class object, and class diagram, will return a multi-line string containing all forward declares
        for types that can be forward declared (ie. to reduce include dependencies) in a header file.

        @param classObj:
        """
        if isinstance(classObj, Class):
            filter = classObj.GetForwardDeclarableNonPrimitiveTypesLinkedToThis()
            namespace_to_classes = _getNamespaceToClassesFromFullyQualifiedNames(classObj, filter, False)
            result = ""
            for _namespace, _classes in namespace_to_classes.items():
                result = result + _getFormatNestedNamespaceBegin(_namespace) + "\n"
                for _class in _classes:
                    result = result + "    class " + _class + ";\n"
                result = result + _getFormatNestedNamespaceEnd(_namespace) + "\n"

            if result:
                result = "// Begin Forward declarations\n" + result + "// End Forward declarations"
            return result
        else:
            raise RuntimeError("classObj not of type 'Class' OR classDiagram not of type 'ClassDiagram'")

    def GetTypeAndNameFromMultiplicityAndModifier(self, classObj, TYPE, TYPE_MODIFIER, MULTIPLICITY, NAME):
        """
        https://www.researchgate.net/figure/Mappings-from-C-declarations-to-UML-multiplicity-ranges-depend-on-pointer-reference_tbl1_4207986
        http://www.cs.kent.edu/~jmaletic/papers/JIST07.pdf

        @param TYPE:
        @param TYPE_MODIFIER:
        @param MULTIPLICITY:
        @param NAME:
        @return:
        """
        # Csharpify
        TYPE = TYPE.replace("::",".")
        if TYPE_MODIFIER.find("*") > -1 or TYPE_MODIFIER.find("&") > -1:
            TYPE_MODIFIER = ""
        # Csharpify

        if TYPE_MODIFIER.strip() == "[]":
            if not MULTIPLICITY:  # vector
                return ["List<" + TYPE + ">", NAME]
            #else:
            #    TYPE_MODIFIER = ""

        containerType = classObj.GetContainerMultiplicityType(MULTIPLICITY)
        if containerType.find('vector') > -1:
            return ["List<" + TYPE + TYPE_MODIFIER + ">", NAME]
        elif containerType.find('array') > -1:
            #return [TYPE + TYPE_MODIFIER, NAME + "[" + containerType.split(":")[-1] + "]"]
            return [TYPE + TYPE_MODIFIER + "[]", NAME ]
        return [TYPE + TYPE_MODIFIER, NAME]

    def GetDefaultFormatFromMultiplicityAndModifier(self, classObj, TYPE_MODIFIER, MULTIPLICITY, DEFAULT):
        if TYPE_MODIFIER.strip() == "[]":
            if not MULTIPLICITY:  # vector
                return " = {" + DEFAULT + "}"

        containerType = classObj.GetContainerMultiplicityType(MULTIPLICITY)
        if containerType.find('vector') > -1:
            return " = {" + DEFAULT + "}"
        elif containerType.find('array') > -1:  # Array -> In C++ it is not possible to pass a complete block of memory by value as a parameter to a function, but we are allowed to pass its address.
            return ""
        return " = " + DEFAULT

    def GetAttributeDeclarationsPerVisibility(self, classObj, visibility="all", attributes=None):
        """
        Get the declaration string for all attributes of the desired visibility
         - public
         - protected
         - private
         - all (public and protected and private)

        @param classObj: vppclassdiagram.Class
        @param visibility: string
        """
        result = ""
        no_attr_passed_in = attributes is None
        if no_attr_passed_in:
            attributes = classObj.ATTRIBUTES

        for attr in attributes:
            if visibility.lower().strip() == attr.VISIBILITY.lower().strip() or visibility.lower().strip() == 'all':
                result = result + self.FormatLongComment(attr.USER_COMMENTS)
                result = result + attr.VISIBILITY.lower() + " "
                type_name = self.GetTypeAndNameFromMultiplicityAndModifier(classObj, attr.TYPE, attr.TYPE_MODIFIER, attr.MULTIPLICITY, attr.NAME)
                result = result + self.InstantiateType(type_name[0], type_name[1], '', False, attr.IS_STATIC, attr.IS_CONST)
                result = result + ";\n"
        if result and no_attr_passed_in:
            result = "/// @{ " + visibility.capitalize() + " attributes\n" + result + "/// @}"
        return result.rstrip("\n")

    def GetAssociationDeclarationsPerVisibility(self, classObj, visibility="all"):
        """
        Get the declaration string for all associations of the desired visibility
         - public
         - protected
         - private
         - all (public and protected and private)

        @param classObj: vppclassdiagram.Class
        @param visibility: string
        """
        result = self.GetAttributeDeclarationsPerVisibility(classObj, visibility, classObj.GetAssociationsAsListOfAttributesPerVisibility(visibility))
        if result:
            result = "/// @{ " + visibility.capitalize() + " associations\n" + result + "\n/// @}"
        return result.rstrip("\n")

    def GetStaticAttributeDefinitions(self, classObj, attributes=None):
        """
        Get the definition string for all static-attributes regardless of the desired visibility
         - public
         - protected
         - private
         - all (public and protected and private)

        @param classObj: vppclassdiagram.Class
        """
        result = ""
        no_attr_passed_in = attributes is None
        if no_attr_passed_in:
            attributes = classObj.ATTRIBUTES

        for attr in attributes:
            if attr.IS_STATIC:
                type_name = self.GetTypeAndNameFromMultiplicityAndModifier(classObj, attr.TYPE, attr.TYPE_MODIFIER, attr.MULTIPLICITY, attr.NAME)
                result = result + self.InstantiateType(type_name[0], classObj.NAME + "::" + type_name[1], ("" if not attr.INITIAL_VALUE else attr.INITIAL_VALUE), False, False, attr.IS_CONST)
                result = result + ";\n"
        if result and no_attr_passed_in:
            result = "/// @{ Static attribute definitions\n" + result + "/// @}"
        return result.rstrip("\n")

    def GetStaticAssociationDefinitions(self, classObj):
        """
        Get the declaration string for all static-associations regardless of the desired visibility
         - public
         - protected
         - private
         - all (public and protected and private)

        @param classObj: vppclassdiagram.Class
        """
        result = self.GetStaticAttributeDefinitions(classObj, classObj.GetAssociationsAsListOfAttributesPerVisibility("all"))
        if result:
            result = "/// @{ Static association definitions\n" + result + "\n/// @}"
        return result.rstrip("\n")

    def GetOperationPerVisibility(self, classObj, is_impl, visibility="all", REALIZING_CLASS = ""):
        is_impl = not classObj.PURE_VIRTUAL_INTERFACE  # Csharp...

        result = ""
        # First see if we realize some base-classes.
        realized_result = ""
        for id, inheritance in classObj.parent_classDiagram.inheritence.items():
            if inheritance.CLASS_TO_ID.find(classObj.ID) > -1:
                if inheritance.IS_REALIZATION or REALIZING_CLASS:  # or REALIZING_CLASS -> if a pure virtual interface inherits another pure virtual interface, and the top child class that inherits them all wants to realize, then all should be realized
                    # get the class we are realizing...
                    realizeObj = classObj.parent_classDiagram.classes[inheritance.CLASS_FROM_ID]
                    if realizeObj.PURE_VIRTUAL_INTERFACE:
                        realized_result = realized_result + self.GetOperationPerVisibility(realizeObj,is_impl,visibility, (classObj.NAME if not REALIZING_CLASS else REALIZING_CLASS)) + "\n"
        if realized_result:
            result = realized_result

        for operation in classObj.OPERATIONS:
            if visibility.lower().strip() == operation.VISIBILITY.lower().strip() or visibility.lower().strip() == 'all':

                is_constructor = operation.NAME.strip() == classObj.NAME.strip()

                result = result + self.FormatLongComment(operation.USER_COMMENTS)
                # Create a list of tuples for the parameters.
                # parameter is a dictionary with the following keys:
                # 'const'
                # 'type'
                # 'name'
                # 'modifier'
                # 'defaultvalue'
                # 'multiplicity'
                # 'direction'
                params = []
                for param in operation.PARAMETERS:
                    tuples = self.GetTypeAndNameFromMultiplicityAndModifier(classObj, param["type"].strip(), param["modifier"].strip(), param["multiplicity"].strip(), param["name"].strip())
                    #tuple0 = param["const"].strip() + " " + tuples[0]
                    if param["direction"].strip().find("inout") > -1:
                        tuple0 = "ref " + tuples[0]
                    elif param["direction"].strip().find("out") > -1:
                        tuple0 = "out " + tuples[0]

                    tuple0 = tuple0.lstrip()
                    tuple1 = tuples[1]
                    if not is_impl:  # declarations need defaults.
                        tuple1 = tuple1 + ("" if not param["defaultvalue"].strip() else self.GetDefaultFormatFromMultiplicityAndModifier(classObj, param["modifier"].strip(), param["multiplicity"].strip(), param["defaultvalue"]))
                    params.append((tuple0, tuple1))

                # How to handle a return type modifier of [] ??? There is no multiplicity.
                # For now I do it as a vector in this case...
                # Search for <!#!>
                return_type = "" if is_constructor else self.GetTypeAndNameFromMultiplicityAndModifier(classObj, operation.RETURN_TYPE, operation.RETURN_TYPE_MODIFIER, "", "")[0]  # operation.RETURN_TYPE + operation.RETURN_TYPE_MODIFIER

                classname = (classObj.NAME if not REALIZING_CLASS else REALIZING_CLASS)
                # result = result + operation.VISIBILITY.lower() + " " + self.DeclareFunction(return_type, classname, operation.NAME, is_impl, params, classObj.PURE_VIRTUAL_INTERFACE or operation.VIRTUAL, operation.IS_STATIC, operation.IS_CONST).lstrip()
                result = result + operation.VISIBILITY.lower() + " " + self.DeclareFunction(return_type, classname,
                                                                                            operation.NAME, is_impl,
                                                                                            params,
                                                                                            operation.VIRTUAL,
                                                                                            operation.IS_STATIC,
                                                                                            False).lstrip()
                if REALIZING_CLASS:
                    result = result.replace("virtual","override")
                if not classObj.PURE_VIRTUAL_INTERFACE or REALIZING_CLASS:
                    result = result + "\n"
                    result = result + "{\n"
                    result = result + "    /// {{{USER_" + ("CONSTRUCTOR" if is_constructor else CleanName(operation.RETURN_TYPE)) + "_" + classname + "_" + operation.NAME + "_" + str(len(params)) + "_PARAMS}}}\n"
                    result = result + "    /// {{{USER_" + ("CONSTRUCTOR" if is_constructor else CleanName(operation.RETURN_TYPE)) + "_" + classname + "_" + operation.NAME + "_" + str(len(params)) + "_PARAMS}}}\n"
                    result = result + "}\n"
                else:
                    result = result + ";\n"

        if result.replace('\n',"").strip():
            if is_impl:
                result = "/// @{ " + visibility.capitalize() + " operation implementations\n" + result + "/// @}" if not REALIZING_CLASS else result
            else:
                result = "/// @{ " + visibility.capitalize() + " operation declarations\n" + result + "/// @}" if not REALIZING_CLASS else "/// @{ " + classObj.NAME + " operation overrides\n" + result + "/// @}"
        return result.rstrip("\n")

    def GetConstructor(self, classObj, is_impl = False):
        is_impl = True  # Csharp...

        # Problem is, that const attributes need to be initialized in a constructor.
        # static const ones are already (and can only be) done where they are declared in CPP file...but class members need to be done in the constructor.
        # This works all that out.
        all = [classObj.ATTRIBUTES, classObj.GetAssociationsAsListOfAttributesPerVisibility("all")]
        params = []
        attr_names = []
        for a in all:
            for attr in a:
                if attr.IS_CONST and not attr.IS_STATIC:
                    tuples = self.GetTypeAndNameFromMultiplicityAndModifier(classObj, attr.TYPE.strip(), attr.TYPE_MODIFIER.strip(), attr.MULTIPLICITY.strip(),  attr.NAME.strip().lower().replace("m_","_"))
                    tuple0 = tuples[0]
                    tuple0 = tuple0.lstrip()
                    tuple1 = tuples[1]
                    params.append((tuple0,tuple1))
                    attr_names.append(attr.NAME.strip())
        result = ""
        if params:
            result = "public " + self.DeclareFunction("", classObj.NAME, classObj.NAME, is_impl, params, False, False, False).lstrip() + ("" if is_impl else ";")
            if is_impl:
                #result = result + "\n: "
                #for i in range(len(params)):
                #    result = result + attr_names[i] + "{ " + params[i][1] + " }, "
                #result = result.rstrip(", ")
                #result = result + "\n"
                result = result + "{\n"
                for i in range(len(params)):
                    result = result + "    " + attr_names[i] + " = " + params[i][1] + ";\n"
                result = result + "    /// {{{USER_CONSTRUCTOR_" + classObj.NAME + "_" + str(len(params)) + "_PARAMS}}}\n"
                result = result + "    /// {{{USER_CONSTRUCTOR_" + classObj.NAME + "_" + str(len(params)) + "_PARAMS}}}\n"
                result = result + "}\n"
        return result.rstrip("\n")

    def GetAttributeAssociationGetterSetter(self, classObj, is_impl = False):
        is_impl = True  # Csharp...
        result = ""
        # start with attributes, then associations
        all = [classObj.ATTRIBUTES, classObj.GetAssociationsAsListOfAttributesPerVisibility("protected") + classObj.GetAssociationsAsListOfAttributesPerVisibility("private")]
        for a in all:
            for attr in a:
                type_and_name = self.GetTypeAndNameFromMultiplicityAndModifier(classObj, attr.TYPE, attr.TYPE_MODIFIER, attr.MULTIPLICITY, attr.NAME)
                #a_type = ("const " if attr.IS_CONST else "") + type_and_name[0]
                a_type = type_and_name[0]
                if attr.HAS_GETTER:
                    result = result + self.DeclareFunction(a_type, classObj.NAME, type_and_name[1].replace("m_", "Get"), is_impl) + ("\n" if is_impl else ";\n")
                    if is_impl:
                        result = result + "{\n"
                        result = result + "    return " + type_and_name[1] + ";\n"
                        result = result + "}\n"
                if attr.HAS_SETTER and not attr.IS_CONST:  # Cant set a const attribute!
                    inputvarName = type_and_name[1].replace("m_", "__new")
                    result = result + self.DeclareFunction("void", classObj.NAME, type_and_name[1].replace("m_", "Set"), is_impl, [(a_type, inputvarName)]) + ("\n" if is_impl else ";\n")
                    if is_impl:
                        result = result + "{\n"
                        result = result + "    " + type_and_name[1] + " = " + inputvarName + ";\n"
                        result = result + "}\n"

        if result:
            if is_impl:
                result = "/// @{ Accessor implementations\n" + result + "/// @}"
            else:
                result = "/// @{ Accessor declarations\n" + result + "/// @}"
        return result.rstrip("\n")

    def GetEnumLiterals(self, classObj):
        if not classObj.IS_ENUM:
            raise RuntimeError("Can't get enum literals from a non-Enum")
        result = ""
        cnt = 0
        for literal in classObj.ENUM_LITERALS:
            result = result + literal + " = " + str(cnt) + ",\n"
            cnt = cnt + 1
        result = result.rstrip(",\n")

        return result

    def GetStructMembers(self, classObj):
        if not classObj.IS_STRUCT:
            raise RuntimeError("Can't get struct members from a non-Struct")
        result = ""
        for attr in classObj.ATTRIBUTES:
            result = result + self.FormatLongComment(attr.USER_COMMENTS)
            type_name = self.GetTypeAndNameFromMultiplicityAndModifier(classObj, attr.TYPE, attr.TYPE_MODIFIER, attr.MULTIPLICITY, attr.NAME)
            result = result + self.InstantiateType(type_name[0], type_name[1], '', classObj.IS_STRUCT_PACKED, False, False)
            result = result + ";\n"
        return result

    def GetPacked(self, classObj, is_begin):
        if not classObj.IS_STRUCT:
            raise RuntimeError("Can't get struct members from a non-Struct")
        result = ""
        if classObj.IS_STRUCT_PACKED:
            if is_begin:
                result = result + "using System;\n"
                result = result + "using System.Runtime.InteropServices;\n\n"
                result = result + "[StructLayout(LayoutKind.Sequential, Pack=1)]\n"
            else:
                pass
        return result

    def GetProjectIncludes(self, setOfProjectDependencies):
        """
        Used in a .csharp project to include other dependant project files :

        <ItemGroup>
            <ProjectReference Include="..\XTestingClassTypes\XTestingClassTypes.csproj" />
            <ProjectReference Include="..\XTestingInheritance\XTestingInheritance.csproj" />
        </ItemGroup>
        """
        result = ""
        if len(setOfProjectDependencies) > 0:
            result = "<ItemGroup>\n"
            for s in setOfProjectDependencies:
                result = result + '    <ProjectReference Include="..\\' + s + '\\' + s + '.csproj" />\n'
            result = result + "</ItemGroup>\n"
        return result

def _filterOutTypesNotInModel(namespace_to_classes, classDiagram):
    """
    Will filter out class names in the 'namespace_to_classes' structure that do not exist in the class diagram.

    @param namespace_to_classes: a dictionary of lists - {"XNameSpace1::XNameSpace2":[Class1, Class2, Class3]}
    @param classDiagram: vppclassdiagram.ClassDiagram

    """
    namespace_to_classes_only_in_model = {}
    for ns, classes in namespace_to_classes.items():
        new_classes = []
        for c in classes:
            for id, pc in classDiagram.classes.items():
                if pc.NAME == c:
                    new_classes.append(c)
        if len(new_classes) > 0:
            namespace_to_classes_only_in_model[ns] = new_classes
    return namespace_to_classes_only_in_model


def _getFormatNestedNamespaceBegin(fullyQualifiedNamespace):
    """
    Returns the C++ format string for a nested namespace declaration on one line...
    @param fullyQualifiedNamespace: a string i.e. "XNamespace1::XNamespace2::CClass"
    @return: string i.e. "namespace XFullStack { namespace XProtocol {"
    """
    # Nested NAMESPACE of the classobj is i.e. 'XFullStack::XProtocol'
    nestedNS = fullyQualifiedNamespace.split("::")
    result = ""
    for n in nestedNS:
         result = result + " namespace " + n + " { "
    result = result.lstrip(" ")
    return result


def _getFormatNestedNamespaceEnd(fullyQualifiedNamespace):
    """
    Returns the C++ format string for a nested namespace end-declaration on one line...
    @param fullyQualifiedNamespace: a string i.e. "XNamespace1::XNamespace2::CClass"
    @return: string i.e. for "namespace XFullStack { namespace XProtocol {" will return "} }"
    """
    # Nested NAMESPACE of the classobj is i.e. 'XFullStack::XProtocol'
    nestedNS = fullyQualifiedNamespace.split("::")
    result = ""
    for n in nestedNS:
        result = result + " } "
    result = result.lstrip()
    return result


def _getIncludeStringFromNamespaceToClassMap(namespace_to_class, namespace_to_folders):
    result = ""
    for path, classnames in namespace_to_class.items():
        for classname in classnames:
            if not namespace_to_folders:  # clear the path
                path = ""
            result = result + '#include "' + path + classname + ".h" + '"\n'
    return result


def _getNamespaceToClassesFromFullyQualifiedNames(classObj, setOfClasses, is_file_include):
    """
    In the ClassDiagramModel, all Types are full qualified, ie 'XFullStack::XProtocol::CProtocolStack'
    It is thus safe to assume that should one split on ::, if the result is one, there is no namespace.

    @param setOfClasses: Set of all classes extracted for classObj
    @param classObj:
    @return: dictionary {'NS1::NS2':'CClass'}
    """
    namespace_to_class = OrderedDict()
    # Get a dictionary of namespace names, with all classes within.
    for f in setOfClasses:
        if is_file_include:
            # If a class is in the same namespace...then it is in the same folder...so clean this first.
            f = f.replace(classObj.NAMESPACE + "::", "")
        full = f.split("::")
        ns = f.replace(full[-1], "")
        if is_file_include:  # when using this for include files, switch :: with /
            ns = ns.replace("::", "/")
        else:  # when using this for forward declarations, the extra '::' creates an empty namespace.
            ns = ns.rstrip("::")
        if ns not in namespace_to_class:
            namespace_to_class[ns] = []
        namespace_to_class[ns].append(full[-1])
    return namespace_to_class

