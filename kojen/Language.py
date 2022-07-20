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
import time
import datetime
import sys


class Language:


    # Apparently these vars are static.
    Lang = None

    # The last created language is the currently generated one...
    def __init__(self):
        Language.Lang = self

    def HasDefault(self, member_tuple) -> bool:
        """
        Returns true if a tuple (representing a member) has a default
        """
        return len(member_tuple) >= 3 and member_tuple[2]

    # ------------------------------ Begin : Language Specifics
    # Braces
    def OpenBrace(self):
        raise RuntimeError("Language Feature Not Implemented")

    def CloseBrace(self):
        raise RuntimeError("Language Feature Not Implemented")

    # White space
    def WhiteSpace(self, indentationlevels):
        return (indentationlevels+1)*'    '

    # Connection type
    def ConnectionType(self):
        raise RuntimeError("Language Feature Not Implemented")

    def ConnectionTypePtr(self):
        raise RuntimeError("Language Feature Not Implemented")

    # Member access / dereference
    def Accessor(self, is_ptr):
        raise RuntimeError("Language Feature Not Implemented")

    # Bytestream access / dereference
    def BytestreamAccessor(self):
        raise RuntimeError("Language Feature Not Implemented")

    # Byte Stream
    def ByteStreamType(self):
        raise RuntimeError("Language Feature Not Implemented")

    def ByteStreamTypeSharedPtr(self):
        raise RuntimeError("Language Feature Not Implemented")

    def ByteStreamTypeRawPtr(self):
        raise RuntimeError("Language Feature Not Implemented")

    # Convenience
    def MessageDescriptor(self, interface, struct):
        return "" if interface.GetMessageTypeIDStr(struct) == "" else " [ MsgTypeID = " + interface.GetMessageTypeIDStr(struct) + " ]"

    def SharedPtrToType(self, typename):
        raise RuntimeError("Language Feature Not Implemented")

    def PtrToTypeName(self, typename):
        return ""

    def GetFactoryCreateParams(self, struct, interface, with_defaults=False) -> list:
        raise RuntimeError("Language Feature Not Implemented")

    def DeclareStructMembers(self, struct, interface, whitespace, attr_packed=True) -> list:
        raise RuntimeError("Language Feature Not Implemented")

    def InstantiateStructMembers(self, struct, interface, whitespace, instancename, accessor) -> list:
        raise RuntimeError("Language Feature Not Implemented")

    def RawPtrToType(self, typename):
        raise RuntimeError("Language Feature Not Implemented")

    def TypedefSharedPtrToType(self, typename, newtypename):
        raise RuntimeError("Language Feature Not Implemented")

    def TypedefRawPtrToType(self, typename, newtypename):
        raise RuntimeError("Language Feature Not Implemented")

    # Packedness
    def AddAttributePackedToDecl(self, declaration):
        raise RuntimeError("Language Feature Not Implemented")

    def InstantiatePtrToType(self, typepointername, instancename, typename):
        raise RuntimeError("Language Feature Not Implemented")

    def InstantiateArray(self, instancename, typename, noelements):
        raise RuntimeError("Language Feature Not Implemented")

    def DeleteArray(self, instancename):
        raise RuntimeError("Language Feature Not Implemented")

    def DeletePtrToType(self, instancename):
        raise RuntimeError("Language Feature Not Implemented")

    ''' Instantiate/declare a basic type, with optional initializer. Only declarations can use 'attribute packed' directives.
        use typename = '' to make it a known variable initialization
    '''
    def InstantiateType(self, typename, instancename, initialevalue='', is_attr_packed=False, is_static=False, is_const=False) -> str:
        raise RuntimeError("Language Feature Not Implemented")

    # parameters need to be a list of (type, name).
    def DeclareFunction(self, returntype, classname, functionname, is_impl, parameters=None, virtual=False, is_static=False, is_const=False) -> str:
        raise RuntimeError("Language Feature Not Implemented")

    def DeclareClass(self, classname, declspec=''):
        raise RuntimeError("Language Feature Not Implemented")

    def ForwareDeclareClass(self, classname):
        raise RuntimeError("Language Feature Not Implemented")

    def DeclareStruct(self, structname, declspec=''):
        raise RuntimeError("Language Feature Not Implemented")

    def DeclareEnum(self, enum, whitespace):
        raise RuntimeError("Language Feature Not Implemented")

    def DeclareHashDefine(self, name, val):
        raise RuntimeError("Language Feature Not Implemented")

    def DeclareNamespace(self, namespacename):
        raise RuntimeError("Language Feature Not Implemented")

    def UsingNamespace(self, namespacename):
        raise RuntimeError("Language Feature Not Implemented")

    def FormatComment(self, commenttext):
        raise RuntimeError("Language Feature Not Implemented")

    def FormatLongComment(self, commenttext):
        raise RuntimeError("Language Feature Not Implemented")

    # The includes that each generated file needs to have from the provided mini framework
    def LanguageSpecificFrameWorkIncludes(self):
        raise RuntimeError("Language Feature Not Implemented")

    def AddInclude(self, filename):  # for python we can simply replace .h with''
        raise RuntimeError("Language Feature Not Implemented")

    def PrintError(self, message):  # python should split the strings by '<<', as there are more arguments passed this way
        raise RuntimeError("Language Feature Not Implemented")

    def PrintMessage(self, message):
        raise RuntimeError("Language Feature Not Implemented")

    def BooleanTrue(self):
        raise RuntimeError("Language Feature Not Implemented")

    def BooleanFalse(self):
        raise RuntimeError("Language Feature Not Implemented")

    def NullPtr(self):  # should be NULL for C, and None for pooota
        raise RuntimeError("Language Feature Not Implemented")

    def PublicAccessSpecifier(self):
        raise RuntimeError("Language Feature Not Implemented")

    def ProtectedAccessSpecifier(self):
        raise RuntimeError("Language Feature Not Implemented")

    def PrivateAccessSpecifier(self):
        raise RuntimeError("Language Feature Not Implemented")

    def If(self, statement):
        raise RuntimeError("Language Feature Not Implemented")

    def ElseIf(self, statement):
        raise RuntimeError("Language Feature Not Implemented")

    def Else(self):
        raise RuntimeError("Language Feature Not Implemented")

    def This(self):
        raise RuntimeError("Language Feature Not Implemented")

    def ParameterString(self,  parameters=None) -> str:
        raise RuntimeError("Language Feature Not Implemented")

    # 1 means ++
    def For_Range(self, start, stop, incr=1):
        raise RuntimeError("Language Feature Not Implemented")

    def LicenseAgreement(self):
        result = []
        result.append("--------------------------------------------------------------------------------")
        result.append("")
        result.append('    ' + "MIT License")
        result.append("")
        result.append('    ' + "Copyright (c) 2015 Eugene Grobbelaar (email : koh.jaen@yahoo.de)")
        result.append("")
        result.append('    ' + "Permission is hereby granted, free of charge, to any person obtaining a copy")
        result.append('    ' + 'of this software and associated documentation files (the "Software"), to deal')
        result.append('    ' + "in the Software without restriction, including without limitation the rights")
        result.append('    ' + "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell")
        result.append('    ' + "copies of the Software, and to permit persons to whom the Software is")
        result.append('    ' + "furnished to do so, subject to the following conditions:")
        result.append("")
        result.append('    ' + "The above copyright notice and this permission notice shall be included in all")
        result.append('    ' + "copies or substantial portions of the Software.")
        result.append("")
        result.append('    ' + 'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR')
        result.append('    ' + "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,")
        result.append('    ' + "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE")
        result.append('    ' + "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER")
        result.append('    ' + "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,")
        result.append('    ' + "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE")
        result.append('    ' + "SOFTWARE.")
        result.append("")
        result.append("--------------------------------------------------------------------------------")
        result.append('        ' + "This file was generated on    : " + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + ".")
        result.append('        ' + "This file was generated using : " + sys.platform + ".")
        result.append('        ' + "This file was generated by a machine. Do not modify it by hand.")
        result.append("")
        result.append("--------------------------------------------------------------------------------")
        return result

    ''' Additions that were added for class diagram
    '''
    def GetFormatNestedNamespaceBegin(self, classObj):
        raise RuntimeError("Language Feature Not Implemented")

    def GetFormatNestedNamespaceEnd(self, classObj):
        raise RuntimeError("Language Feature Not Implemented")

    def GetFormatClassInheritence(self, classObj, dictOfInheritance):
        raise RuntimeError("Language Feature Not Implemented")

    # Typically what goes into a H file, when the items can NOT be forward declared in H file.
    def GetNotForwardDeclarableHeaderIncludes(self, classObj, namespace_to_folders = False, filter_out_type_not_in_model = False, include_vector_if_needed = False):
        raise RuntimeError("Language Feature Not Implemented")

    # Typically what goes into a CPP file, when the items can be forward declared in H file.
    def GetForwardDeclarableHeaderIncludes(self, classObj, classDiagram):
        raise RuntimeError("Language Feature Not Implemented")

    # Typically what goes into a H file, when the items can be forward declared in H file.
    def GetForwardDeclarations(self, classObj, classDiagram):
        raise RuntimeError("Language Feature Not Implemented")

    # Typically what goes into a H file...to determine the language types to be used for multiplicity
    def GetTypeAndNameFromMultiplicityAndModifier(self, TYPE, TYPE_MODIFIER, MULTIPLICITY, NAME):
        raise RuntimeError("Language Feature Not Implemented")

    # Typically what goes into a H file...Get the declaration string for all attributes of the desired visibility
    def GetAttributeDeclarationsPerVisibility(self, classObj, visibility="all"):
        raise RuntimeError("Language Feature Not Implemented")

    # Typically what goes into a H file...Get the declaration string for all associations of the desired visibility
    def GetAssociationDeclarationsPerVisibility(self, classObj, visibility="all"):
        raise RuntimeError("Language Feature Not Implemented")

    # Will get the declaration string for all attributes of the following visibility
    # - public
    # - protected
    # - private
    # - all (public and protected and private)
    def GetAttributeDeclarationsPerVisibility(self, classObj, visibility="all"):
        raise RuntimeError("Language Feature Not Implemented")

    # Will get the declaration string for all attributes of the following visibility
    # - public
    # - protected
    # - private
    # - all (public and protected and private)
    def GetAssociationDeclarationsPerVisibility(self, classObj, visibility="all"):
        raise RuntimeError("Language Feature Not Implemented")

    # Typically what goes into a CPP file...static declared attributes need to be defined somewhere else.
    def GetStaticAttributeDefinitions(self, classObj):
        raise RuntimeError("Language Feature Not Implemented")

    # Typically what goes into a CPP file...static declared associations need to be defined somewhere else.
    def GetStaticAssociationDefinitions(self, classObj):
        raise RuntimeError("Language Feature Not Implemented")

    def GetOperationPerVisibility(self, classObj, is_impl, visibility="all"):
        raise RuntimeError("Language Feature Not Implemented")

    def GetAttributeAssociationGetterSetter(self, classObj, is_impl=False):
        raise RuntimeError("Language Feature Not Implemented")

    def GetEnumLiterals(self, classObj):
        raise RuntimeError("Language Feature Not Implemented")

    def GetStructMembers(self, classObj):
        raise RuntimeError("Language Feature Not Implemented")

    def GetConstructor(self, classobj, is_impl=False):
        raise RuntimeError("Language Feature Not Implemented")

    def GetProjectIncludes(self, setOfProjectDependencies):
        raise RuntimeError("Language Feature Not Implemented")
    # ------------------------------ End
