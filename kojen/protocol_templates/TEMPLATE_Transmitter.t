/**
[[[cog
import cog
from <<<PYIFGENNAME>>> import *
from LanguageCPP import *
interface = CreateInterface()
language  = LanguageCPP()
is_impl = False
classname = "C<<<CLASSNAME>>>Transmitter"

for g in language.LicenseAgreement():
	cog.outl(g)

]]]

[[[end]]]
*/
#pragma once
#include <allplatforms/basetypes.h>
#include <allplatforms/IConnection.h>
#include "<<<CLASSNAME>>>.h"
#if defined(_MSC_VER)
	#define __attribute__(x)
	#pragma pack(push,1)
#elif defined(__GNUC__) || defined(__clang__)
	// Nothing required
#endif

namespace <<<NAMESPACE>>>
{
	using namespace XKoJen;
#ifdef __arm__
#else
	CGEN_DECL_CLASS_PTR(C<<<CLASSNAME>>>Transmitter);
#endif // __arm__
	class <<<DLL_EXPORT>>> C<<<CLASSNAME>>>Transmitter
	{
	public:
		explicit C<<<CLASSNAME>>>Transmitter(IConnection_ptr connection):m_connection(connection){}
		/**
		Functions used for message transmission.
		*/
		/**[[[cog
		structs = interface.Messages()
		cog.outl("")
		for s in structs:
			cog.outl("// Message " + s.Name + " "+language.MessageDescriptor(interface,s)+" Transmitter.")
			cog.outl(language.DeclareFunction("bool", classname, "Transmit_"+s.Name, is_impl, [("const "+language.PtrToTypeName(s.Name) + "&", "_data"), ("int8","retries = 5")])+";")
			cog.outl("")
		]]]*/

		//[[[end]]]

		// Interface Test : Sends all messages, with autogenerated payloads.
		void  TestSendAll();

	protected:
		IConnection_ptr m_connection;
	private:
		C<<<CLASSNAME>>>Transmitter(){}
	};
}

#if defined(_MSC_VER)
	#pragma pack(pop)
#elif defined(__GNUC__) || defined(__clang__)
	// Nothing required
#endif
