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
#if defined(_MSC_VER)
	// Nothing required
#elif defined(__GNUC__) || defined(__clang__)
	// Nothing required
#endif // _MSC_VER

/**[[[cog
cog.outl("\n")
hashdefines = interface.HashDefines()
for (k,v) in hashdefines:
	cog.outl(language.DeclareHashDefine(k,v))
cog.outl("\n")
]]] **/

//[[[end]]]

#ifdef __arm__
// Might want to include this in a mix of C/C++.
#else
namespace <<<NAMESPACE>>>
{
#endif

	/**[[[cog
	enums = interface.Enums()
	whitespace = "\t"
	for e in enums:
		lines = language.DeclareEnum(e, whitespace)
		#for l in lines:
		cog.outl(lines)
	cog.outl("\n")
	]]] **/
	//[[[end]]]

#ifdef __arm__
#else
}
#endif	

#if defined(_MSC_VER)
	// Nothing required
#elif defined(__GNUC__) || defined(__clang__)
	// Nothing required
#endif
