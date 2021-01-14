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

#include "tcpipclientserver.h"
#include "IConnection.h"

#ifdef __arm__
#pragma message "tcpipclientserver.cpp is not supported for ARM."
#else

#ifdef USING_BOOST

#include "network.h"

namespace XKoJen
{
#ifdef _LOG_DEBUG_
	boost::mutex global_stream_lock;
#endif	

	// TCPIP connection **************************************	
    class KOJEN_API CTCPIPConnection : 
		public Network::Connection
	   ,public XKoJen::IConnection
    {
    private:
		///@{ Network::Connection overrides
        // Async handlers...
        virtual void OnAccept( const std::string & host, uint16 port )				override
		{
#ifdef _LOG_DEBUG_
			global_stream_lock.lock();
			std::cout << "[" << __FUNCTION__ << "] " << host << ":" << port << std::endl;
			global_stream_lock.unlock();
#endif        
			// Let users know
			m_sig_OnConnectionAccepted(boost::dynamic_pointer_cast<XKoJen::IConnection>(shared_from_this()));

			Recv();
		}
        virtual void OnConnect( const std::string & host, uint16 port )				override
		{
#ifdef _LOG_DEBUG_
			global_stream_lock.lock();
			std::cout << "[" << __FUNCTION__ << "] " << host << ":" << port << std::endl;
			global_stream_lock.unlock();
#endif        
			// Let users know
			m_sig_OnConnectionAccepted(boost::dynamic_pointer_cast<XKoJen::IConnection>(shared_from_this()));

			Recv();
		}
        virtual void OnSend( boost::shared_ptr< const std::vector< uint8 > > buffer ) override
		{
#ifdef _LOG_DEBUG_
			global_stream_lock.lock();
			std::cout << "[" << __FUNCTION__ << "] " << buffer->size() << " bytes" << std::endl;
			//for( size_t x = 0; x < buffer->size(); ++x )
			//{
			//	std::cout << std::hex << std::setfill( '0' ) <<
			//		std::setw( 2 ) << (int)(*buffer)[ x ] << " ";
			//	if( ( x + 1 ) % 16 == 0 )
			//	{
			//		std::cout << std::endl;
			//	}
			//}
			//std::cout << std::endl;
			global_stream_lock.unlock();
#endif
		}
        virtual void OnRecv( boost::shared_ptr< std::vector< uint8 > > buffer )		override
		{
#ifdef _LOG_DEBUG_
			global_stream_lock.lock();
			std::cout << "[" << __FUNCTION__ << "] " << buffer->size() << " bytes" << std::endl;
			//for( size_t x = 0; x < buffer->size(); ++x )
			//{
			//	std::cout << std::hex << std::setfill( '0' ) <<
			//		std::setw( 2 ) << (int)(*buffer)[ x ] << " ";
			//	if( ( x + 1 ) % 16 == 0 )
			//	{
			//		std::cout << std::endl;
			//	}
			//}
			//std::cout << std::endl;
			global_stream_lock.unlock();
#endif
			// XKoJen -> This will handle fragmentation in the protocol layer.
			if(buffer->size() > 0)
				OnDataReceived(&((*buffer)[0]), buffer->size());

			// Start the next receive
			Recv();

#ifdef _ECHO_
			// Echo the data back
			Send( buffer );
#endif
		}
        virtual void OnTimer( const boost::posix_time::time_duration & delta )			override
		{
#ifdef _LOG_DEBUG_
			//global_stream_lock.lock();
			//std::cout << "[" << __FUNCTION__ << "] " << delta << std::endl;
			//global_stream_lock.unlock();
#endif		
			// Disconnects call the hive (stop). This needs to be done by a thread
			// that called 'run', other wise it sucks it up.
			boost::mutex::scoped_lock lock(m_request_disconnect_mutex);
			if(m_request_disconnect)
				Disconnect();
		}
        virtual void OnError( const boost::system::error_code & error )					override
		{
			// if this code is 'boost::system::errc::success', then its not an error.
			if( ( error.value() == boost::asio::error::connection_aborted) || 
				( error.value() == boost::asio::error::connection_reset)   || 
				( error.value() == boost::asio::error::eof) )
			{
				m_sig_OnConnectionClosed(boost::dynamic_pointer_cast<XKoJen::IConnection>(shared_from_this()));
#ifdef _LOG_DEBUG_
				global_stream_lock.lock();
				std::cout << "Connection [" << __FUNCTION__ << "] Connection closed : " << error << "(" << error.message() << ")" << std::endl;
				global_stream_lock.unlock();
#endif
			}
			else if(error.value() == boost::asio::error::connection_refused)
			{
				// Clients that received this, should continually try to connect until the server becomes present.
				m_sig_OnConnectionRefused();
			}
#ifdef _LOG_DEBUG_
			else if(error.value() != boost::system::errc::success) // success means the operation completed successfully
			{
				global_stream_lock.lock();
				std::cout << "Connection [" << __FUNCTION__ << "] " << error << "(" << error.message() << ")" << std::endl;
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
        CTCPIPConnection( boost::shared_ptr< Hive > hive ): Connection( hive ){}
		virtual ~CTCPIPConnection(){}

		///@{ XKoJen::IConnection overrides
		virtual bool SendData(  const uint8* data_buffer, const uint16& number_of_bytes ) override
		{
#ifdef USING_BOOST
			boost::mutex::scoped_lock lock(m_send_lock); // exception safe
#else
			std::mutex::scoped_lock lock(m_send_lock);
#endif
			// XKoJen Send user defined data
			boost::shared_ptr<std::vector<uint8>> txbuf(new std::vector<uint8>);
			txbuf->resize(number_of_bytes);
			memcpy((void*) &(*txbuf)[0], (void*) data_buffer, number_of_bytes);

			Send(txbuf);

			return true; // how to return status here being asynchronous and all?
		}
		///@}
    };
	
	// TCPIP acceptor ****************************************
    class KOJEN_API CTCPIPAcceptor : public Acceptor
    {
    private:
        // Async handlers...
        virtual bool OnAccept( boost::shared_ptr< Connection > connection, const std::string & host, uint16 port ) override
		{
			/// KoJen : start
			CTCPIPServer_ptr strong = m_parent_server.lock();
			/// KoJen : end
#ifdef _LOG_DEBUG_
			global_stream_lock.lock();
			std::cout << "[" << __FUNCTION__ << "] " << host << ":" << port << std::endl;			
			global_stream_lock.unlock();
#endif
			/// KoJen : start
			// Do the accept from the last worker thread...
			// start a new one for the next connection
			strong->SpawnNewConnectionAcceptor();
			/// KoJen : end
			return true;
		}
        virtual void OnTimer( const boost::posix_time::time_duration & delta )										 override
		{
#ifdef _LOG_DEBUG_
			//global_stream_lock.lock();
			//std::cout << "[" << __FUNCTION__ << "] " << delta << std::endl;
			//global_stream_lock.unlock();
#endif		
		}
        virtual void OnError( const boost::system::error_code & error )												 override
		{
#ifdef _LOG_DEBUG_	
			if(error.value() != boost::system::errc::success) // success means the operation completed successfully
			{
				global_stream_lock.lock();
				std::cout << "Acceptor [" << __FUNCTION__ << "] " << error << "(" << error.message() << ")" << std::endl;
				global_stream_lock.unlock();
			}
#endif		
		}
		/// KoJen : start
		CTCPIPServer_wptr m_parent_server;
		/// KoJen : end
    public:
		CTCPIPAcceptor( boost::shared_ptr< Hive > hive , CTCPIPServer_wptr parent): Acceptor( hive ),m_parent_server(parent){}
        virtual ~CTCPIPAcceptor(){}
    };
	//////////////////////////////////////////////////////////////////
	
	// TCPIP Client ****************************************
	CTCPIPClient_ptr CTCPIPClient::Create()
	{
		CTCPIPClient_ptr client(new CTCPIPClient());
		client->m_hive.reset(new Hive());
		return client;
	}

	CTCPIPClient::~CTCPIPClient()
	{
		Disconnect();
	}
	CTCPIPClient::CTCPIPClient()
	{
	}
	void CTCPIPClient::DoConnect(std::string IP, unsigned int port)
	{
		m_ip = IP;
		m_port = port;

		m_hive->Stop();
		m_hive->Reset();
		if(m_server)
			m_server->Disconnect();	

		m_server.reset(new CTCPIPConnection(m_hive));
		m_server->m_sig_OnConnectionRefused.connect(boost::bind(&CTCPIPClient::DoReconnect, this));
		m_server->m_sig_OnConnectionAccepted.connect(boost::bind(&CTCPIPClient::DoConnectionAccepted, this,_1));
		m_server->Connect(IP,port);
		m_hive->Run();
	}
	void CTCPIPClient::Connect(std::string IP, unsigned int port)
	{		
		m_worker.reset(new boost::thread(boost::bind(&CTCPIPClient::DoConnect, this, IP, port)));		
	}
	void CTCPIPClient::Disconnect()
	{
		if(m_worker)
		{
			m_server->Disconnect();	
			m_hive->Stop();			
			m_worker->interrupt();
			if (m_worker->joinable()) {
				if (m_worker->get_id() != boost::this_thread::get_id()) { // if the calling thread is this thread...don't join...exception will be thrown.
					m_worker->timed_join(boost::posix_time::seconds(1));
				}
			}
			m_worker.reset();			
		}
	}

	void CTCPIPClient::DoReconnect()
	{
		// If this happens, its on the same thread that called 'run'.
		// Hive needs to be stopped/reset from another thread, so that the last thread can be released.
		// This is thus done in 'DoConnect' which is always a new thread.
		Connect(m_ip,m_port);
	}
	void CTCPIPClient::DoConnectionAccepted(IConnection_ptr connection)
	{
		onConnectionReady(connection);
	}
	
	// TCPIP Server ****************************************
	CTCPIPServer_ptr CTCPIPServer::Create(uint16 port)
	{
		CTCPIPServer_ptr server(new CTCPIPServer());
		server->m_hive.reset(new Hive());
		server->m_acceptor.reset(new CTCPIPAcceptor(server->m_hive,server));
		server->m_acceptor->Listen("127.0.0.1", port);
		server->SpawnNewConnectionAcceptor();
		return server;
	}
	CTCPIPServer::~CTCPIPServer()
	{
		m_acceptor->Stop();
		m_hive->Stop();
		m_worker_threads.join_all();
		m_acceptor.reset();
		m_hive.reset();
	}
	CTCPIPServer::CTCPIPServer()
	{
	}
	void CTCPIPServer::SpawnNewConnectionAcceptor()
	{
		m_worker_threads.create_thread( boost::bind( &CTCPIPServer::DoAcceptNewConnection, this ) );
	}
	void CTCPIPServer::DoAcceptNewConnection()
	{
		boost::shared_ptr< CTCPIPConnection > connection( new CTCPIPConnection( m_hive ) );
		m_acceptor->Accept( connection );
		// Let managers/interested parties know
		connection->m_sig_OnConnectionAccepted.connect(boost::bind(&CTCPIPServer::DoConnectionAccepted, this, _1));	
		// give the thread to the hive
		m_hive->Run();
	}
	
	void CTCPIPServer::DoConnectionAccepted(IConnection_ptr connection)
	{
		onNewConnection(connection);
	}
}

#endif // USING_BOOST
#endif // __arm__