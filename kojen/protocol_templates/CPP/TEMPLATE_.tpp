/*
[[[cog
import cog
from <<<PYIFGENNAME>>> import *
from LanguageCPP import *
interface = CreateInterface()
language  = LanguageCPP()

for g in language.LicenseAgreement():
	cog.outl(g)

]]]

[[[end]]]
*/
#include "<<<CLASSNAME>>>.h"
#ifdef __arm__
#include <string.h>
#include <stdio.h>
#include <assert.h>
#endif //__arm__
namespace <<<NAMESPACE>>>
{
	/**
	Message Header/Structures used to describe the protocol.
	*/
	/**[[[cog
	is_impl = True
	classname = ""
	structs = interface.All()
	for s in structs:

		comment = ""
		accessor = "->"
		result = language.InstantiatePtrToType(s.Name, "result")
		if interface.IsProtocolStruct(s.Name) or interface.IsStruct(s.Name):
			accessor = "."
			comment = "Protocol definitions" if interface.IsProtocolStruct(s.Name) else "User definitions"
			result = language.InstantiateType(s.Name,"result")

		if interface.IsMessageStruct(s.Name):
			comment = "Message " + s.Name + " "+language.MessageDescriptor(interface,s)+" definitions"

		cog.outl("\n// ********************************************************")
		cog.outl("// " + comment)
		cog.outl("// ********************************************************")

		# ARM SUPPORT : DYNAMIC MEMORY : This is only used for ARM, as PC based code can handle dynamic memory, as well as arrays of data...so this wont make sense.
		if interface.IsMessageStruct(s.Name):
			cog.outl("#ifdef __arm__")
			cog.outl('IMPLEMENT_ALLOCATOR('+s.Name+', 0, 0)')
			cog.outl("#endif //__arm__\n")
			
		factoryparams = language.GetFactoryCreateParams(s,interface)
		structmembers = s.Decompose()

		cog.outl(language.DeclareFunction(language.PtrToTypeName(s.Name) if interface.IsMessageStruct(s.Name) else s.Name , classname, "Create_"+s.Name,is_impl,factoryparams))
		cog.outl("{")
		cog.outl(language.WhiteSpace(0)+result+";")
		guts = language.InstantiateStructMembers(s,interface,language.WhiteSpace(0),"result",accessor)
		for g in guts:
			cog.outl(g)
		cog.outl(language.WhiteSpace(0)+"return result;")
		cog.outl("}\n")

		# TOBYTESTREAM
		cog.outl("#ifdef __arm__")
		cog.outl(language.DeclareFunction("size_t", classname, "ToByteStream_"+s.Name,is_impl,[("const " + (s.Name if "."==accessor else language.PtrToTypeName(s.Name)) + "&","_to"),(language.ByteStreamTypeRawPtr(), 'result')]))
		cog.outl("{")
		##cog.outl(language.WhiteSpace(0)+language.InstantiatePtrToType2(language.ByteStreamTypeSharedPtr(), 'result',language.ByteStreamType())+";")
		is_arm = True
		guts = language.SerializeStructToByteStream(s,interface,language.WhiteSpace(0),"result","_to",accessor, is_arm)
		for g in guts:
			cog.outl(g)
		cog.outl(language.WhiteSpace(0)+"return streamsize;")
		cog.outl("}\n")
		cog.outl('#else')
		cog.outl(language.DeclareFunction(language.ByteStreamTypeSharedPtr(), classname, "ToByteStream_"+s.Name,is_impl,[("const " + (s.Name if "."==accessor else language.PtrToTypeName(s.Name)) + "&","_to")]))
		cog.outl("{")
		cog.outl(language.WhiteSpace(0)+language.InstantiatePtrToType2(language.ByteStreamTypeSharedPtr(), 'result',language.ByteStreamType())+";")
		guts = language.SerializeStructToByteStream(s,interface,language.WhiteSpace(0),"result","_to",accessor)
		for g in guts:
			cog.outl(g)
		cog.outl(language.WhiteSpace(0)+"return result;")
		cog.outl("}\n")
		cog.outl("#endif //__arm__")

		# INTOBYTESTREAM
		cog.outl("#ifdef __arm__")
		cog.outl("#else")
		cog.outl(language.DeclareFunction("void",classname,"IntoByteStream_"+s.Name,is_impl,[("const " + (s.Name if "."==accessor else language.PtrToTypeName(s.Name)) + "&","_to"),(language.ByteStreamTypeSharedPtr() + "&","byte_stream"), ("size_t&", "index")]))
		cog.outl("{")
		guts = language.SerializeStructIntoByteStream(s,interface,language.WhiteSpace(0),"_to","byte_stream","index",accessor)
		for g in guts:
			cog.outl(g)
		cog.outl("}\n")
		cog.outl("#endif //__arm__")

		cog.outl(language.DeclareFunction((s.Name if "."==accessor else language.PtrToTypeName(s.Name)),classname, "FromByteStream_"+s.Name,is_impl,[("const uint8*", "byte_stream"),("const size_t&", "streamsize"), ("size_t&", "index")]))
		cog.outl("{")
		cog.outl(language.WhiteSpace(0)+result+";")
		guts = language.SerializeStructFromByteStream("FromByteStream_"+s.Name,s,interface,language.WhiteSpace(0),"byte_stream","index","result",accessor)
		for g in guts:
			cog.outl(g)
		cog.outl(language.WhiteSpace(0)+"return result;")
		cog.outl("}\n")
	]]] **/

	///[[[end]]]
}