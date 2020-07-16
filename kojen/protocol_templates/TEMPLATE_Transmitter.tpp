/**
[[[cog
import cog
from <<<PYIFGENNAME>>> import *
from LanguageCPP import *
interface = CreateInterface()
language  = LanguageCPP()
is_impl = True
classname = "C<<<CLASSNAME>>>Transmitter"
structs = interface.Messages()

for g in language.LicenseAgreement():
	cog.outl(g)

]]]

[[[end]]]

*/
#include "<<<CLASSNAME>>>Transmitter.h"
#include <assert.h>
namespace <<<NAMESPACE>>>
{
	/**
	Implementations for message transmission.
	*/
	
	/**
	Transmitters.			
	*/

	/**[[[cog
	cog.outl("")
	for s in structs:
		cog.outl(language.DeclareFunction("bool", classname, "Transmit_"+s.Name, is_impl, [("const "+language.PtrToTypeName(s.Name) + "&", "_data"), ("int8","retries")]))
		cog.outl("{")
		
		cog.outl(language.WhiteSpace(0) + "bool ok = false;")
		cog.outl(language.WhiteSpace(0) + "for (; retries >= 0 && !ok && (m_connection != nullptr); retries--) {")
		
		hasArray = s.HasArray() #// TODO : This seems redundant (and less efficient) on already tightly packed data...
		if hasArray: # required to get all the array data into the buffer
			cog.outl(language.WhiteSpace(1) + language.InstantiateType(language.ByteStreamTypeSharedPtr(), 'bytestream',"ToByteStream_"+s.Name+"(_data)")+";")
			cog.outl(language.WhiteSpace(1) + "ok = ok || m_connection->SendData(&(*bytestream)[0], bytestream->size());")
		else:
			cog.outl(language.WhiteSpace(1) + "ok = ok || m_connection->SendData(  (uint8*)&(*_data), sizeof("+s.Name+")  );")

		cog.outl(language.WhiteSpace(0) + "}")
		cog.outl(language.WhiteSpace(0) + "return ok;")
		
		cog.outl("}")
	]]]*/

	//[[[end]]]

	// Interface Test : Sends all messages, with autogenerated payloads.
	void  C<<<CLASSNAME>>>Transmitter::TestSendAll()
	{
		/*[[[cog
		cog.outl("")
		for s in structs:
			a_test_writer = UnitTestWriter(interface,s,language,"ptr2"+s.Name)
			cog.outl(language.WhiteSpace(0) + language.OpenBrace())
			guts, to_delete = a_test_writer.WRITE_CREATE_MESSAGE(language.WhiteSpace(1))
			for g in guts:
				cog.outl(g)
			cog.outl("")

			hasArray = s.HasArray()

			cog.outl("#ifdef __arm__")
			guts = a_test_writer.WRITE_MESSAGE_TO_STREAM(language.WhiteSpace(1), True)
			for g in guts:
				cog.outl(g)

			cog.outl(language.WhiteSpace(1)+ 'm_connection->SendData( (uint8*)&' + a_test_writer.bytestream_of_message_variable_name + '[0], sizeof('+s.Name+'));')

			cog.outl("")
			cog.outl(language.WhiteSpace(1) + "// ARM doesnt use shared_ptr's...Don't leak memory")
			for d in to_delete:
				cog.outl(language.WhiteSpace(1) + "delete " + d + ";")

			cog.outl('#else')
			guts = a_test_writer.WRITE_MESSAGE_TO_STREAM(language.WhiteSpace(1))
			for g in guts:
				cog.outl(g)

			if hasArray:
				cog.outl(language.WhiteSpace(1)+ 'm_connection->SendData(&(*' + a_test_writer.bytestream_of_message_variable_name + ')[0],'+ a_test_writer.bytestream_of_message_variable_name + '->size() );')
			else:
				cog.outl(language.WhiteSpace(1)+ 'm_connection->SendData( (uint8*)&(*' + a_test_writer.bytestream_of_message_variable_name + ')[0], sizeof('+s.Name+'));')

			cog.outl("#endif //__arm__")

			cog.outl(language.WhiteSpace(0) + language.CloseBrace())
			#  (uint8*)&(*_data), sizeof("+s.Name+")  
			cog.outl("")

		]]]*/

		//[[[end]]]
	}

}
