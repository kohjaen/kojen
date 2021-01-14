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
import datetime
import sys
import time
from string import Template

try:
    from interface_base import *
except (ModuleNotFoundError, ImportError) as e:
    from .interface_base import *

try:
    from vppclassdiagram import *
except (ModuleNotFoundError, ImportError) as e:
    from .vppclassdiagram import *


class UnitTestFramework:
    NO_FW, BOOST, CPPuTEST = range(3)


class UnitTestWriter:

    def __init__(self, interface, message, language, instancename):
        self.message = message
        self.interface = interface
        self.language = language
        self.instancename = instancename
        self.bytestream_of_message_variable_name = instancename + '_stream'

    ''' Returns a tuple([list of lines],[list of pointers to delete after])
    '''
    def WRITE_CREATE_MESSAGE(self, WHITESPACE='\t\t'):

        if not self.interface.IsMessageStruct(self.message.Name):
            raise RuntimeError("Wrong type error. Must be message (" + self.message.Name)

        result = []
        result_delete = []
        creation_string = ''
        message = self.message
        interface = self.interface
        language = self.language
        instancename = self.instancename

        hasArray = message.HasArray()
        ignoreArrayCntName = ""
        if hasArray:
            for mem in message:
                if message.IsArray(mem):
                    ignoreArrayCntName = message[mem].Count()

        messagemembers = message.Decompose()
        for i in range(len(messagemembers)):
            mem = messagemembers[i]
            isArray = message.IsArray(mem[1])
            isStruct = message.IsStruct(mem[1])
            # Also ignore this member size, as its compensated for
            # in the payload (we send the data, not the pointer...
            isProtocol = message.IsProtocolStruct(mem[1])

            ''' Embedded struct support (i.e. user typed data)
                Don't create a declaration for the protocol...this we can do automatically with
                provided info
            '''
            if isStruct and not isArray:
                # Decompose by the message struct
                struct = interface[mem[0]]
                struct_instance_name = language.PtrToTypeName(message.Name) + '__' + mem[1]
                # result_delete.append(struct_instance_name) -> this wont be a pointer.
                struct_creation_string = ''
                struct_creation_string += 'Create_' + struct.Name + '('
                structmembers = struct.Decompose()
                for j in range(len(structmembers)):
                    smem = structmembers[j]
                    struct_creation_string += '(' + smem[0] + ') 1'
                    if j != len(structmembers) - 1:
                        struct_creation_string += ","
                struct_creation_string += ')'
                # Write embedded type creation string before interface type creation string
                result.append(WHITESPACE + language.InstantiateType(struct.Name, struct_instance_name, struct_creation_string) + ";")
                creation_string += struct_instance_name
            elif isArray:
                array = message[mem[1]]
                creation_string += '(' + array[array.Count()] + ' )50,' + language.NullPtr()  # Don't copy, just create empty buffer...
            elif isProtocol:
                pass
            elif mem[1] == ignoreArrayCntName:
                pass
            else:  # Normal type
                creation_string = creation_string + '(' + mem[0] + ') 1'

            if not isProtocol and not mem[1] == ignoreArrayCntName:
                if i != len(messagemembers) - 1:
                    creation_string = creation_string + ","

        # Write interface type creation string
        result_delete.append(instancename)
        result.append(WHITESPACE + language.InstantiateType(language.PtrToTypeName(message.Name), instancename, 'Create_' + message.Name + '(' + creation_string + ');'))
        return result, result_delete

    def WRITE_MESSAGE_TO_STREAM(self, WHITESPACE='\t\t', is_arm=False, unittestfw=UnitTestFramework.NO_FW):
        if not self.interface.IsMessageStruct(self.message.Name):
            raise RuntimeError("Wrong type error. Must be message (" + self.message.Name)

        result = []
        message = self.message
        interface = self.interface
        language = self.language
        instancename = self.instancename
        accessor = language.Accessor(True)
        bytestream_of_message_variable_name = instancename + '_stream'
        # Array require pre-initialization
        if message.HasArray():
            result.append(WHITESPACE + language.FormatComment('Has array data needing testing.'))
            messagemembers = message.Decompose()
            for mem in messagemembers:
                isArray = message.IsArray(mem[1])
                isStruct = interface.IsStruct(mem[0])
                if isArray:
                    result.append(WHITESPACE + language.For_Range('0', '50') + language.OpenBrace())
                    if not isStruct:
                        result.append(WHITESPACE + language.WhiteSpace(0) + language.InstantiateType('', instancename + accessor + mem[1] + '[i]', 'i')+";")
                    elif isStruct:
                        structmembers = interface[mem[0]].Decompose()
                        for smem in structmembers:
                            result.append(WHITESPACE + language.WhiteSpace(0) + language.InstantiateType('', instancename + accessor + mem[1] + '[i].' + smem[1], 'i')+";")
                    result.append(WHITESPACE + language.CloseBrace())

        # To Stream
        if is_arm:
            result.append(WHITESPACE + 'uint8 ' + bytestream_of_message_variable_name + "[sizeof(" + message.Name + ")];")
            result.append(WHITESPACE + 'size_t serialized_size = ToByteStream_' + message.Name + '(' + instancename + ', ' + bytestream_of_message_variable_name + ')' + ";")
            if unittestfw == UnitTestFramework.NO_FW:
                result.append(WHITESPACE + 'assert(serialized_size == sizeof('+message.Name+'));')
            elif unittestfw == UnitTestFramework.BOOST:
                result.append(WHITESPACE + 'BOOST_REQUIRE_MESSAGE(serialized_size == sizeof('+message.Name+'), "ERROR : Serialized size of ' + message.Name + ' is not as expected.");')
            elif unittestfw == UnitTestFramework.CPPuTEST:
                result.append(WHITESPACE + 'CHECK_EQUAL_TEXT(serialized_size,sizeof('+message.Name+'), "ERROR : Serialized size of ' + message.Name + ' is not as expected.");')
            else:
                result.append(WHITESPACE + "// Incorrect option " + str(unittestfw) + " for TOBYTESTREAM, please see options in class UnitTestFramework")

        else:
            result.append(WHITESPACE + language.InstantiateType(language.ByteStreamTypeSharedPtr(), bytestream_of_message_variable_name, 'ToByteStream_' + message.Name + '(' + instancename + ')')+";")
        return result

    ''' Returns a tuple([list of lines],[list of pointers to delete after])
    '''
    def WRITE_MESSAGE_FROM_STREAM(self, WHITESPACE='\t\t', is_arm=False, unittestfw=UnitTestFramework.NO_FW):

        if not self.interface.IsMessageStruct(self.message.Name):
            raise RuntimeError("Wrong type error. Must be message (" + self.message.Name)

        result = []
        result_delete = []
        message = self.message
        interface = self.interface
        language = self.language
        instancename = self.instancename
        bytestream_of_message_variable_name = self.bytestream_of_message_variable_name
        message_variable_name_after_ser = instancename + '_fromstream'
        result_delete.append(message_variable_name_after_ser)
        accessor = language.Accessor(True)

        # From Stream
        indexer = 'i_'+bytestream_of_message_variable_name
        result.append(WHITESPACE + language.InstantiateType('size_t', indexer, '0') + ";")
        if is_arm:
            result.append(WHITESPACE + language.InstantiateType(language.PtrToTypeName(message.Name), message_variable_name_after_ser, 'FromByteStream_' + message.Name + '( &' + bytestream_of_message_variable_name + '[0], serialized_size, ' + indexer + ')') + ";")
        else:
            result.append(WHITESPACE + language.InstantiateType(language.PtrToTypeName(message.Name), message_variable_name_after_ser, 'FromByteStream_' + message.Name + '( &(*'+bytestream_of_message_variable_name + ')[0], ' + bytestream_of_message_variable_name + '->size(), '+indexer+')')+";")
        # Make sure the indexer matches the streamsize
        result.append(WHITESPACE + language.FormatComment('Index should be at next (non existant) place (thus streamsize).'))
        if is_arm:
            if unittestfw == UnitTestFramework.NO_FW:
                result.append(WHITESPACE + language.If(indexer + ' != serialized_size'))
                result.append(WHITESPACE + language.OpenBrace())
                result.append(WHITESPACE + language.WhiteSpace(0) + language.PrintError('"ERROR : Indexing count %i not match the stream %i ..." ,' + indexer + ',serialized_size'))
            elif unittestfw == UnitTestFramework.BOOST:
                result.append(WHITESPACE + 'BOOST_REQUIRE_MESSAGE('+indexer+' == serialized_size, "ERROR : Indexing count does not match the stream size.");')
            elif unittestfw == UnitTestFramework.CPPuTEST:
                result.append(WHITESPACE + 'CHECK_EQUAL_TEXT('+indexer+',serialized_size, "ERROR : Indexing count does not match the stream size.");')
            else:
                result.append(WHITESPACE + "// Incorrect option " + str(unittestfw) + " for FROMBYTESTREAMINDEX, please see options in class UnitTestFramework")
        else:
            if unittestfw == UnitTestFramework.NO_FW:
                result.append(WHITESPACE + language.If(indexer+' != '+bytestream_of_message_variable_name+'->size()'))
                result.append(WHITESPACE + language.OpenBrace())
                result.append(WHITESPACE + language.WhiteSpace(0) + language.PrintError('"ERROR : Indexing count %i not match the stream %i ..." ,' + indexer + ',' + bytestream_of_message_variable_name + '->size()'))
            elif unittestfw == UnitTestFramework.BOOST:
                result.append(WHITESPACE + 'BOOST_REQUIRE_MESSAGE('+indexer+' == '+bytestream_of_message_variable_name+'->size(), "ERROR : Indexing count does not match the stream size.");')
            elif unittestfw == UnitTestFramework.CPPuTEST:
                result.append(WHITESPACE + 'CHECK_EQUAL_TEXT('+indexer+','+bytestream_of_message_variable_name+'->size(), "ERROR : Indexing count does not match the stream size.");')
            else:
                result.append(WHITESPACE + "// Incorrect option " + str(unittestfw) + " for FROMBYTESTREAMINDEX, please see options in class UnitTestFramework")

        if unittestfw == UnitTestFramework.NO_FW:
            result.append(WHITESPACE + language.WhiteSpace(0) + 'return false;')
            result.append(WHITESPACE + language.CloseBrace())
        # Make sure all fields are equal...
        equality_check = 'b_'+bytestream_of_message_variable_name+'_equal'
        result.append(WHITESPACE + language.InstantiateType('bool', equality_check, 'true') + ";")

        messagemembers = message.Decompose()

        for mem in messagemembers:
            membername = mem[1]
            #membertype = str(self.m_struct_members.m_member_type[i])
            isArray = message.IsArray(mem[1])
            isStruct = interface.IsStruct(mem[0])
            isProtocol = interface.IsProtocolStruct(mem[0])
            if isStruct or isProtocol:
                struct = interface[mem[0]]
                structmembers = struct.Decompose()
                if isArray:
                    result.append(WHITESPACE + language.For_Range('0', '50'))
                    result.append(WHITESPACE + language.OpenBrace())
                    for smem in structmembers:
                        result.append(WHITESPACE + language.WhiteSpace(0) + equality_check + ' = '+equality_check + ' && '+instancename+accessor+membername+'[i].'+smem[1]+' == '+message_variable_name_after_ser+accessor+membername+'[i].'+smem[1]+';')
                    result.append(WHITESPACE + language.CloseBrace())
                else:
                    for smem in structmembers:
                        result.append(WHITESPACE + equality_check + ' = ' + equality_check + ' && '+instancename+accessor+membername+'.'+smem[1]+' == '+message_variable_name_after_ser+accessor+membername+'.'+smem[1]+';')
            else:
                if isArray:
                    result.append(WHITESPACE + language.For_Range('0', '50'))
                    result.append(WHITESPACE + language.OpenBrace())
                    result.append(WHITESPACE + language.WhiteSpace(0) + equality_check+' = '+equality_check + ' && '+instancename+accessor+membername+'[i] == '+message_variable_name_after_ser+accessor+membername+'[i];')
                    result.append(WHITESPACE + language.CloseBrace())
                else:
                    result.append(WHITESPACE + equality_check + ' = ' + equality_check + ' && '+instancename+accessor+membername+' == '+message_variable_name_after_ser+accessor+membername+';')

        if unittestfw == UnitTestFramework.NO_FW:
            result.append(WHITESPACE + language.If('!' + equality_check))
            result.append(WHITESPACE + language.OpenBrace())
            result.append(WHITESPACE + language.WhiteSpace(0) + language.PrintError('"ERROR : Equality check for '+message.Name+' failed"'))
            result.append(WHITESPACE + language.WhiteSpace(0) + 'return false;')
            result.append(WHITESPACE + language.CloseBrace())
        elif unittestfw == UnitTestFramework.BOOST:
            result.append(WHITESPACE + 'BOOST_REQUIRE_MESSAGE(' + equality_check + ', "ERROR : Equality check for '+message.Name+' failed.");')
        elif unittestfw == UnitTestFramework.CPPuTEST:
            result.append(WHITESPACE + 'CHECK_TEXT(' + equality_check + ', "ERROR : Equality check for '+message.Name+' failed.");')
        else:
            result.append(WHITESPACE + "// Incorrect option " + str(unittestfw) + " for "+message.Name+" EQUALITY CHECK, please see options in class UnitTestFramework")

        return result, result_delete

    def WRITE_UNITTEST_PACKED_STRUCT_SIZE(self, WHITESPACE='\t\t', unittestfw=UnitTestFramework.NO_FW):
        result = []

        struct = self.message
        language = self.language
        interface = self.interface

        struct_name             = struct.Name
        size_struct_name        = 'size_' + struct_name
        size_accum_struct_name  = 'size_accum_' + struct_name

        result.append(WHITESPACE + language.FormatComment('Test ' + ("struct " if language.MessageDescriptor(interface, struct) == "" else "message " + language.MessageDescriptor(interface, struct)) + " " + struct_name + ' packedness'))

        # Start Scope
        result.append(WHITESPACE + language.OpenBrace())

        result.append(WHITESPACE + language.WhiteSpace(0) + language.InstantiateType('size_t', size_struct_name, 'sizeof(' + struct_name + ')') + ";")
        result.append(WHITESPACE + language.WhiteSpace(0) + language.InstantiateType('size_t', size_accum_struct_name, '0') + ";")

        structmembers = struct.Decompose()
        for mem in structmembers:
            membertype = mem[0]
            membername = mem[1]

            result.append(WHITESPACE + language.WhiteSpace(0) + size_accum_struct_name + ' += sizeof(' + membertype + ('*' if struct.IsArray(membername) else '') + '); ' + language.FormatComment(struct_name + '::' + membername + ';'))

        if unittestfw == UnitTestFramework.NO_FW:
            result.append(WHITESPACE + language.WhiteSpace(0) + language.If(size_struct_name + ' != ' + size_accum_struct_name))
            result.append(WHITESPACE + language.WhiteSpace(0) + language.OpenBrace())
            result.append(WHITESPACE + language.WhiteSpace(1) + language.PrintError('"ERROR : Size of ' + struct_name + ' does not equal the sum of its separate parts: %i != %i" ,' + size_struct_name + ',' + size_accum_struct_name))
            result.append(WHITESPACE + language.WhiteSpace(1) + 'return false;')
            result.append(WHITESPACE + language.WhiteSpace(0) + language.CloseBrace())
        elif unittestfw == UnitTestFramework.BOOST:
            result.append(WHITESPACE + language.WhiteSpace(0) + 'BOOST_REQUIRE_MESSAGE(' + size_struct_name + ' == ' + size_accum_struct_name + ', "ERROR : Size of ' + struct_name + ' does not equal the sum of its separate parts.");')
        elif unittestfw == UnitTestFramework.CPPuTEST:
            result.append(WHITESPACE + language.WhiteSpace(0) + 'CHECK_EQUAL_TEXT(' + size_struct_name + ',' + size_accum_struct_name + ', "ERROR : Size of ' + struct_name + ' does not equal the sum of its separate parts.");')
        else:
            result.append(WHITESPACE + language.WhiteSpace(0) + "// Incorrect option " + str(unittestfw) + " for PACKEDNESS, please see options in class UnitTestFramework")

        # End Scope
        result.append(WHITESPACE + language.CloseBrace())

        return result

    def WRITE_DELETERS(self, to_delete, struct_name, WHITESPACE='\t\t', unittestfw=UnitTestFramework.NO_FW):
        language = self.language
        result = []
        result.append("#ifdef __arm__")
        result.append(WHITESPACE + "// ARM doesnt use shared_ptr's, but a custom allocator...Don't leak memory")
        if unittestfw == UnitTestFramework.CPPuTEST:
            result.append(WHITESPACE + 'CHECK_EQUAL_TEXT(' + struct_name + '::GetBlocksInUse(),' + str(len(to_delete)) + ',"ERROR : Somebody is using ' + struct_name + 's without deleting them.");')
            for delete in to_delete:
                result.append(WHITESPACE + "delete " + delete + ";")
            result.append(WHITESPACE + 'CHECK_EQUAL_TEXT(' + struct_name + '::GetBlocksInUse(),0,"ERROR : Somebody is using ' + struct_name + 's without deleting them (2).");')
            result.append(WHITESPACE + 'CHECK_EQUAL_TEXT(' + struct_name + '::GetAllocations(),' + struct_name + '::GetDeallocations(),"ERROR : Somebody is using ' + struct_name + 's without deleting them (3).");')
        else:
            result.append(WHITESPACE + "if(" + struct_name + "::GetBlocksInUse() != " + str(len(to_delete)) + ")")
            result.append(WHITESPACE + language.WhiteSpace(0) + language.PrintError('"ERROR : Somebody is using ' + struct_name + 's without deleting them.'))
            for delete in to_delete:
                result.append(WHITESPACE + 'delete ' + delete + ';')
            result.append(WHITESPACE + 'if(' + struct_name + '::GetBlocksInUse() != 0)')
            result.append(WHITESPACE + language.WhiteSpace(0) + language.PrintError('"ERROR : Somebody is using ' + struct_name + 's without deleting them (2).'))
            result.append(WHITESPACE + 'if(' + struct_name + '::GetAllocations() != ' + struct_name + '::GetDeallocations())')
            result.append(WHITESPACE + language.WhiteSpace(0) + language.PrintError('"ERROR : Somebody is using ' + struct_name + 's without deleting them (3).'))

        result.append('#endif // __arm__')
        return result

    def WRITE_UNITTEST_FACTORY_PAYLOAD_SIZE(self, WHITESPACE='\t\t', unittestfw=UnitTestFramework.NO_FW):
        struct = self.message
        language = self.language
        interface = self.interface

        struct_name = struct.Name

        result = []
        result.append(WHITESPACE + language.FormatComment('Test ' + ("struct " if language.MessageDescriptor(interface, struct) == "" else "message " + language.MessageDescriptor(interface, struct)) + " " + struct_name + ' payload size'))

        # Start scope for local vars redeclared
        result.append(WHITESPACE + language.OpenBrace())
        # Accumulate the size
        size_accumulator = 'size_accpl_' + struct.Name
        result.append(WHITESPACE + language.WhiteSpace(0) + language.InstantiateType('size_t ', size_accumulator, '0') + ";")

        # Reuse Base Class : Create Temporary Structs
        lines, to_delete = self.WRITE_CREATE_MESSAGE(WHITESPACE + language.WhiteSpace(0))
        for line in lines:
            result.append(line)

        '''
        Memory Management via Shared Pointer support
        '''
        accessor = language.Accessor(True)

        # Whilst we decompose, we might as well build these too...
        member_size_strings = []
        # To get payload size.
        protocol_membername = None
        # Creation of the type...
        structmembers = struct.Decompose()
        for mem in structmembers:
            membername = mem[1]
            membertype = mem[0]
            isArray = struct.IsArray(membername)
            isStruct = struct.IsStruct(membername)

            isProtocol = struct.IsProtocolStruct(membername)
            isEmbedded = isStruct or isProtocol

            ''' Embedded struct support (i.e. user typed data)
                Dont create a declaration for the protocol...this we can do automatically with
                provided info
            '''
            if isEmbedded and not isArray:
                if isProtocol:
                    # Also ignore this member size, as its compensated for
                    # in the payload (we send the data, not the pointer...
                    protocol_membername = membername
                else:
                    member_size_strings.append(WHITESPACE + language.WhiteSpace(0) + size_accumulator + ' += sizeof(' + membertype + '); ' + language.FormatComment(struct.Name + '::' + membername))
            elif isArray:
                member_size_strings.append(WHITESPACE + language.WhiteSpace(0) + size_accumulator + ' += sizeof(' + membertype + ')*50;')
            else:  # Normal type
                # We are traversing, build these up inline.
                member_size_strings.append(WHITESPACE + language.WhiteSpace(0) + size_accumulator + ' += sizeof(' + membertype + '); ' + language.FormatComment(struct.Name + '::' + membername))

        # Now accumulate the size of payload items
        for plitem in member_size_strings:
            result.append(plitem)
        # Now compare ...
        if unittestfw == UnitTestFramework.NO_FW:
            result.append(WHITESPACE + language.WhiteSpace(0) + language.If(self.instancename + accessor + protocol_membername + '.' + interface[MessageHeader.Name].PayloadSize() + ' != ' + size_accumulator))
            result.append(WHITESPACE + language.WhiteSpace(0) + language.OpenBrace())
            result.append(WHITESPACE + language.WhiteSpace(1) + language.PrintError('"ERROR : Size of ' + struct.Name + ' payload size does not equal the sum of its separate parts (less pointers to data): %i != %i " ,' + size_accumulator + ',' + self.instancename + accessor + protocol_membername + '.' + interface[MessageHeader.Name].PayloadSize()))

            result.extend(self.WRITE_DELETERS(to_delete, struct_name, WHITESPACE + language.WhiteSpace(0), unittestfw))

            result.append(WHITESPACE + language.WhiteSpace(1) + 'return false;')
            result.append(WHITESPACE + language.WhiteSpace(0) + language.CloseBrace())
        elif unittestfw == UnitTestFramework.BOOST:
            result.append(WHITESPACE + language.WhiteSpace(0) + 'BOOST_REQUIRE_MESSAGE(' + self.instancename + accessor + protocol_membername + '.' + interface[MessageHeader.Name].PayloadSize() + ' == ' + size_accumulator + ', "ERROR : Size of ' + struct_name + ' payload size does not equal the sum of its separate parts (less pointers to data).");')
        elif unittestfw == UnitTestFramework.CPPuTEST:
            result.append(WHITESPACE + language.WhiteSpace(0) + 'CHECK_EQUAL_TEXT(' + self.instancename + accessor + protocol_membername + '.' + interface[MessageHeader.Name].PayloadSize() + ',' + size_accumulator + ', "ERROR : Size of ' + struct_name + ' payload size does not equal the sum of its separate parts (less pointers to data).");')
        else:
            result.append(WHITESPACE + language.WhiteSpace(0) + "// Incorrect option " + str(unittestfw) + " for FACTORY PAYLOAD SIZE, please see options in class UnitTestFramework")

        result.extend(self.WRITE_DELETERS(to_delete, struct_name, WHITESPACE + language.WhiteSpace(0), unittestfw))

        # Stop scope for local vars redeclared
        result.append(WHITESPACE + language.CloseBrace())

        return result

    def WRITE_UNITTEST_TOFROM_BYTESTREAM(self, WHITESPACE='\t\t', is_arm=False, unittestfw=UnitTestFramework.NO_FW):
        struct = self.message
        struct_name = struct.Name

        result = []
        result.append(WHITESPACE + self.language.FormatComment('Test ' + ("struct " if self.language.MessageDescriptor(self.interface, self.message) == "" else "message " + self.language.MessageDescriptor(self.interface, self.message)) + " " + self.message.Name + ' to/from byte stream '))

        # Start scope for local vars redeclared
        result.append(WHITESPACE + self.language.OpenBrace())
        result.append("")
        creation, to_delete = self.WRITE_CREATE_MESSAGE(WHITESPACE + self.language.WhiteSpace(0))
        result.extend(creation)
        result.append("")
        result.extend(self.WRITE_MESSAGE_TO_STREAM(WHITESPACE + self.language.WhiteSpace(0), is_arm, unittestfw))
        result.append("")
        fromstream, to_delete2 = self.WRITE_MESSAGE_FROM_STREAM(WHITESPACE + self.language.WhiteSpace(0), is_arm, unittestfw)
        result.extend(fromstream)
        to_delete.extend(to_delete2)
        result.append("")
        result.extend(self.WRITE_DELETERS(to_delete, struct_name, WHITESPACE + self.language.WhiteSpace(0), unittestfw))
        # Stop scope for local vars redeclared
        result.append(WHITESPACE + self.language.CloseBrace())

        return result


class LanguageCsharp:

    """USED"""
    def MessageDescriptor(self, interface, struct):
        return "" if interface.GetMessageTypeIDStr(struct) == "" else " [ MsgTypeID = " + interface.GetMessageTypeIDStr(struct) + " ]"

    # White space
    def WhiteSpace(self, indentationlevels):
        return (indentationlevels+1)*'\t'

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
    def ParameterString(self, parameters=None):
        # def ParameterString(self, parameters = []):
        # https://florimond.dev/blog/articles/2018/08/python-mutable-defaults-are-the-source-of-all-evil/
        if parameters is None:
            parameters = []

        if str(type(parameters)) == "<type 'list'>" or str(type(parameters)) == "<class 'list'>":  # Python2 gives the first, python3 the second!
            parameter_string = ''
            size = len(parameters)
            cnt = 0
            for param in parameters:
                parameter_string += param[0] + ' ' + param[1]
                if cnt != (size - 1):
                    parameter_string += ', '
                cnt += 1
            return parameter_string

        raise Exception("Please use OrderedDict when passing parameters into 'ParameterString'")
    '''USED'''
    def DeclareFunction(self, returntype, classname, functionname, is_impl, parameters=None, virtual=False, is_static=False, is_const=False):
        # def DeclareFunction(self, returntype, classname, functionname, is_impl, parameters=[], virtual=False):
        # https://florimond.dev/blog/articles/2018/08/python-mutable-defaults-are-the-source-of-all-evil/
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
    def GetFactoryCreateParams(self, struct, interface):
        structmembers = struct.Decompose()
        factoryparams = []
        for mem in structmembers:
            isArray = struct.IsArray(mem[1])
            isMessage = interface.IsMessageStruct(mem[0])
            isStruct = struct.IsStruct(mem[1])
            if not interface.IsProtocolStruct(mem[0]):
                ptr = "*" if isArray else ""
                ref = "&" if isStruct or isMessage else ""
                if (mem[0] in interface) and not isArray:
                    factoryparams.append(("/*const*/ "+(self.SharedPtrToType(mem[0]) if isMessage else mem[0]) + ref, mem[1]))
                else:
                    factoryparams.append(("/*const*/ "+mem[0] + ptr + ref, mem[1]))
        return factoryparams

    '''USED
    Declares the guts of a struct declaration
    '''
    def DeclareStructMembers(self, struct, interface, whitespace, attr_packed=True):
        arrayName = []
        structmembers = struct.Decompose()
        result = []
        for mem in structmembers:
            ptr = ""
            if struct.IsArray(mem[1]):
                ptr = "*"
            if (mem[0] in interface) and not struct.IsArray(mem[1]):
                result.append(whitespace + self.InstantiateType(mem[0], mem[1]) + ";")
            else:
                result.append(whitespace + self.InstantiateType(mem[0] + ptr, mem[1], '', attr_packed) + ";")

            if struct.IsArray(mem[1]):
                arrayName.append(mem[1])
        if len(arrayName) != 0:
            result.append(whitespace+"~%s()" % struct.Name)
            result.append(whitespace+"{")
            for todel in arrayName:
                result.append(2*whitespace+"delete[] %s;" % todel)
            result.append(whitespace+"}")
        return result
    '''USED'''
    def InstantiateStructMembers(self, struct, interface, whitespace, instancename, accessor):
        structmembers = struct.Decompose()
        result = []
        for mem in structmembers:
            isArray = struct.IsArray(mem[1])
            isStruct = interface.IsStruct(mem[1])
            isProtocol = interface.IsProtocolStruct(mem[0])
            instance_accessor = whitespace + instancename + accessor

            if not isArray and (not isProtocol or isStruct):
                result.append(instance_accessor + self.InstantiateType('', mem[1], mem[1]) + ";")
            elif not isArray and isProtocol and not isStruct:
                s = Template("sizeof(${this}) - sizeof(${header})")
                result.append(instance_accessor + self.InstantiateType("", mem[1], "Create_" + mem[0] + "(" + struct[mem[1]].GetDefaultsAsString(s.substitute(this=struct.Name, header=mem[0])) + ");"))
            elif isArray and not isProtocol and not isStruct:
                if not IsMessageStruct(interface, struct.Name):
                    raise RuntimeError("Only mesage structs are allowed arrays.")
                result.append(whitespace + "// cant transmit ptr's across the world, but well data.")
                s = Template("${payload} ${op} ${bytes}")
                array = struct[mem[1]]
                result.append(instance_accessor + s.substitute(payload=struct.HeaderName() + "." + struct[struct.HeaderName()].PayloadSize(), op="-=", bytes="sizeof("+instancename+accessor+array.Name+");"))
                result.append(instance_accessor + s.substitute(payload=struct.HeaderName() + "." + struct[struct.HeaderName()].PayloadSize(), op="+=", bytes="sizeof("+array.type + ")*" + array.Count() + ";"))
                # result.append(instance_accessor + self.InstantiateType("",array.Count(),array.Count()))
                result.append(instance_accessor + self.InstantiateArray(array.type, array.Name, array.Count()) + ";")
                result.append(whitespace + "if(nullptr != " + array.Name + ")")
                result.append(2*whitespace + "memcpy((void*) "+instance_accessor.replace("\t", '') + array.Name + ',(void*) ' + array.Name + ',sizeof(' + array.type + ")*" + array.Count() + ");")
            else:
                print("WTF : InstantiateStructMembers")

        return result
    '''USED
    All custom structs, protocol structs and message structs.
    '''
    def SerializeStructToByteStream(self, struct, interface, whitespace, outname, inname, inacessor, is_arm=False):
        result = []
        hasArray = False
        isProtocol = interface.IsProtocolStruct(struct.Name)
        isStruct = interface.IsStruct(struct.Name)
        if isProtocol or isStruct:
            result.append(whitespace + "size_t streamsize = sizeof("+struct.Name+");")
        else:
            hasArray = struct.HasArray()  # Message can not have an array.
            result.append(whitespace + "size_t streamsize = sizeof("+inname + inacessor + struct.HeaderName() + ") +" + inname + inacessor + struct.HeaderName() + "."+struct[struct.HeaderName()].PayloadSize() + ";")
        out_accessor = outname + self.BytestreamAccessor()
        if not is_arm:
            result.append(whitespace + out_accessor + "resize(streamsize)"+";")
        if isProtocol or isStruct or not hasArray:
            if not is_arm:
                result.append(whitespace + "memcpy((void*) &(*"+outname+")[0], (void*) " + (("&"+inname) if ("." == inacessor) else (inname + ".get()")) + ", streamsize);")
            else:
                result.append(whitespace + "memcpy((void*) " + outname + ", (void*) " + (("&"+inname) if ("." == inacessor) else ("&(*" + inname + ")")) + ", streamsize);")
        else:
            if not interface.IsMessageStruct(struct.Name):
                raise RuntimeError("Unhandled type. This should be an message struct, but is a %s" % str(type(struct)))
            result.append(whitespace + "size_t index = 0;")
            structmembers = struct.Decompose()
            for mem in structmembers:
                if struct.IsArray(mem[1]):
                    array = struct[mem[1]]
                    result.append(whitespace + "memcpy((void*) &(*"+outname+")[index], (void*) "+inname + inacessor + mem[1] + ", sizeof("+mem[0]+")*"+inname + inacessor + array.Count() + ");")
                    result.append(whitespace + "index += sizeof("+mem[0]+")*" + inname + inacessor + array.Count()+";")
                else:
                    result.append(whitespace + "memcpy((void*) &(*"+outname+")[index], (void*) &"+inname + inacessor + mem[1] + ", sizeof("+mem[0]+"));")
                    result.append(whitespace + "index += sizeof("+mem[0]+");")
            result.append(whitespace + "assert(index == streamsize); // index should be at next (non existant) place (thus streamsize).")
        return result
    '''USED
    All custom structs, protocol structs and message structs.
    '''
    def SerializeStructIntoByteStream(self, struct, interface, whitespace, inname, streamname, cntname, inacessor):
        result = []
        hasArray = False
        isProtocol = interface.IsProtocolStruct(struct.Name)
        isStruct = interface.IsStruct(struct.Name)
        if isProtocol or isStruct:
            result.append(whitespace + "size_t append_size = sizeof("+struct.Name+");")
        else:
            hasArray = struct.HasArray()  # Message can not have an array.
            result.append(whitespace + "size_t append_size = sizeof("+inname + inacessor + struct.HeaderName() + ") +"+inname + inacessor + struct.HeaderName() + "."+struct[struct.HeaderName()].PayloadSize() + ";")
        result.append(whitespace + "size_t avail_size = "+streamname+"->size() - "+cntname+";")
        result.append(whitespace + "if(avail_size < append_size)")
        result.append(whitespace*2 + streamname + "->resize(append_size - avail_size);")
        if isProtocol or isStruct or not hasArray:
            result.append(whitespace + "memcpy((void*) &(*"+streamname+")["+cntname+"], (void*) " + (("&"+inname ) if ("." == inacessor) else (inname + ".get()")) + ", append_size);")
        else:
            if not interface.IsMessageStruct(struct.Name):
                raise RuntimeError("Unhandled type. This should be an message struct, but is a %s" % str(type(struct)))

            structmembers = struct.Decompose()
            for mem in structmembers:
                if struct.IsArray(mem[1]):
                    array = struct[mem[1]]
                    result.append(whitespace + "memcpy((void*) &(*"+streamname+")[index], (void*) "+inname + inacessor + mem[1] + ", sizeof("+mem[0]+")*"+inname + inacessor + array.Count() + ");")
                    result.append(whitespace + "index += sizeof("+mem[0]+")*" + inname + inacessor + array.Count()+";")
                else:
                    result.append(whitespace + "memcpy((void*) &(*"+streamname+")[index], (void*) &"+inname+inacessor + mem[1] + ", sizeof("+mem[0]+"));")
                    result.append(whitespace + "index += sizeof("+mem[0]+");")
        result.append(whitespace + cntname + "+=append_size;")
        return result
    '''USED
    All custom structs, protocol structs and message structs.
    '''
    def SerializeStructFromByteStream(self, functioname, struct, interface, whitespace, streamname, cntname, outname, outaccessor):
        result = []

        structmembers = struct.Decompose()
        has_allowed_stream_size = False
        for mem in structmembers:

            isProtocol = interface.IsProtocolStruct(mem[0])
            isStruct = interface.IsStruct(mem[0])
            isArray = struct.IsArray(mem[1])
            isType = not isProtocol and not isStruct and not isArray

            access_member = outname+outaccessor+mem[1]
            if isArray:
                array = struct[mem[1]]
                size_of_cnt_var = 'sizeof(' + array[array.Count()] + ')'
                array_cnt_var = outname + outaccessor + array.Count()
                size_of_array = 'sizeof(' + mem[0] + ')*' + array_cnt_var
                result.append(whitespace + 'if ((' + cntname + ' + ' + size_of_cnt_var + ' < streamsize) && (' + size_of_cnt_var + ' <= allowed_streamsize))')
                result.append(whitespace + '{')
                result.append(whitespace*2 +      'memcpy((void*) &' + array_cnt_var + ', (void*) &('+streamname+'['+cntname+']), ' + size_of_cnt_var + ');')
                result.append(whitespace*2 +      cntname + '+=' + size_of_cnt_var + ";")
                result.append(whitespace*2 +      'allowed_streamsize-=' + size_of_cnt_var + ";")
                # Create a new array, set the size, and memcpy the entire contents into the member var
                result.append(whitespace*2 +      self.InstantiateArray(mem[0], access_member, array_cnt_var) + ";")
                result.append(whitespace*2 +      'if ((' + cntname + ' + ' + size_of_array + ' <= streamsize) && (' + size_of_array + ' <= allowed_streamsize))')
                result.append(whitespace*2 +      '{')
                result.append(whitespace*3 +          'memcpy((void*) ' + access_member + ', (void*) &(' + streamname + '[' + cntname + ']), ' + size_of_array + ');')
                result.append(whitespace*3 +          cntname + '+=' + size_of_array + ";")
                result.append(whitespace*3 +          'allowed_streamsize-=' + size_of_array + ";")
                result.append(whitespace*2 +      '}')
                result.append(whitespace*2 +      'else if ((' + cntname + ' + ' + size_of_array + ' <= streamsize) && (' + size_of_array + ' > allowed_streamsize))')
                result.append(whitespace*2 +      '{')
                result.append(whitespace*3 +          'memcpy((void*) ' + access_member + ', (void*) &(' + streamname + '[' + cntname + ']), allowed_streamsize);')
                result.append(whitespace*3 +          cntname + '+=allowed_streamsize;')
                result.append(whitespace*3 +          'allowed_streamsize-=allowed_streamsize;')
                result.append(whitespace*2 +      '}')
                result.append(whitespace*2 +      'else')
                result.append(whitespace*2 +      '{')
                result.append(whitespace*3 +          self.PrintMessage('"' + functioname + ' Safety Bogey : resyncing streams, not copying..."'))
                result.append(whitespace*3 +          'index+=allowed_streamsize;')
                result.append(whitespace*3 +          'allowed_streamsize=0;')
                result.append(whitespace*2 +      '}')
                result.append(whitespace + '}')
                result.append(whitespace + 'else')
                result.append(whitespace + '{')
                result.append(whitespace*2 +      self.PrintMessage('"' + functioname + ' index exceeds given streamsize."'))
                result.append(whitespace + '}')
            elif isProtocol:
                result.append(whitespace + access_member + ' = FromByteStream_' + mem[0] + '('+streamname+', streamsize, '+cntname+');')
                result.append(whitespace + '// Backward Compat: Protocol header should NEVER change, but payloads may.')
                result.append(whitespace + '// Calculate remaining non destructive stream size.')
                result.append(whitespace + 'size_t allowed_streamsize = '+access_member+'.' + struct[mem[1]].PayloadSize()+";")
                has_allowed_stream_size = True
            elif isStruct:
                result.append(whitespace + access_member + ' = FromByteStream_' + mem[0] + '('+streamname+', streamsize, '+cntname+');')
                result.append(whitespace + 'allowed_streamsize-=sizeof('+mem[0]+');')
            elif isType:
                if mem[1].find(Array.PREFIX) == -1:  # Ignore the array count memember here! deal with it in the array...
                    if has_allowed_stream_size:
                        result.append(whitespace + "if((" + cntname + " + sizeof(" + mem[0] + ") <= streamsize) && (sizeof(" + mem[0] + ") <= allowed_streamsize))")
                        result.append(whitespace + "{")
                        result.append(whitespace*2 +   "memcpy((void*) &" + access_member + ", (void*) &(" + streamname + "[" + cntname + "]), sizeof(" + mem[0] + "));")
                        result.append(whitespace*2 +   cntname + "+=sizeof(" + mem[0] + ");")
                        result.append(whitespace*2 +   "allowed_streamsize-=sizeof(" + mem[0] + ");")
                        result.append(whitespace + "}")
                        result.append(whitespace + "else")
                        result.append(whitespace + "{")
                        result.append(whitespace*2 +   self.PrintMessage('"' + functioname + ' index exceeds given streamsize."'))
                        result.append(whitespace + "}")
                    else:
                        result.append(whitespace + 'if(index + sizeof(' + mem[0] + ') <= streamsize)')
                        result.append(whitespace + '{')
                        result.append(whitespace*2 +      'memcpy((void*) &' + access_member + ', (void*) &(' + streamname + '[' + cntname + ']), sizeof(' + mem[0] + '));')
                        result.append(whitespace*2 +      cntname + '+=sizeof(' + mem[0] + ');')
                        result.append(whitespace + '}')
                        result.append(whitespace + "else")
                        result.append(whitespace + '{')
                        result.append(whitespace*2 + self.PrintMessage('"' + functioname + ' index exceeds given streamsize."'))
                        result.append(whitespace + '}')
            else:
                raise RuntimeError("Unhandled type %s in SerializeStructFromByteStream" % str(type(mem[1])))

        if has_allowed_stream_size:
            result.append(whitespace + 'assert(allowed_streamsize==0);')
        return result

    '''USED'''
    def InstantiatePtrToType(self, typename, instancename):
        return self.PtrToTypeName(typename) + ' ' + instancename + '(new ' + typename + ')'

    def InstantiatePtrToType2(self, typepointername, instancename, typename):
        return typepointername + ' ' + instancename + '(new ' + typename + ')'

    '''USED'''
    def InstantiateArray(self, typename, instancename, noelements):
        return instancename + ' = new ' + typename + '['+noelements+']'

    '''USED

        Instantiate/declare a basic type, with optional initializer. Only declarations can use 'attribute packed' directives.
        use typename = '' to make it a known variable initialization
    '''
    def InstantiateType(self, typename, instancename, initialevalue='', is_attr_packed=False, is_static=False, is_const=False):
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

    # File extenstion
    def DotHFile(self):
        return '.h'

    def DotCPPFile(self):
        return '.cpp'

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
        '''
        ws = ' '
        len_declaration = len(declaration)
        trailingspacecnt = 50 - len_declaration
        for i in range(trailingspacecnt):
            ws = ws + ' '
        result = declaration + ws + '__attribute__ ((packed))'
        '''
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

    def DeclareEnum(self, enum, whitespace):
        result = whitespace + "enum " + enum.Name + "{\n"
        for descriptionName, val in enum.items():
            result += whitespace*2 + str(descriptionName) + " = " + str(val) + ",\n"
        result = result[:len(result)-2] + "\n"  # items from the beginning through end-1 (i.e. remove last character which is a ','
        result += whitespace + "};\n"
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

    '''USED'''
    # 1 means ++
    def For_Range(self, start, stop, incr=1):
        if incr == 1:
            return 'for (size_t i = ' + str(start) + '; i < ' + str(stop) + '; ++i)'
        return 'for (size_t i = ' + str(start) + '; i < ' + str(stop) + '; i+=' + str(incr) + ')'

    # ------------------------------ End

    def LicenseAgreement(self):
        product_name = "'KoJen'"
        result = []
        result.append("--------------------------------------------------------------------------------")
        result.append("")
        result.append('\t' + "This file is part of " + product_name + ".")
        result.append("")
        result.append('\t' + product_name + " is free software: you can redistribute it and/or modify")
        result.append('\t' + "it under the terms of the GNU General Public License as published by")
        result.append('\t' + "the Free Software Foundation, either version 3 of the License, or")
        result.append('\t' + "(at your option) any later version.")
        result.append("")
        result.append('\t' + product_name + " is distributed in the hope that it will be useful,")
        result.append('\t' + "but WITHOUT ANY WARRANTY; without even the implied warranty of")
        result.append('\t' + "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the")
        result.append('\t' + "GNU General Public License for more details.")
        result.append("")
        result.append('\t' + "You should have received a copy of the GNU General Public License")
        result.append('\t' + "along with " + product_name + ".  If not, see <http://www.gnu.org/licenses/>.")
        result.append('\t' + "For any queries please contact : koh.jaen@yahoo.de.")
        result.append("\n")
        result.append('\t\t' + "This file was generated on    : " + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + ".")
        result.append('\t\t' + "This file was generated using : " + sys.platform + ".")
        result.append('\t\t' + "This file was generated by a machine. Do not modify it by hand.")
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
                    result = result + "\tclass " + _class + ";\n"
                result = result + _getFormatNestedNamespaceEnd(_namespace) + "\n"

            if result:
                result = "// Begin Forward declarations\n" + result + "// End Forward declarations"
            return result
        else:
            raise RuntimeError("classObj not of type 'Class' OR classDiagram not of type 'ClassDiagram'")

    def GetTypeAndNameFromMultiplicityAndModifier(self, classObj, TYPE, TYPE_MODIFIER, MULTIPLICITY, NAME):
        '''
        https://www.researchgate.net/figure/Mappings-from-C-declarations-to-UML-multiplicity-ranges-depend-on-pointer-reference_tbl1_4207986
        http://www.cs.kent.edu/~jmaletic/papers/JIST07.pdf

        @param TYPE:
        @param TYPE_MODIFIER:
        @param MULTIPLICITY:
        @param NAME:
        @return:
        '''
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
                    result = result + "\t/// {{{USER_" + ("CONSTRUCTOR" if is_constructor else CleanName(operation.RETURN_TYPE)) + "_" + classname + "_" + operation.NAME + "_" + str(len(params)) + "_PARAMS}}}\n"
                    result = result + "\t/// {{{USER_" + ("CONSTRUCTOR" if is_constructor else CleanName(operation.RETURN_TYPE)) + "_" + classname + "_" + operation.NAME + "_" + str(len(params)) + "_PARAMS}}}\n"
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
                    result = result + "\t" + attr_names[i] + " = " + params[i][1] + ";\n"
                result = result + "\t/// {{{USER_CONSTRUCTOR_" + classObj.NAME + "_" + str(len(params)) + "_PARAMS}}}\n"
                result = result + "\t/// {{{USER_CONSTRUCTOR_" + classObj.NAME + "_" + str(len(params)) + "_PARAMS}}}\n"
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
                        result = result + "\treturn " + type_and_name[1] + ";\n"
                        result = result + "}\n"
                if attr.HAS_SETTER and not attr.IS_CONST:  # Cant set a const attribute!
                    inputvarName = type_and_name[1].replace("m_", "__new")
                    result = result + self.DeclareFunction("void", classObj.NAME, type_and_name[1].replace("m_", "Set"), is_impl, [(a_type, inputvarName)]) + ("\n" if is_impl else ";\n")
                    if is_impl:
                        result = result + "{\n"
                        result = result + "\t" + type_and_name[1] + " = " + inputvarName + ";\n"
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
        '''
        Used in a .csharp project to include other dependant project files :

        <ItemGroup>
            <ProjectReference Include="..\XTestingClassTypes\XTestingClassTypes.csproj" />
            <ProjectReference Include="..\XTestingInheritance\XTestingInheritance.csproj" />
        </ItemGroup>
        '''
        result = ""
        if len(setOfProjectDependencies) > 0:
            result = "<ItemGroup>\n"
            for s in setOfProjectDependencies:
                result = result + '\t<ProjectReference Include="..\\' + s + '\\' + s + '.csproj" />\n'
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


if __name__ == "__main__":
    from TCPGen_IF_test import *
    interface = CreateInterface()
    structs = interface.Messages()
    language = LanguageCsharp()
    '''
    for s in structs:
            a_test_writer = UnitTestWriter(interface,s,language,"ptr2"+s.Name)
            print (language.WhiteSpace(1) + language.OpenBrace())
            guts = a_test_writer.WRITE_CREATE_MESSAGE(language.WhiteSpace(2))
            for g in guts:
                print (g)
            guts = a_test_writer.WRITE_MESSAGE_TO_STREAM(language.WhiteSpace(2))
            for g in guts:
                print (g)
            print (language.WhiteSpace(2)+'m_connection->SendData(' + a_test_writer.bytestream_of_message_variable_name + ');')
            print (language.WhiteSpace(1) + language.CloseBrace())
    '''
    for s in structs:
        test = UnitTestWriter(interface, s, language, "WATKYKJY")
        guts = test.WRITE_UNITTEST_FACTORY_PAYLOAD_SIZE(language.WhiteSpace(0))
        for g in guts:
            print(g)

