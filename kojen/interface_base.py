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
from collections import OrderedDict


class MsgIDType:
	m_msg_id = ""
	m_msg_type = ""

	def __init__(self, msg_id, msg_type):
		self.m_msg_id = msg_id
		self.m_msg_type = msg_type


def IsArray(container, instancename):
	if instancename in container:
		typeof = str(type(container[instancename]))
		if typeof.find('class') > -1 and typeof.find('Array') > -1 and typeof.find('Struct') == -1 and typeof.find('Message') == -1 and typeof.find('MessageHeader') == -1:
			return True
	return False


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
	def IsArray(self, instancename):
		return IsArray(self, instancename)

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


# TODO : This is currently defined, but unused anywhere.
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
		self.defaults[self.Preamble()]		= preamble
		self.defaults[self.TypeID()]		= typeid
		self.defaults[self.PayloadSize()]	= plsz

	def Preamble(self):
		return 'Preamble'

	def TypeID(self):
		return 'TypeID'

	def PayloadSize(self):
		return 'PayloadSize'

	def Decompose(self):
		result = []
		for memberName in self:
			result.append((self[memberName], memberName))
		return result

	def OverridePreamble(self, preamble):
		self.defaults[self.Preamble()] = preamble

	# allow override of payload size
	def GetDefaultsAsString(self, payloadsizeoverride=''):
		if payloadsizeoverride.replace(' ', '') != '':
			self.defaults['PayloadSize'] = payloadsizeoverride
		return DefaultVal.GetDefaultsAsString(self)


class Enum(OrderedDict):
	"""
	Enumeration.
	"""

	def __init__(self, enumName):
		super(Enum, self).__init__()
		self.Name = enumName

	def Add(self, descriptionName, val):
		self[descriptionName] = val

	def Decompose(self):
		result = []
		for descriptionName, val in self.items():
			result.append((descriptionName, val))
		return result


class Struct(OrderedDict, Query, DefaultVal):
	"""
	Struct.
	A struct is a collection of base types, that form part of a message, as a separate member.
	"""
	def __init__(self, structName):
		super(Struct, self).__init__()
		DefaultVal.__init__(self)
		self.Name  = structName

	def AddType(self, memberName, memberType, val=0):
		self[memberName]          = memberType
		self.defaults[memberName] = val

	def Decompose(self):
		result = []
		for memberName in self:
			result.append((self[memberName], memberName))
		return result


class Array(OrderedDict, Query):

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


MessageMap = {}


class Message(OrderedDict, Query, DefaultVal):
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
		if messageTypeID in MessageMap:
			if self.Name != MessageMap[messageTypeID].Name:
				raise RuntimeError("Message [%s] already defined." % messageTypeID)
		self[self.HeaderName()] = MessageHeader(0, self.MessageTypeID)
		MessageMap[messageTypeID] = self

	# done by Interface.
	def SetPreamble(self, preamble):
		self[self.HeaderName()].OverridePreamble(preamble)

	def HeaderName(self):
		return 'Header'

	def AddType(self, memberName, membertype, val=0):
		self[memberName] = membertype
		self.defaults[memberName] = val

	def AddStruct(self, memberName, struct):
		self[memberName] = struct

	def AddArrayOfType(self, memberName, membertype):
		self[memberName] = Array(memberName, membertype)

	def AddArrayOfStruct(self, memberName, struct):
		self[memberName] = Array(memberName, struct.Name)

	def HasArray(self):
		for memberName in self:
			if self.IsArray(memberName):
				return True
		return False

	def Decompose(self):
		result = []
		for memberName in self:
			if hasattr(self[memberName], 'Decompose'):
				if self.IsStruct(memberName) or self.IsProtocolStruct(memberName):  # Recursive decomposition if we dont do this
					result.append((self[memberName].Name, memberName))
				else:
					kid = self[memberName].Decompose()
					result.extend(kid)
			else:
				result.append((self[memberName], memberName))
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

	enums = OrderedDict()
	hashdefines = OrderedDict()

	def __init__(self, interfaceName, interfacePreamble=0xDEAD):
		super(Interface, self).__init__()
		self[MessageHeader.Name] = MessageHeader(interfacePreamble, -1)
		self.Name = interfaceName
		self.InterfacePreamble = interfacePreamble

	def AddStruct(self, struct):
		self[struct.Name] = struct

	def AddMessage(self, message):
		message.SetPreamble(self.InterfacePreamble)
		self[message.Name] = message

	def AddEnum(self, enum):
		self.enums[enum.Name] = enum

	def AddHashDefine(self, name, val):
		self.hashdefines[name] = val

	def All(self):
		result = self.ProtocolStructs()
		result.extend(self.Structs())
		result.extend(self.Messages())
		return result

	def Messages(self):
		result = []
		for key in self:
			# Depending on the python setup, this will change. Which is a pain, because suddenly something doesnt work
			# if str(type(self[key])) == "<class 'tcp_gen.interface_base.Message'>" or str(type(self[key])) == "<class 'interface_base.Message'>":
			typeof = str(type(self[key]))
			if typeof.find('class') > -1 and typeof.find('Struct') == -1 and typeof.find('Message') > -1 and typeof.find('MessageHeader') == -1:
				result.append(self[key])
		return result

	def Structs(self):
		result = []
		for key in self:
			# Depending on the python setup, this will change. Which is a pain, because suddenly something doesnt work.
			# if str(type(self[key])) == "<class 'tcp_gen.interface_base.Struct'>" or str(type(self[key])) == "<class 'interface_base.Struct'>":
			typeof = str(type(self[key]))
			if typeof.find('class') > -1 and typeof.find('Struct') > -1 and typeof.find('Message') == -1 and typeof.find('MessageHeader') == -1:
				result.append(self[key])
		return result

	def ProtocolStructs(self):
		result = []
		for key in self:
			# Depending on the python setup, this will change. Which is a pain, because suddenly something doesnt work.
			# if str(type(self[key])) == "<class 'tcp_gen.interface_base.MessageHeader'>" or str(type(self[key])) == "<class 'interface_base.MessageHeader'>":
			typeof = str(type(self[key]))
			if typeof.find('class') > -1 and typeof.find('Struct') == -1 and typeof.find('MessageHeader') > -1:
				result.append(self[key])
		return result

	def Enums(self):
		result = []
		for n, e in self.enums.items():
			result.append(e)
		return result

	def HashDefines(self):
		result = []
		for k, v in self.hashdefines.items():
			result.append((k, v))
		return result

	def Decompose(self):
		result = []
		for name in self:
			result.extend(self[name].Decompose())
		return result

	def GetMessageTypeIDStr(self, struct):
		for a in MessageMap:
			if MessageMap[a].Name == struct.Name:
				return str(a).replace("[", "").replace("]", "").replace("'", "").replace("(", "").replace(")", "")
		return ""


