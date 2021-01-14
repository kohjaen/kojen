/**

This file is part of 'KoJen'.

'KoJen' is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

'KoJen' is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with 'KoJen'.  If not, see <http://www.gnu.org/licenses/>.
For any feedback please contact the original author : koh.jaen@yahoo.de.

*/

#include "serialport.h"
#include "IConnection.h"
#include "IRawDataReceiver.h"

#ifdef __arm__
#pragma message "serialport.cpp is not supported for ARM."
#else

#ifdef USING_BOOST

#include "network.h"
#ifdef RUDIMENTARY_SERIAL_TIMEOUT
#include "waitcondition.h"
#endif

namespace XKoJen
{
#ifdef _LOG_DEBUG_
	boost::mutex global_stream_lock;
#endif
	
	//////////////////////////////////////////////////////////////////
	// Serial connection **************************************	
	class KOJEN_API CSerialConnection :
		public Network::SerialConnection
		, public XKoJen::IConnection
	{
	private:
		///@{ Network::Connection overrides
		// Async handlers...
		virtual void OnConnect(const std::string & comport, unsigned int baudrate)		override
		{
#ifdef _LOG_DEBUG_
			global_stream_lock.lock();
			std::cout << "[" << __FUNCTION__ << "] " << comport << ":" << baudrate << std::endl;
			global_stream_lock.unlock();
#endif        
			// Let users know
			m_sig_OnConnectionAccepted(boost::dynamic_pointer_cast<XKoJen::IConnection>(shared_from_this()));

			Recv();
		}
		virtual void OnSend(boost::shared_ptr< const std::vector< uint8 > > buffer) override
		{
#ifdef _LOG_DEBUG_
			global_stream_lock.lock();
			std::cout << "[" << __FUNCTION__ << "] " << buffer->size() << " bytes" << std::endl;
			global_stream_lock.unlock();
#endif
		}
		virtual void OnRecv(boost::shared_ptr< std::vector< uint8 > > buffer)		override
		{
#ifdef _LOG_DEBUG_
			global_stream_lock.lock();
			std::cout << "[" << __FUNCTION__ << "] " << buffer->size() << " bytes" << std::endl;
			global_stream_lock.unlock();
#endif
			// XKoJen -> This will handle fragmentation in the protocol layer.
			if (buffer->size() > 0) {
#ifdef RUDIMENTARY_SERIAL_TIMEOUT
				if (m_wait_for_bytes) {
					m_wait_for_bytes->DisableWait();
				}
#endif
				OnDataReceived(&((*buffer)[0]), (uint16)buffer->size());
			}

			// Start the next receive
			Recv();

#ifdef _ECHO_
			// Echo the data back
			Send(buffer);
#endif
		}
		virtual void OnTimer(const boost::posix_time::time_duration & delta)			override
		{
#ifdef _LOG_DEBUG_
			//global_stream_lock.lock();
			//std::cout << "[" << __FUNCTION__ << "] " << delta << std::endl;
			//global_stream_lock.unlock();
#endif		
			// Disconnects call the hive (stop). This needs to be done by a thread
			// that called 'run', other wise it sucks it up.
			boost::mutex::scoped_lock lock(m_request_disconnect_mutex);
			if (m_request_disconnect)
				Disconnect();
		}
		virtual void OnError(const boost::system::error_code & error)					override
		{
			// if this code is 'boost::system::errc::success', then its not an error.
			if ((error.value() == boost::asio::error::connection_aborted) ||
				(error.value() == boost::asio::error::connection_reset) ||
				(error.value() == boost::asio::error::eof)||
				(error.value() == boost::asio::error::operation_aborted))
			{
				m_sig_OnConnectionClosed(boost::dynamic_pointer_cast<XKoJen::IConnection>(shared_from_this()));
#ifdef _LOG_DEBUG_
				global_stream_lock.lock();
				std::cout << "[" << __FUNCTION__ << "] Connection closed : " << error << "(" << error.message() << ")" << std::endl;
				global_stream_lock.unlock();
#endif
			}
			else if (error.value() == boost::asio::error::connection_refused)
			{
				// Clients that received this, should continually try to connect until the server becomes present.
				m_sig_OnConnectionRefused();
			}
#ifdef _LOG_DEBUG_
			else if (error.value() != boost::system::errc::success) // success means the operation completed successfully
			{
				global_stream_lock.lock();
				std::cout << "[" << __FUNCTION__ << "] " << error << "(" << error.message() << ")" << std::endl;
				global_stream_lock.unlock();
			}
#endif		
		}
		///@}
#ifdef USING_BOOST
		boost::mutex m_send_lock;
#else
		std::mutex m_send_lock;
#endif
	public:
		CSerialConnection(boost::shared_ptr< Hive > hive) : SerialConnection(hive) {}
		virtual ~CSerialConnection() {}

#ifdef RUDIMENTARY_SERIAL_TIMEOUT
		/** Rudimentary timeout mechanism ...

			I say rudimentary, because one could do it on a message level :
			- after transmitting  MSG_ID(1), timeout if receipt MSG_ID(2) is not received timeously.

			current implementation will just clear the timeout on any received bytes after transmission.

			To disable : use 0

		*/
		uint16_t m_datarx_after_tx_timeout_ms;
		CWaitCondition_ptr m_wait_for_bytes;
#endif
		///@{ XKoJen::IConnection overrides
		virtual bool SendData(const uint8* data_buffer, const uint16& number_of_bytes) override
		{
#ifdef USING_BOOST
			boost::mutex::scoped_lock lock(m_send_lock); // exception safe
#else
			std::mutex::scoped_lock lock(m_send_lock);
#endif
			// XKoJen Send user defined data
			boost::shared_ptr<std::vector<uint8>> txbuf(new std::vector<uint8>);
			txbuf->resize(number_of_bytes);
			memcpy((void*) &(*txbuf)[0], (void*)data_buffer, number_of_bytes);

			Send(txbuf);
			bool ok = true;
#ifdef RUDIMENTARY_SERIAL_TIMEOUT
			if (m_wait_for_bytes) {
				m_wait_for_bytes->EnableWait();
				ok = m_wait_for_bytes->TimedWait(m_datarx_after_tx_timeout_ms);
			}
#endif

			return ok; // how to return status here being asynchronous and all?
		}
		///@}
	};
	
	// Serial Port ****************************************
#ifdef RUDIMENTARY_SERIAL_TIMEOUT
	CSerialPort_ptr CSerialPort::Create(IMsgReceiver_ptr receiver_of_messages, uint16_t timeout_ms/* = 0*/)
#else
	CSerialPort_ptr CSerialPort::Create(IMsgReceiver_ptr receiver_of_messages)
#endif
	{
		CSerialPort_ptr client(new CSerialPort());
		client->m_hive.reset(new Hive());
		client->m_msg_handler = receiver_of_messages;
#ifdef RUDIMENTARY_SERIAL_TIMEOUT
		client->m_datarx_after_tx_timeout_ms = timeout_ms;
#endif
		return client;
	}

#ifdef RUDIMENTARY_SERIAL_TIMEOUT
	CSerialPort_ptr CSerialPort::Create(IRawDataReceiver_ptr receiver_of_rawdata, uint16_t timeout_ms/* = 0*/)
#else
	CSerialPort_ptr CSerialPort::Create(IRawDataReceiver_ptr receiver_of_rawdata)
#endif
	{
		CSerialPort_ptr client(new CSerialPort());
		client->m_hive.reset(new Hive());
		client->m_rawdata_handler = receiver_of_rawdata;
#ifdef RUDIMENTARY_SERIAL_TIMEOUT
		client->m_datarx_after_tx_timeout_ms = timeout_ms;
#endif
		return client;
	}

	CSerialPort::~CSerialPort()
	{
		Disconnect();
	}
	CSerialPort::CSerialPort() 
		: m_comport("")
		, m_baudrate(0) 
		, m_do_auto_reconnect_on_disconnect(false)
		, m_is_connected(false)
#ifdef RUDIMENTARY_SERIAL_TIMEOUT
		, m_datarx_after_tx_timeout_ms(0)
#endif
	{
	}
#ifdef RUDIMENTARY_SERIAL_TIMEOUT
	void CSerialPort::SetTimeout(uint16_t timeout_ms)
	{
		m_datarx_after_tx_timeout_ms = timeout_ms;
	}
#endif

	void CSerialPort::DoConnect(const std::string comport, unsigned int baudrate)
	{
		m_comport = comport;
		m_baudrate = baudrate;

		for (auto& c : m_auto_reconnections) // When explicitly disconnecting, no more auto-reconnect
			c.disconnect();
		m_auto_reconnections.clear();

		m_hive->Stop();
		m_hive->Reset();
		if (m_server)
			m_server->Disconnect();

		m_server.reset(new CSerialConnection(m_hive));

#ifdef RUDIMENTARY_SERIAL_TIMEOUT
		m_server->m_datarx_after_tx_timeout_ms = m_datarx_after_tx_timeout_ms;
		// timeout of 0 = disabled!
		if (m_datarx_after_tx_timeout_ms != 0) {
			m_server->m_wait_for_bytes = CWaitCondition::Create(false);
		}
		else{
			m_server->m_wait_for_bytes.reset();
		}
#endif
		if(auto protocolhandler = m_msg_handler.lock())
			m_server->SetMsgReceiver(protocolhandler.get());
		if (auto rawdatahandler = m_rawdata_handler.lock())
			m_server->SetRawDataReceiver(rawdatahandler.get());
		
		m_auto_reconnections.push_back(m_server->m_sig_OnConnectionRefused.connect(boost::bind(&CSerialPort::DoReconnect, this)));
		m_auto_reconnections.push_back(m_server->m_sig_OnConnectionClosed.connect(boost::bind(&CSerialPort::DoConnectionClosed, this, _1)));
		m_auto_reconnections.push_back(m_server->m_sig_OnConnectionAccepted.connect(boost::bind(&CSerialPort::DoConnectionAccepted, this, _1)));
		m_server->Bind(&comport[0], baudrate);
		m_hive->Run();
	}
	void CSerialPort::Connect(const std::string comport, unsigned int baudrate)
	{
		m_worker.reset(new boost::thread(boost::bind(&CSerialPort::DoConnect, this, comport, baudrate)));
	}
	void CSerialPort::Disconnect() const
	{
		if(m_server)
			m_server->Disconnect();
		if(m_hive)
			if(!m_hive->HasStopped())
				m_hive->Stop();

		for (auto& c : m_auto_reconnections) // When explicitly disconnecting, no more auto-reconnect
			c.disconnect();
		m_auto_reconnections.clear();

		if (m_worker)
		{
			m_worker->interrupt();
			if (m_worker->joinable()) {
				if (m_worker->get_id() != boost::this_thread::get_id()) { // if the calling thread is this thread...don't join...exception will be thrown.
					m_worker->timed_join(boost::posix_time::seconds(1));
				}
			}
			m_worker.reset();
		}
	}
	std::string CSerialPort::ComPort() const
	{
		return m_comport;
	}

	unsigned int CSerialPort::BaudRate() const
	{
		return m_baudrate;
	}

	void CSerialPort::DoReconnect()
	{
		// When unplugging a device (i.e. to power it down) reconnect 
		// happens so quick that the GUI thread gets blocked. So put in a delay 
		boost::this_thread::sleep_for(boost::chrono::milliseconds(200));

		// If this happens, its on the same thread that called 'run'.
		// Hive needs to be stopped/reset from another thread, so that the last thread can be released.
		// This is thus done in 'DoConnect' which is always a new thread.
		Connect(m_comport, m_baudrate);
	}

	void CSerialPort::DoConnectionAccepted(IConnection_ptr connection)
	{
		m_is_connected = true;
		onConnectionReady(connection);
	}
	void CSerialPort::DoConnectionClosed(IConnection_ptr connection)
	{
		m_is_connected = false;
		onConnectionClosed(connection);
		if(m_do_auto_reconnect_on_disconnect)
			DoReconnect();
	}
	bool CSerialPort::IsConnected() const 
	{ 
		return m_is_connected; 
	}
	void CSerialPort::EnableAutoReconnectOnDisconnect(bool enable)
	{
		m_do_auto_reconnect_on_disconnect = enable;
	}
	
}

#endif // USING_BOOST
#endif // __arm__