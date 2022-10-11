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
from .Language import *


class LanguagePython(Language):

    ## Language Specifics
    # Braces
    def OpenBrace(self):
        return ''

    def CloseBrace(self):
        return ''

    # Connection type
    def ConnectionType(self):
        return 'IConnection'

    def ConnectionTypePtr(self):
        return 'IConnection'

    # Member access / dereference
    def Accessor(self, is_ptr):
        return '.'

    # Bytestream access / dereference
    def BytestreamAccessor(self):
        return '.'

    # Byte Stream
    def ByteStreamType(self):
        return 'bytearray'

    def ByteStreamTypeSharedPtr(self):
        return self.SharedPtrToType(self.ByteStreamType())

    def ByteStreamTypeRawPtr(self):
        return self.RawPtrToType(self.ByteStreamType())

    # Convenience
    def SharedPtrToType(self, typename):
        return typename

    def RawPtrToType(self, typename):
        return typename

    def TypedefSharedPtrToType(self, typename, newtypename):
        return ''

    def TypedefRawPtrToType(self, typename, newtypename):
        return ''

    def GetFactoryCreateParams(self, struct, interface, with_defaults=False) -> list:
        structmembers = struct.Decompose()
        factoryparams = []
        for mem in structmembers:
            #isArray = struct.IsArray(mem[1])
            #isMessage = interface.IsMessageStruct(mem[0])
            #isStruct = struct.IsStruct(mem[1])
            if not interface.IsProtocolStruct(mem[0]):
                if with_defaults and self.HasDefault(mem):
                    factoryparams.append(("", mem[1] + "=" + mem[2]))
                else:
                    factoryparams.append(("", mem[1]))
        return factoryparams

    '''Declares the guts of a struct declaration
    '''
    def DeclareStructMembers(self, struct, interface, whitespace, attr_packed=True) -> list:
        arrayName = []
        structmembers = struct.Decompose()
        result = []
        for mem in structmembers:
            if not struct.IsArray(mem[1]):
                result.append(whitespace + self.InstantiateType(mem[0], mem[1], mem[2] if self.HasDefault(mem) else 'None') + ' # ' + mem[0])
            else:
                result.append(whitespace + self.InstantiateType(mem[0], mem[1]) + ' # ' + mem[0] + '[]')

            if struct.IsArray(mem[1]):
                arrayName.append(mem[1])
        return result

    # Packedness
    def AddAttributePackedToDecl(self, declaration):
        # http://stackoverflow.com/questions/14771150/python-ctypes-pragma-pack-for-byte-aligned-read
        return '_pack_ = 1'

    def InstantiatePtrToType(self, typename, instancename):
        return instancename + ' = ' + typename + '()'

    def InstantiateArray(self, instancename, typename, noelements):
        return instancename + ' = ' + typename + '('+noelements+')\n'

    def DeleteArray(self, instancename):
        return 'del ' + instancename + '\n'

    def DeletePtrToType(self, instancename):
        return 'del ' + instancename + '\n'

    ''' Instantiate/declare a basic type, with optional initializer. Only declarations can use 'attribute packed' directives.
        use typename = '' to make it a known variable initialization
    '''
    def InstantiateType(self, typename, instancename, initialevalue='None', is_attr_packed=False, is_static=False, is_const=False):
        # declaration...i.e. in class or struct. no initial value, can be packed
        # if initialevalue.replace(' ','') == '':
        #    decl =  "('" + instancename + "'," + typename + ")"
        #    return decl + ',\n'

        # local variable decl/instantiation or known variable instantiation
        return instancename + ' = ' + initialevalue

    def InstantiateStructMembers(self, struct, interface, whitespace, instancename, accessor) -> list:
        structmembers = struct.Decompose()
        result = []
        for mem in structmembers:
            isArray = struct.IsArray(mem[1])
            isStruct = interface.IsStruct(mem[1])
            isProtocol = interface.IsProtocolStruct(mem[0])
            instance_accessor = whitespace + instancename + accessor

            if not isArray and (not isProtocol or isStruct):
                result.append(instance_accessor + self.InstantiateType('', mem[1], mem[1]))
            elif not isArray and isProtocol and not isStruct:
                raise RuntimeError("C++ Copy Paste -> Language Feature Not Implemented")
            elif isArray and not isProtocol and not isStruct:
                raise RuntimeError("C++ Copy Paste -> Language Feature Not Implemented")
            else:
                print("WTF : InstantiateStructMembers")

        return result

    def ParameterString(self,  parameters=None) -> str:
        if parameters is None:
            parameters = []

        if str(type(parameters)) == "<type 'list'>" or str(type(parameters)) == "<class 'list'>":  # Python2 gives the first, python3 the second!
            parameter_string = ''
            size = len(parameters)
            cnt = 0
            for param in parameters:
                parameter_string += param[1]
                if cnt != (size - 1):
                    parameter_string += ', '
                cnt += 1
            return parameter_string

        raise Exception("Please use OrderedDict when passing parameters into 'ParameterString'")

    # parameters need to be a list of (type, name).
    def DeclareFunction(self, returntype, classname, functionname, is_impl, parameters=None, virtual=False, is_static=False, is_const=False):
        # def DeclareFunction(self, returntype, classname, functionname, is_impl, parameters=[], virtual=False):
        # https://florimond.dev/blog/articles/2018/08/python-mutable-defaults-are-the-source-of-all-evil/
        if parameters is None:
            parameters = []
        if not is_impl:
            return ''

        if str(type(parameters)) == "<type 'list'>" or str(type(parameters)) == "<class 'list'>":  # Python2 gives the first, python3 the second!
            parameter_string = ''

            size = len(parameters)
            cnt = 0
            for param in parameters:
                parameter_string += param[1]
                if cnt != (size - 1):
                    parameter_string += ', '
                cnt += 1

            return 'def ' + functionname + '(' + parameter_string + ')' + ':'

        raise Exception("Please use list when passing parameters into 'DeclareFunction'")

    def DeclareClass(self, classname, declspec=''):
        return 'class ' + classname + ':\n'

    def ForwareDeclareClass(self, classname):
        return ''

    def DeclareStruct(self, structname, declspec=''):
        """c-type structs here
        # http://stackoverflow.com/questions/14771150/python-ctypes-pragma-pack-for-byte-aligned-read
        """
        result = 'class ' + structname + '(Structure):\n'
        result += self.AddAttributePackedToDecl('') + '\n'
        result += '_fields_ = [\n'
        return result

    def DeclareEnum(self, enum, whitespace) -> str:
        result = self.FormatComment(enum.documentation) + "\n"
        result += whitespace + "@unique\n"
        result += whitespace + "class " + enum.Name + "(Enum):\n"
        for descriptionName, val in enum.items():
            result += whitespace*2 + str(descriptionName) + " = " + str(val) + "\n"
        return result

    def DeclareNamespace(self, namespacename):
        return '\n'

    def UsingNamespace(self, namespacename):
        return '\n'

    #def DeclareClassConstructor(self, classname, is_impl, parameters = OrderedDict()):

    def FormatComment(self, commenttext):
        return '# ' + commenttext

    def FormatLongComment(self, commenttext):
        return "'''" + commenttext + "'''\n"

    # The includes that each generated file needs to have from the provided mini framework
    def LanguageSpecificFrameWorkIncludes(self):
        return ['ctypes']

    def AddInclude(self, filename):  # for python we can simply replace .h with''
        return 'from ' + filename.replace('.py', '').replace('"', '').replace('<', '').replace('>', '').replace('\n', '') + ' import *\n'

    def PrintError(self, message):  # python should split the strings by '<<', as there are more arguments passed this way
        return self.PrintMessage("ERROR : " + message)

    def PrintMessage(self, message):
        result = 'print ('
        for i in message.split("<<"):
            result += "+ str(" + i + ")"
        result += ')\n'
        return result

    def BooleanTrue(self):
        return 'True'

    def BooleanFalse(self):
        return 'False'

    def NullPtr(self):  # should be NULL for C, and None for pooota
        return 'None'

    def PublicAccessSpecifier(self):
        return ''

    def ProtectedAccessSpecifier(self):
        return ''

    def PrivateAccessSpecifier(self):
        return ''

    def If(self, statement):
        return 'if '+statement+' :\n'

    def ElseIf(self, statement):
        return 'elif '+statement+' :\n'

    def Else(self):
        return 'else:\n'

    def This(self):
        return 'self.'

    # 1 means ++
    def For_Range(self, iterName, iterType, start, stop, incr=1) -> str:
        if incr == 1:
            return 'for ' + iterName + ' in range(' + str(start) + ',' + str(stop) + '):'
        return 'for ' + iterName + ' in range (' + str(start) + ',' + str(stop) + ',' + str(incr) + '):'

    # Python special functions
    def DeclareDataFormatFunction(self, struct, interface, whitespace, formatfunction):
        structmembers = struct.Decompose()
        result = []
        result.append(whitespace + "# Binary data format")
        result.append(whitespace + "@staticmethod")
        hasArray = False
        if interface.IsMessageStruct(struct.Name):
            hasArray = struct.HasArray()
        if not hasArray:
            result.append(whitespace + self.DeclareFunction(struct.Name, "", "BinaryDataFormat", True, []))
        else:
            result.append(whitespace + self.DeclareFunction(struct.Name, "", "BinaryDataFormat", True, [('actual', 'actual')]) + " # Has array, needs actual count.")

        result.append(whitespace + self.WhiteSpace(0) + 'result = ""')
        for mem in structmembers:
            isArray = struct.IsArray(mem[1])
            isStruct = struct.IsStruct(mem[1])
            isProtocol = interface.IsProtocolStruct(mem[0])
            if isStruct or isProtocol:
                result.append(whitespace + self.WhiteSpace(0) + 'result += ' + mem[0] + '.BinaryDataFormat()' + "# " + mem[0] + ' - ' + mem[1])
            elif isArray:
                if interface.IsStruct(mem[0]):
                    result.append(whitespace + self.WhiteSpace(0) + 'for i in range(actual.' + mem[1] + '_Cnt):' + "# " + mem[0] + ' - ' + mem[1])
                    result.append(whitespace + self.WhiteSpace(1) + 'result += ' + mem[0] + '.BinaryDataFormat()')
                else:
                    result.append(whitespace + self.WhiteSpace(0) + 'result += str(actual.' + mem[1] + "_Cnt) + " + formatfunction + '("' + mem[0] + '")' + "# " + mem[0] + ' - ' + mem[1])
            else:
                result.append(whitespace + self.WhiteSpace(0) + 'result += '+formatfunction+'("' + mem[0] + '")' + "# " + mem[0] + ' - ' + mem[1])
        result.append(whitespace + self.WhiteSpace(0) + 'return "="+result.replace("=","") # "=" for no padding...only need the first one, this removes nested "="\n')
        return result

    def DeclareDataSizeFunction(self, struct, interface, whitespace):
        result = []

        hasArray = False
        if interface.IsMessageStruct(struct.Name):
            hasArray = struct.HasArray()

        structmembers = struct.Decompose()

        result.append(whitespace + "# Binary data size")
        result.append(whitespace + "@staticmethod")
        if hasArray:
            result.append(whitespace + self.DeclareFunction(struct.Name, '', "SizeOf", True, [('actual = None', 'actual = None')]))
            result.append(whitespace + self.WhiteSpace(0) + 'if None == actual: # Factory create will calculate correctly')
            result.append(whitespace + self.WhiteSpace(1) + self.InstantiatePtrToType(struct.Name, 'actual'))
            for mem in structmembers:
                if mem[1].find('_Cnt') > -1:
                    result.append(whitespace + self.WhiteSpace(1) + 'actual.' + mem[1] + ' = 1')
            result.append(whitespace + self.WhiteSpace(0) + 'return calcsize(' + struct.Name + '.BinaryDataFormat(actual))\n')
        else:
            result.append(whitespace + self.DeclareFunction(struct.Name, '', "SizeOf", True, []))
            result.append(whitespace + self.WhiteSpace(0) + 'return calcsize(' + struct.Name + '.BinaryDataFormat())\n')
        return result

    # ------------------------------ End
