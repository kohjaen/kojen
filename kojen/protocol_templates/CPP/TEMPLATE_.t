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

#pragma once

/// {{{USER_<<<CLASSNAME>>>_HEADER_INCLUDES}}}
/// {{{USER_<<<CLASSNAME>>>_HEADER_INCLUDES}}}

#include "allplatforms/MsgHeader.h"
#ifdef __arm__
#include "allplatforms/allocator.h"
#endif // __arm__
#include "<<<CLASSNAME>>>Defines.h"
#include "<<<CLASSNAME>>>Structs.h"
#if defined(_MSC_VER)
	#define __attribute__(x)
	#pragma pack(push,1)
#elif defined(__GNUC__) || defined(__clang__)
	// Nothing required
#endif // _MSC_VER

namespace <<<NAMESPACE>>>
{
	/**[[[cog
	is_impl = False
	classname = ""
	structs = interface.All()
	for s in structs:
		comment = ""
		accessor = "->"
		if interface.IsProtocolStruct(s.Name) or interface.IsStruct(s.Name):
			accessor = "."
			comment = "Protocol definitions" if interface.IsProtocolStruct(s.Name) else "User definitions"

		hasArray = False
		if interface.IsMessageStruct(s.Name):
			hasArray = s.HasArray()
			comment = "Message " + s.Name + " "+language.MessageDescriptor(interface,s)+" definitions"

		# ARM SUPPORT : NO ARRAYS
		if hasArray:
			cog.outl("\n#ifdef __arm__")
			cog.outl('#error "Dynamic memory allocation on ARM Platform prohibited. Please modify your interface accordingly (hint : no arrays of types)"')
			cog.outl("#else")

		cog.outl("\n// ********************************************************")
		cog.outl("// " + comment)
		cog.outl("// ********************************************************")

		factoryparams = language.GetFactoryCreateParams(s,interface)
		if interface.IsMessageStruct(s.Name): # Protocol struct and other structs go into a seperate file -> underlying framework need to know of this (but not every interface that uses it)
			structguts = language.DeclareStructMembers(s,interface, language.WhiteSpace(0))
			cog.outl("struct %s" % s.Name)
			cog.outl("{")
			for gut in structguts:
				cog.outl(gut)
			# ARM SUPPORT : DYNAMIC MEMORY : This is only used for ARM, as PC based code can handle dynamic memory, as well as arrays of data...so this wont make sense.
			if interface.IsMessageStruct(s.Name):
				cog.outl("#ifdef __arm__")
				cog.outl('DECLARE_ALLOCATOR')
				cog.outl("#endif //__arm__")
			cog.outl("};\n")

		if interface.IsMessageStruct(s.Name):
			cog.outl("#ifdef __arm__")
			cog.outl(language.TypedefRawPtrToType(s.Name)+";")
			cog.outl('#else')
			cog.outl(language.TypedefSharedPtrToType(s.Name)+";")
			cog.outl("#endif //__arm__")
		cog.outl("// Factory for " + s.Name + ("" if not hasArray else " - Pass a valid pointer and no. array items to copy, or pass nullptr and desired no. items to allocate data for later use."))
		cog.outl('<<<DLL_EXPORT>>> ' + language.DeclareFunction(language.PtrToTypeName(s.Name) if interface.IsMessageStruct(s.Name) else s.Name, classname, "Create_"+s.Name,is_impl,factoryparams)+";")

		cog.outl("#ifdef __arm__")
		cog.outl("// Serialize " + s.Name + " to separate bytestream. User needs to ensure the stream is as big as the item being serialized. Returns the number of bytes serialized.")
		cog.outl('<<<DLL_EXPORT>>> ' + language.DeclareFunction("size_t", classname, "ToByteStream_"+s.Name,is_impl,[("const " + (s.Name if "."==accessor else language.PtrToTypeName(s.Name)) + "&","_to"),(language.ByteStreamTypeRawPtr(), 'result')])+";")
		cog.outl('#else')
		cog.outl("// Serialize " + s.Name + " to separate bytestream")
		cog.outl('<<<DLL_EXPORT>>> ' + language.DeclareFunction(language.ByteStreamTypeSharedPtr(), classname, "ToByteStream_"+s.Name,is_impl,[("const " + (s.Name if "."==accessor else language.PtrToTypeName(s.Name)) + "&","_to")])+";")
		cog.outl("#endif //__arm__")

		cog.outl("#ifdef __arm__")
		cog.outl("// Could be used to capture/playback a time-sequenced set of events. Not useful on the embedded side.")
		cog.outl("#else")
		cog.outl("// Serialize " + s.Name + " into a bytestream...")
		cog.outl("// Stream is resized accordingly.")
		cog.outl('<<<DLL_EXPORT>>> ' + language.DeclareFunction("void",classname,"IntoByteStream_"+s.Name,is_impl,[("const " + (s.Name if "."==accessor else language.PtrToTypeName(s.Name)) + "&","_to"),(language.ByteStreamTypeSharedPtr() + "&","byte_stream"), ("size_t&", "index")])+";")
		cog.outl("#endif //__arm__")

		cog.outl("// Serialize " + s.Name + " from a bytestream")
		cog.outl('<<<DLL_EXPORT>>> ' + language.DeclareFunction((s.Name if "."==accessor else language.PtrToTypeName(s.Name)),classname, "FromByteStream_"+s.Name,is_impl,[("const uint8*", "byte_stream"),("const size_t&", "streamsize"), ("size_t&", "index")])+";")

		# ARM SUPPORT : NO ARRAYS
		if hasArray:
			cog.outl("\n#endif //__arm__")
	]]] **/

	//[[[end]]]
}

#if defined(_MSC_VER)
	#pragma pack(pop)
#elif defined(__GNUC__) || defined(__clang__)
	// Nothing required
#endif
