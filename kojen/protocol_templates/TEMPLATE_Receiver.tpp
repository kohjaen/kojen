/*
[[[cog
import cog
from <<<PYIFGENNAME>>> import *
from LanguageCPP import *
interface = CreateInterface()
language  = LanguageCPP()
is_impl = True
classname = "C<<<CLASSNAME>>>Receiver"
structs = interface.Messages()

for g in language.LicenseAgreement():
	cog.outl(g)

]]]

[[[end]]]
*/

#include "<<<CLASSNAME>>>Receiver.h"
#ifdef __arm__
#include <stdio.h>
#endif //__arm__
namespace <<<NAMESPACE>>>
{
	//#define DEBUG_OUT

	/**
	Implementations for message reception.
	*/
#ifdef __arm__
	uint16 C<<<CLASSNAME>>>Receiver::LargestMessageSize()
	{
		uint16 result(0);
		/**[[[cog
		for s in structs:
			cog.outl("if(sizeof("+s.Name+") > result)")
			cog.outl(language.WhiteSpace(0) + "result = sizeof("+s.Name+");")
		]]]*/

		//[[[end]]]
		return result;
	}
#endif
	uint16 C<<<CLASSNAME>>>Receiver::Preamble() const
	{
		/**[[[cog
		msgHeader = interface[MessageHeader.Name]
		cog.outl("// Preamble is chosen by interface configurator.")
		cog.outl("return " + str(msgHeader.defaults[msgHeader.Preamble()]) + ";")
		]]]*/

		//[[[end]]]
	}

	void C<<<CLASSNAME>>>Receiver::OnMessageReceived( const uint8* data_buffer, const uint16& number_of_bytes )
	{
		/**[[[cog
		msgHeader = interface[MessageHeader.Name]

		cog.outl("// Deriving from class IMsgReceiver means data is passed here as solid messages.")
		cog.outl(MessageHeader.Name+"* header = ("+MessageHeader.Name+"*)(&data_buffer[0]);")
		members = msgHeader.Decompose()
		for mem in members:
			cog.outl(language.InstantiateType(mem[0], mem[1], "header->"+mem[1])+";")

		cog.outl("size_t index = 0;")
		cog.outl("")
		for s in structs:
			# dont use the interface msgheader -> use each individual messages header for is defaults.
			msgHeader = s[s.HeaderName()]
			cog.outl("if(" + msgHeader.TypeID() + " == " + str(msgHeader.defaults[msgHeader.TypeID()])+")")
			cog.outl("{")
			cog.outl(language.WhiteSpace(0) +language.PtrToTypeName(s.Name)+ " msg = FromByteStream_"+s.Name+"(data_buffer,number_of_bytes,index);")
			cog.outl(language.WhiteSpace(0) +"On_"+s.Name+"_Received(msg);")
			cog.outl("#ifdef __arm__")
			cog.outl(language.WhiteSpace(0) + '// Once handled, return to allocator for re-use ...')
			cog.outl(language.WhiteSpace(0) + 'delete msg;')
			cog.outl("#endif //__arm__")
			cog.outl(language.WhiteSpace(0) +"return;")
			cog.outl("}")
		]]]*/

		//[[[end]]]

		// Not found -> Unhandled. Perhaps someone wants to maintain backward compatibility...
		if(m_unhandledReceiver != nullptr)
			m_unhandledReceiver->OnNotHandledMessageReceived(data_buffer,number_of_bytes);
#ifdef DEBUG_OUT
		printf("Message (%i) not supported.\r\n", TypeID);
#endif
	}

	/**
	Receivers.
	*/

	/**[[[cog
	cog.outl("")
	for s in structs:
		cog.outl(language.DeclareFunction("void", classname, "On_"+s.Name+"_Received", is_impl, [("const "+language.PtrToTypeName(s.Name) + "&", "_data")]))
		cog.outl("{")
		cog.outl("#ifdef DEBUG_OUT")
		cog.outl(language.WhiteSpace(0) + language.PrintMessage('"Received message '+s.Name+'\\r\\n"'))
		cog.outl("#endif")
		cog.outl("}")
	]]]*/

	//[[[end]]]
}
