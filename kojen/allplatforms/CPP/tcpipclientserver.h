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
#pragma message "tcpipclientserver.h is not supported for ARM."
#else

#ifdef USING_BOOST
//http://www.gamedev.net/blog/950/entry-2249317-a-guide-to-getting-started-with-boostasio/?pg=1

//#define _ECHO_
//#define _LOG_DEBUG_

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

	
	CGEN_DECL_CLASS_PTR(CTCPIPConnection);
	CGEN_DECL_CLASS_PTR(CTCPIPAcceptor);
    CGEN_DECL_CLASS_PTR(IConnection);
	CGEN_DECL_CLASS_PTR(IMsgReceiver);
	CGEN_DECL_CLASS_PTR(IRawDataReceiver);
	
	// TCPIP Client ****************************************
	CGEN_DECL_CLASS_PTR(CTCPIPClient);
	class KOJEN_API CTCPIPClient
	{
	public:
		static CTCPIPClient_ptr Create();
		virtual ~CTCPIPClient();

		/** KoJen : Starts the connection, and starts the service listening.
		*/
		void Connect(std::string IP, unsigned int port);
		/** KoJen : Disconnects the client
		*/
		void Disconnect();
		/** KoJen : Returns the connection used to TX/RX data when ready.
		*/
		boost::signals2::signal< void (IConnection_ptr) > onConnectionReady;
	protected:
		CTCPIPClient();
		/** KoJen : worker will do the connect, and run the hive.
		*/
		void DoConnect(std::string IP, unsigned int port);
		/** KoJen : thread that does the work.
		*/
		boost::thread_ptr m_worker;
		/** KoJen : handle a server who is not yet present.
		*/
		void DoReconnect();
		/** KoJen : when a connection is accepted, it will call this.
		    We can then notify interested parties.
		*/
		void DoConnectionAccepted(IConnection_ptr connection);
	private:
		CTCPIPConnection_ptr m_server;
		Hive_ptr m_hive;
		/** KoJen : Keep desired parameters for reconnect.
		*/
		std::string m_ip;
		unsigned int m_port;
	};

	// TCPIP Server ****************************************
	CGEN_DECL_CLASS_PTR(CTCPIPServer);
	class KOJEN_API CTCPIPServer
	{
	public:
		static CTCPIPServer_ptr Create(uint16 port);
		virtual ~CTCPIPServer();
		/** This signal will let us know when a new server connection has been accepted.
			It will have a client on the other end.
		*/
		boost::signals2::signal<void (IConnection_ptr)> onNewConnection;
	protected:
		CTCPIPServer();
		/** KoJen : For each new connection made to the server,
		and on start, we create a new thread to run this function.
		It will call 'hive->run' which in turn calls asio::io_service::run, thus adding
		threads to the service. It thus scales.
		*/
		void SpawnNewConnectionAcceptor();
		void DoAcceptNewConnection();
		/** KoJen : when a connection is accepted, it will call this.
		    We can then notify interested parties.
		*/
		void DoConnectionAccepted(IConnection_ptr connection);
	private:
		friend class CTCPIPAcceptor;
		CTCPIPAcceptor_ptr m_acceptor;
		Hive_ptr m_hive;
		/** KoJen : Each accepted connection gets its own thread. Scalable.
		*/
		boost::thread_group m_worker_threads;
	};
}
#else
#pragma WARNING("tcpipclientserver requires the usage of BOOST libraries,and the preprocessor definition 'USE_BOOST'")
#endif // USING_BOOST
#endif // __arm__