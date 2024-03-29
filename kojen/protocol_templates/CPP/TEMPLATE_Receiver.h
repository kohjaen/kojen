/**
 * @file
 * @ingroup <<<GROUP>>>
 * @brief   <<<BRIEF>>>
 *
 *          This code is Autogenerated from '<<<PYIFGENNAME>>>' with the MIT License.
 *          As such, please only hand-code within 'USER' tags.
 *
 * @author  <<<AUTHOR>>>
 */

#ifndef <<<CLASSNAME>>>_RECEIVER_HPP
#define <<<CLASSNAME>>>_RECEIVER_HPP

#include "allplatforms/basetypes.h"
#include "allplatforms/IConnection.h"
#include "allplatforms/IMsgReceiver.h"
#include "<<<CLASSNAME>>>.h"

namespace <<<NAMESPACE>>>
{
    /** A Receiver for the unhandled/undefined protocol messages(MSGID's not found). 
     *  Can also be used for backward compatibility.
    */
    class <<<DLL_EXPORT>>> <<<CLASSNAME>>>NotHandledReceiver
    {
    public:
        virtual void OnNotHandledMessageReceived( const uint8* data_buffer, const uint32& number_of_bytes ) = 0;
    };

    /** A Receiver for the defined protocol.
    */
    class <<<DLL_EXPORT>>> <<<CLASSNAME>>>Receiver : public XKoJen::IMsgReceiver
    {
    public:
        <<<CLASSNAME>>>Receiver() : unhandledReceiver{nullptr} {}
        virtual ~<<<CLASSNAME>>>Receiver(){ unhandledReceiver = nullptr;}
        /** IMsgReceiver overrides
         */
        virtual void OnMessageReceived( const uint8* data_buffer, const uint32& number_of_bytes ) override;
        /** Preamble (start marker in byte stream)
         */
        //virtual uint16 Preamble() const override;

        /** Receiver functions for decoded protocol messages.
          */
         <<<PER_MSG_BEGIN>>>
        virtual void On<<<MSGNAME>>>Received(const <<<MSGNAME>>>* data){};
        <<<PER_MSG_END>>>

        void SetUnhandledReceiver(<<<CLASSNAME>>>NotHandledReceiver& unhandledReceiver){this->unhandledReceiver = &unhandledReceiver;}
    protected:
        <<<CLASSNAME>>>NotHandledReceiver* unhandledReceiver;
    };
}

#endif // #ifndef <<<CLASSNAME>>>_RECEIVER_HPP