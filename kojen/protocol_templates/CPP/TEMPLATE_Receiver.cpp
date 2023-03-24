/**
 * @file
 * @ingroup <<<GROUP>>>
 * @brief   <<<BRIEF>>>
 *
 *          This code is Autogenerated from '<<<PYIFGENNAME>>>.py' with the MIT License.
 *          As such, please only hand-code within 'USER' tags.
 *
 * @author  <<<AUTHOR>>>
 */
#include "<<<CLASSNAME>>>Receiver.h"
namespace <<<NAMESPACE>>>
{
    //#define DEBUG_OUT

    /*uint16 <<<CLASSNAME>>>Receiver::Preamble() const
    {
    }*/

    void <<<CLASSNAME>>>Receiver::OnMessageReceived( const uint8* data_buffer, const uint32& number_of_bytes )
    {
        // IMsgReceiver is guaranteed to get complete messages.
        const sMsgHeader* header = (sMsgHeader*)(&data_buffer[0]);
        switch(header->TypeID)
        {
        <<<PER_MSG_BEGIN>>>
        case <<<MSGID>>>: On<<<MSGNAME>>>Received(reinterpret_cast<const <<<MSGNAME>>>*>(&data_buffer[0])); break;
        <<<PER_MSG_END>>>
        default:
#ifdef DEBUG_OUT
            printf("Message (%i) not supported.\r\n", TypeID);
#endif
            if(unhandledReceiver != nullptr)
                unhandledReceiver->OnNotHandledMessageReceived(data_buffer,number_of_bytes);
            break;
        }
    }
}
