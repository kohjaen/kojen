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
from collections import OrderedDict


def IsStruct(container, instancename):
    if instancename in container:
        typeof = str(type(container[instancename]))
        if typeof.find('class') > -1 and typeof.find('Array') == -1 and typeof.find('Struct') > -1 and typeof.find('Message') == -1 and typeof.find('MessageHeader') == -1:
            return True
    return False


def IsProtocolStruct(container, instancename):
    if instancename in container:
        typeof = str(type(container[instancename]))
        if typeof.find('class') > -1 and typeof.find('Array') == -1 and typeof.find('Struct') == -1 and typeof.find('MessageHeader') > -1:
            return True
    return False


def IsMessageStruct(container, instancename):
    if instancename in container:
        typeof = str(type(container[instancename]))
        if typeof.find('class') > -1 and typeof.find('Array') == -1 and typeof.find('Struct') == -1 and typeof.find('Message') > -1 and typeof.find('MessageHeader') == -1:
            return True
    return False


class Query:
    def IsStruct(self, instancename):
        return IsStruct(self, instancename)

    def IsProtocolStruct(self, instancename):
        return IsProtocolStruct(self, instancename)

    def IsMessageStruct(self, instancename):
        return IsMessageStruct(self, instancename)


class DefaultVal:

    def __init__(self):
        self.defaults = OrderedDict()

    def GetDefaults(self):
        result = []
        for d in self.defaults:
            result.append(self.defaults[d])
        return result

    def GetDefaultsAsString(self):
        return str(self.GetDefaults()).replace("[", "").replace("]", "").replace("'", "")

    def GetDefault(self, varname):
        if varname in self.defaults:
            return self.defaults[varname]
        return "0"

class Documentation:
    def __init__(self):
        self.documentation = ""

    def SetDocumentation(self, documentation):
        self.documentation = documentation

''' TODO
class RoutingHeader(OrderedDict, Query, DefaultVal):
    """
    RoutingHeader.

    All Messages that are routed between network nodes have a RoutingHeader.

    It is enough information that, at a byte level we can parse the byte stream correctly, and not lose any information
    and do it generically in such a way that derived protocols do not have to be known by the nodes.
    This allows us to reuse a common snippet of code in all places, for handling bytestreams to protocols, without knowing
    of the protocols themselves (only RoutingHeader needs to be known).

    First  : 1 byte   = This Module Address.
    Second : 1 byte   = Destination Module Address.
    Third  : 1 byte   = Status. This is for handshaking, error handling when there is no path to the requested node etc.
    Fourth : 4 bytes  = No of bytes to follow that make this message complete. We can thus pull all data out from
                        the byte stream, and pass it on to be handled correctly, without affecting other data.
                        2 pow (4x8) = 4GB max payload size...
    """

    Name = 'sRoutingHeader'

    def __init__(self, toaddr=0, thisaddr=0, stat=0, plsz=0):
        super(RoutingHeader, self).__init__()
        DefaultVal.__init__(self)
        self[self.ToModuleAddress()]			= 'uint8'
        self[self.ThisModuleAddress()]			= 'uint8'
        self[self.Status()]						= 'uint8'
        self[self.PayloadSize()] 				= 'uint32'
        self.defaults[self.ToModuleAddress()] 	= toaddr
        self.defaults[self.ThisModuleAddress()] = thisaddr
        self.defaults[self.Status()] 			= stat
        self.defaults[self.PayloadSize()] 		= plsz

    def ToModuleAddress(self):
        return 'ToModuleAddress'

    def ThisModuleAddress(self):
        return 'ThisModuleAddress'

    def Status(self):
        return 'Status'

    def PayloadSize(self):
        return 'PayloadSize'
'''

class MessageHeader(OrderedDict, Query, DefaultVal):
    """
    MessageHeader.

    All Messages that are exchanged between two endpoints have a MessageHeader.

    It is enough information that, at a byte level 	we can parse the byte stream correctly, not lose any information
    and do it generically in such a way that derived protocols do not have to be known by the endpoints.
    This allows us to reuse a common snippet of code in all places, for handling bytestreams to message, without knowing
    of the messages themselves (only MessageHeader needs to be known).

    First  : 2 bytes  = Preamble. A marker separating all messages.
    Second : 2 bytes  = Type ID. We can get the particular structure of the message.
    Third  : 4 bytes  = No of bytes to follow that make this message complete. We can thus pull all data out from
                        the byte stream, and pass it on to be handled correctly, without affecting other data.
                        2 pow (4x8) = 4GB max payload size...
    """

    Name = 'sMsgHeader'

    def __init__(self, preamble, typeid, plsz=0):
        super(MessageHeader, self).__init__()
        DefaultVal.__init__(self)
        self[self.Preamble()]				= 'uint16'
        self[self.TypeID()]					= 'uint16'
        self[self.PayloadSize()]			= 'uint32'
        self.defaults[self.Preamble()]		= str(preamble)
        self.defaults[self.TypeID()]		= str(typeid)
        self.defaults[self.PayloadSize()]	= str(plsz)

    def Preamble(self):
        return 'Preamble'

    def TypeID(self):
        return 'TypeID'

    def PayloadSize(self):
        return 'PayloadSize'

    def Decompose(self, recursive = True):
        result = []
        for memberName in self:
            result.append((self[memberName], memberName, self.defaults[memberName]))
        return result

    def OverridePreamble(self, preamble):
        self.defaults[self.Preamble()] = preamble

    # allow override of payload size
    def GetDefaultsAsString(self, payloadsizeoverride=''):
        if payloadsizeoverride.replace(' ', '') != '':
            self.defaults['PayloadSize'] = payloadsizeoverride
        return DefaultVal.GetDefaultsAsString(self)


class Enum(OrderedDict, Documentation):
    """
    Enumeration.
    """

    def __init__(self, enumName):
        super(Enum, self).__init__()
        Documentation.__init__(self)
        self.Name = enumName

    def Add(self, descriptionName, val):
        self[descriptionName] = val

    def Decompose(self):
        result = []
        for descriptionName, val in self.items():
            result.append((descriptionName, val))
        return result


class Struct(OrderedDict, Query, DefaultVal, Documentation):
    """
    Struct.
    A struct is a collection of base types, that form part of a message, as a separate member.
    """
    def __init__(self, structName):
        super(Struct, self).__init__()
        DefaultVal.__init__(self)
        self.Name  = structName

    def AddType(self, memberName, memberType, default = None):
        self[memberName]          = memberType
        self.defaults[memberName] = str(default) if default else default

    def AddStruct(self, memberName, struct):
        self[memberName] = struct

    def Decompose(self, recursive = True):
        result = []
        for memberName in self:
            if hasattr(self[memberName], 'Decompose') and recursive:
                if self.IsStruct(memberName):
                    nested = self[memberName].Decompose()
                    result.append((self[memberName].Name, memberName, nested))
            else:
                if self.IsStruct(memberName):
                    if memberName in self.defaults:
                        result.append((self[memberName].Name, memberName, self.defaults[memberName]))
                    else:
                        result.append((self[memberName].Name, memberName))
                else:
                    result.append((self[memberName], memberName, self.defaults[memberName]))
        return result


class Array(OrderedDict, Query, Documentation):

    PREFIX = '_Cnt'

    def __init__(self, arrayname, arraytype):
        super(Array, self).__init__()
        self.Name = arrayname
        self[self.Count()] = 'uint32'
        self.type = arraytype

    def Count(self):
        return self.Name+Array.PREFIX

    def Decompose(self):
        result = []
        for memberName in self:
            result.append((self[memberName], memberName))

        if hasattr(self.type, 'Decompose'):
            result.append((self.type.Name, self.Name))
        else:
            result.append((self.type, self.Name))
        return result


class Message(OrderedDict, Query, DefaultVal, Documentation):
    """
    Message.
    This represents a package of data the is passed between entities.
    A message contains a header.
    Then, as per user definition the following member fields can be added
     - a member of Type
     - a member of Struct
     - a member of Type[]
     - a member of Struct[].
    """
    def __init__(self, messageName, messageTypeID):
        super(Message, self).__init__()
        DefaultVal.__init__(self)
        self.Name            = messageName
        self.MessageTypeID   = messageTypeID
        self[self.HeaderName()] = MessageHeader(0, self.MessageTypeID)

    # done by Interface.
    def SetPreamble(self, preamble):
        self[self.HeaderName()].OverridePreamble(preamble)

    def HeaderName(self):
        return 'Header'

    def AddType(self, memberName, membertype, default = None):
        self[memberName] = membertype
        self.defaults[memberName] = str(default) if default else default

    def AddStruct(self, memberName, struct):
        self[memberName] = struct

    def Decompose(self, recursive = True):
        result = []
        for memberName in self:
            if hasattr(self[memberName], 'Decompose') and recursive:
                if self.IsStruct(memberName):
                    nested = self[memberName].Decompose()
                    result.append((self[memberName].Name, memberName, nested))
                elif self.IsProtocolStruct(memberName):
                    result.append((self[memberName].Name, memberName))
                else:
                    kid = self[memberName].Decompose()
                    result.extend(kid)
            else:
                if self.IsStruct(memberName) or self.IsProtocolStruct(memberName):
                    if memberName in self.defaults:
                        result.append((self[memberName].Name, memberName, self.defaults[memberName]))
                    else:
                        result.append((self[memberName].Name, memberName))
                else:
                    result.append((self[memberName], memberName, self.defaults[memberName]))
        return result


class Interface(OrderedDict, Query):
    """
    Interface.
    A message passing interface represents a unique set of transactions (similar to serialized function calls)
    between two entities.
    An interface has
      - a collection of structs used in messages, messages themselves
      - defines (enumerations and #defines not used in stucts or messages currently).
    Each message is uniquely defined with
    - a message marker preamble. Marks the start of a message, eg. 0xBEEF, 0xBABE, 0xCAFE, 0xDEAD, 0xDEAF, 0xFACE, 0xFADE, 0xFEED
    - a message type id.
    """

    def __init__(self, interfaceName, interfacePreamble=0xDEAD):
        super(Interface, self).__init__()
        self[MessageHeader.Name] = MessageHeader(interfacePreamble, -1)
        self.Name = interfaceName
        self.InterfacePreamble = interfacePreamble
        self.enums = OrderedDict()
        self.hashdefines = OrderedDict()
        self.usertags = OrderedDict()
        self.MessageMap = {}

    def AddStruct(self, struct):
        self[struct.Name] = struct

    def AddMessage(self, message):
        message.SetPreamble(self.InterfacePreamble)
        if message.MessageTypeID in self.MessageMap:
            added = message.Name
            existing = self.MessageMap[message.MessageTypeID].Name
            raise RuntimeError("Error when adding (%s) : Message with id [%s] (%s) already defined." % (added , message.MessageTypeID , existing))
        self[message.Name] = message
        self.MessageMap[message.MessageTypeID] = message

    def AddEnum(self, enum):
        self.enums[enum.Name] = enum

    def AddHashDefine(self, name, val):
        self.hashdefines[name] = val

    def AddUserTag(self, name, val):
        self.usertags[name] = val

    def All(self):
        result = self.ProtocolStructs()
        result.extend(self.Structs())
        result.extend(self.Messages())
        return result

    def Messages(self) -> list:
        result = []
        for key in self:
            typeof = str(type(self[key]))
            if typeof.find('class') > -1 and typeof.find('Struct') == -1 and typeof.find('Message') > -1 and typeof.find('MessageHeader') == -1:
                result.append(self[key])
        return result

    def MessageNames(self) -> list:
        result = []
        for key in self:
            typeof = str(type(self[key]))
            if typeof.find('class') > -1 and typeof.find('Struct') == -1 and typeof.find('Message') > -1 and typeof.find('MessageHeader') == -1:
                result.append(key)
        return result

    def Structs(self) -> list:
        result = []
        for key in self:
            typeof = str(type(self[key]))
            if typeof.find('class') > -1 and typeof.find('Struct') > -1 and typeof.find('Message') == -1 and typeof.find('MessageHeader') == -1:
                result.append(self[key])
        return result

    def StructNames(self) -> list:
        result = []
        for key in self:
            typeof = str(type(self[key]))
            if typeof.find('class') > -1 and typeof.find('Struct') > -1 and typeof.find('Message') == -1 and typeof.find('MessageHeader') == -1:
                result.append(key)
        return result

    def ProtocolStructs(self) -> list:
        result = []
        for key in self:
            typeof = str(type(self[key]))
            if typeof.find('class') > -1 and typeof.find('Struct') == -1 and typeof.find('MessageHeader') > -1:
                result.append(self[key])
        return result

    def ProtocolStructNames(self) -> list:
        result = []
        for key in self:
            typeof = str(type(self[key]))
            if typeof.find('class') > -1 and typeof.find('Struct') == -1 and typeof.find('MessageHeader') > -1:
                result.append(key)
        return result

    def Enums(self) -> list:
        result = []
        for n, e in self.enums.items():
            result.append(e)
        return result

    def HashDefines(self) -> list:
        result = []
        for k, v in self.hashdefines.items():
            result.append((k, v))
        return result

    def UserTags(self):
        return self.usertags

    def Decompose(self):
        result = []
        for name in self:
            result.extend(self[name].Decompose())
        return result

    def GetMessageTypeIDStr(self, struct):
        for a in self.MessageMap:
            if self.MessageMap[a].Name == struct.Name:
                return str(a).replace("[", "").replace("]", "").replace("'", "").replace("(", "").replace(")", "")
        return ""


