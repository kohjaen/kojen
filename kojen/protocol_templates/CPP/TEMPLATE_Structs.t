
/**
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
#include "allplatforms/basetypes.h"
#include "<<<CLASSNAME>>>Defines.h"
// Memory allocator not used here (as this header forms part of the messages, where it is used)
#if defined(_MSC_VER)
	#define __attribute__(x)
	#pragma pack(push,1)
#elif defined(__GNUC__)
#elif defined(__clang__)
#endif

#ifdef __arm__
// Might want to include this in a mix of C/C++.
#else
namespace <<<NAMESPACE>>>
{
#endif

	/**
	Structures used to within the protocol.
	*/

	/**[[[cog
	is_impl = False
	classname = ""
	structs = interface.Structs()
	for s in structs:
		structguts = language.DeclareStructMembers(s,interface, language.WhiteSpace(0))
		cog.outl("struct %s" % s.Name)
		cog.outl("{")
		for gut in structguts:
			cog.outl(gut)
		cog.outl("};\n")
	]]]*/

	///[[[end]]]
	
#ifdef __arm__
#else
}
#endif	

#if defined(_MSC_VER)
	#pragma pack(pop)
#elif defined(__GNUC__) || defined(__clang__)
	// Nothing required
#endif
