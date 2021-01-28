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

#ifdef __arm__
#pragma message("clientserver.h is not supported for ARM.")
#else
	
#ifdef USING_BOOST
//#define _ECHO_
//#define _LOG_DEBUG_

#define RUDIMENTARY_SERIAL_TIMEOUT

namespace Network
{
	CGEN_DECL_CLASS_PTR(Hive);
}
namespace boost
{
	CGEN_DECL_CLASS_PTR(thread);
}

namespace XKoJen 
{
	using namespace Network;

	CGEN_DECL_CLASS_PTR(CSerialConnection);
	CGEN_DECL_CLASS_PTR(IConnection);
	CGEN_DECL_CLASS_PTR(IMsgReceiver);
	CGEN_DECL_CLASS_PTR(IRawDataReceiver);
#ifdef RUDIMENTARY_SERIAL_TIMEOUT
	CGEN_DECL_CLASS_PTR(CWaitCondition);
#endif

	// SerialPort ****************************************
	CGEN_DECL_CLASS_PTR(CSerialPort);
	class KOJEN_API CSerialPort
	{
	public:
#ifdef RUDIMENTARY_SERIAL_TIMEOUT
		/** Use this constructor when speaking protocol.
			Default timeout (0ms) disables this feature.

			Note: the runtime behaviour of receiving raw streams or protocol messages can be changed
			by calling 'SetMsgReceiver' or 'SetRawDataReceiver' on the IConnection that is passed
			upon connection on 'onConnectionReady'. Its at this point where one has to set the connection
			to the protocol transmitter, so this could just as well be done at that point. This constructor
			is thus for convenience.
		*/
		static CSerialPort_ptr Create(IMsgReceiver_ptr receiver_of_messages, uint16_t timeout_ms = 0);
		/** Use this constructor when raw data is required.
			Default timeout (0ms) disables this feature.

			Note: the runtime behaviour of receiving raw streams or protocol messages can be changed
			by calling 'SetMsgReceiver' or 'SetRawDataReceiver' on the IConnection that is passed
			upon connection on 'onConnectionReady'. Its at this point where one has to set the connection
			to the protocol transmitter, so this could just as well be done at that point. This constructor
			is thus for convenience.
		*/
		static CSerialPort_ptr Create(IRawDataReceiver_ptr receiver_of_rawdata, uint16_t timeout_ms = 0);
		/** Modify the timeout...
		*/
		void SetTimeout(uint16_t timeout_ms);
#else
		/** Use this constructor when speaking protocol.
		*/
		static CSerialPort_ptr Create(IMsgReceiver_ptr receiver_of_messages);
		/** Use this constructor when raw data is required.
		*/
		static CSerialPort_ptr Create(IRawDataReceiver_ptr userrxhandler);
#endif
		virtual ~CSerialPort();

		/** KoJen : Starts the connection, and starts the service listening.
		*/
		void Connect(const std::string comport, unsigned int baudrate);
		/** KoJen : Disconnects the client
		*/
		void Disconnect() const;
		/** KoJen : Returns the connection used to TX/RX data when ready.
		*/
		boost::signals2::signal< void(IConnection_ptr) > onConnectionReady;
		/** KoJen : when the connection closes.
		*/
		boost::signals2::signal< void(IConnection_ptr) > onConnectionClosed;
		/** KoJen : query comport
		*/
		std::string ComPort() const;
		/** KoJen : query baudrate
		*/
		unsigned int BaudRate() const;
		/** Great for 1 device that you want to try and automatically connect to when it disconnects or has an error.
			(I.e. no external device management)
		*/
		void EnableAutoReconnectOnDisconnect(bool enable);

		bool IsConnected() const;
	protected:
		CSerialPort();
		/** KoJen : worker will do the connect, and run the hive.
		*/
		void DoConnect(const std::string comport, unsigned int baudrate);
		/** KoJen : thread that does the work.
		*/
		mutable boost::thread_ptr m_worker;
		/** KoJen : handle a server who is not yet present.
		*/
		void DoReconnect();
		/** KoJen : when a connection is accepted, it will call this.
		We can then notify interested parties.
		*/
		void DoConnectionAccepted(IConnection_ptr connection);
		void DoConnectionClosed(IConnection_ptr connection);
	private:
		IMsgReceiver_wptr m_msg_handler;		 // For users who want messages.
		CSerialConnection_ptr m_server;
		IRawDataReceiver_wptr m_rawdata_handler; // For users who want raw data.

#ifdef RUDIMENTARY_SERIAL_TIMEOUT
		uint16_t m_datarx_after_tx_timeout_ms;
#endif
		Hive_ptr m_hive;
		/** KoJen : Keep desired parameters for auto reconnect.
		*/
		std::string m_comport;
		unsigned int m_baudrate;
		//...except when disconnecting...
		mutable std::vector<boost::signals2::connection> m_auto_reconnections;

		bool m_do_auto_reconnect_on_disconnect;
		bool m_is_connected;
	};
}
#else
#pragma WARNING("serialport requires the usage of BOOST libraries,and the preprocessor definition 'USE_BOOST'")
#endif // USING_BOOST
#endif // __arm__