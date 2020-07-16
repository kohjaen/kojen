/**
[[[cog
import cog
from <<<PYIFGENNAME>>> import *
from LanguageCPP import *
interface = CreateInterface()
language  = LanguageCPP()
is_impl = False
classname = "C<<<CLASSNAME>>>Receiver"

for g in language.LicenseAgreement():
	cog.outl(g)

]]]

[[[end]]]
*/
#pragma once
#include <allplatforms/basetypes.h>
#include <allplatforms/IConnection.h>
#include <allplatforms/IMsgReceiver.h>
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
	CGEN_DECL_CLASS_PTR(C<<<CLASSNAME>>>NotHandledReceiver);
#endif // __arm__
	/** A Receiver for the undefined protocol (MSGID's not found). Perhaps someone needs backward compatibility with a very old generated interface.
	*/
	class <<<DLL_EXPORT>>> C<<<CLASSNAME>>>NotHandledReceiver
	{
	public:
		virtual void OnNotHandledMessageReceived( const uint8* data_buffer, const uint16& number_of_bytes ) = 0;
	};

#ifdef __arm__
#else
	CGEN_DECL_CLASS_PTR(C<<<CLASSNAME>>>Receiver);
#endif // __arm__
	/** A Receiver for the currently defined protocol (MSGID's found).
	*/
	class <<<DLL_EXPORT>>> C<<<CLASSNAME>>>Receiver : public IMsgReceiver
	{
	public:
		C<<<CLASSNAME>>>Receiver() : m_unhandledReceiver{nullptr} {}
		virtual ~C<<<CLASSNAME>>>Receiver(){ m_unhandledReceiver.reset();}
		/**
		IMsgReceiver overrides
		*/
		virtual void OnMessageReceived( const uint8* data_buffer, const uint16& number_of_bytes ) override;
		/**
		Preamble, i.e. the message start marker in the byte stream
		*/
		virtual uint16 Preamble() const override;
#ifdef __arm__
		/**
		See comments in base class.
		*/
		virtual uint16 LargestMessageSize() override;
#endif

		/**[[[cog
		is_impl = False
		classname = ""
		structs = interface.Messages()
		cog.outl("")
		for s in structs:
			cog.outl("// Message " + s.Name + " "+language.MessageDescriptor(interface,s)+" Receive handler. Override to handle specific messages.")
			cog.outl(language.DeclareFunction("void", classname, "On_"+s.Name+"_Received", is_impl, [("const "+language.PtrToTypeName(s.Name) + "&", "_data")], True)+";")
			cog.outl("")
		]]]*/

		//[[[end]]]
		
		void SetUnhandledReceiver(const C<<<CLASSNAME>>>NotHandledReceiver_ptr& unhandledReceiver){m_unhandledReceiver = unhandledReceiver;}
	protected:
		C<<<CLASSNAME>>>NotHandledReceiver_ptr m_unhandledReceiver;
	};
}

#if defined(_MSC_VER)
	#pragma pack(pop)
#elif defined(__GNUC__) || defined(__clang__)
	// Nothing required
#endif
