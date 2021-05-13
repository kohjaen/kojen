/**

    MIT License

    Copyright (c) 2015 Eugene Grobbelaar (email : koh.jaen@yahoo.de)

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

*/

#pragma once
#include "basetypes.h"
#include "IMsgReceiver.h"
#include "IRawDataReceiver.h"

#if defined(__arm__)
#else
#ifdef USING_BOOST
#include <boost/signals2.hpp>
#endif
#endif // __arm__

#if defined(__arm__)
#define FRAGMENT_BUF_SIZE 512
#endif

namespace XKoJen
{
    /** Class IConnection knows deals with sending and receiving bytes, only using sMsgHeader. It is thus message(communication) protocol independant.
        Derived classes are to implement a transport-layer specific transmission and reception of bytes (eg. TCP/UDP/RS232 etc).
        Its primary purpose is to
            - provide a layer independant interface for byte transmission and reception -> it is thus easy to route byte streams between physical layers.
            - know how to extract messages (using sMsgHeader) from bytestreams...it passes messages (as a chunk of bytes) to the derived IMsgReceiver for specific communication
              protocol handling.

        It thus requires a IMsgReceiver upon creation.
    */
#if defined(__arm__)
    class IConnection;
    typedef IConnection* IConnection_ptr;
#else
    CGEN_DECL_CLASS_PTR(IConnection);
#endif // __arm__
    class KOJEN_API IConnection
    {
    public:
#if defined(__arm__)
#else
        /** Lets users define their own handlers for disconnection.
        */
#ifdef USING_BOOST
        boost::signals2::signal< void (IConnection_ptr) > m_sig_OnConnectionClosed;
#endif
        /** Lets derived classes try to reconnect to servers who are not there yet (activley refused). Most likely only useful for TCPIP.
        */
#ifdef USING_BOOST
        boost::signals2::signal< void (void) > m_sig_OnConnectionRefused;
#endif
        /** Lets derived classes know when the connection has been accepted.
        */
#ifdef USING_BOOST
        boost::signals2::signal< void (IConnection_ptr) > m_sig_OnConnectionAccepted;
#endif
        /** Request this connected to disconnect.
        */
        void RequestDisconnect();
#endif // __arm__
        /** Send data via this connection. Return failure or success.
        */
        virtual bool SendData( const uint8* data_buffer, const uint16& number_of_bytes ) = 0;

        /** Set the receiver for protocol communications. No messages will flow otherwise...
            Setting this will clear the rawdatareceiver.
        */
        void SetMsgReceiver(IMsgReceiver* receiver);
        bool HasMsgReceiver() const;
        /** Set the receiver for raw data communications. No data will flow otherwise...
            Setting this will clear the message receiver
        */
        void SetRawDataReceiver(IRawDataReceiver* receiver);
        bool HasRawDataReceiver() const;
        virtual ~IConnection();

#if defined(__arm__)
        /** For the case where unknown data can be received that is larger than the fragment buf...set this flag...
        */
        bool HasDataExceedingFragmentBufferSize();

        IConnection();
    protected:
#else
    protected:
        IConnection();
        std::mutex									m_request_disconnect_mutex;
        bool										m_request_disconnect;
#endif // __arm__
        /** Each derived transport layer connection should assume that there could be some fragmentation
            in the data that flows (either it is a bunch of messages concatenated, in the case of a fast burst of small messages,
            or its seperate parts of a larger message).

            Therefore, each derived transport layer connection should enter all its received data here, it will handle this.
        */
        void OnDataReceived( const uint8* data_buffer, const uint32& number_of_bytes );

#if defined(__arm__)
        uint8  m_fragment_buffer[FRAGMENT_BUF_SIZE];
        uint16 m_fragment_buffer_cnt;
#else
        std::vector< uint8 > m_fragment_buffer;
#endif
        uint32 m_fragment_buffer_bytes_required;

        IMsgReceiver* m_msg_receiver;
        IRawDataReceiver* m_rawdata_receiver;

        uint16 m_receiver_preamble;
        uint8 m_receiver_preamble_0;
        uint8 m_receiver_preamble_1;

        IConnection( const IConnection &c );
        IConnection& operator=( const IConnection &c );

#if defined(__arm__)
        uint16 m_largest_message_size;
        bool m_has_data_exceeding_fragment_buffer_size;
#endif // __arm__

        // This connection parses a specific header. Cache the size once.
        const uint16 m_sizeofheader;
    };
}