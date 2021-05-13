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

#ifdef __arm__
#pragma message "network.h is not supported for ARM."
#else

//-----------------------------------------------------------------------------
#include "basetypes.h"

#ifdef USING_BOOST
#include <boost/asio.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/enable_shared_from_this.hpp>
#include <boost/shared_ptr.hpp>
#include <string>
#include <vector>
#include <list>
//#include <boost/cstdint.hpp>

//-----------------------------------------------------------------------------

namespace Network{
    
    //-----------------------------------------------------------------------------
    
    class Hive;
    class Acceptor;
    class Connection;
    class SerialConnection;

    //-----------------------------------------------------------------------------

    class KOJEN_API SerialConnection : public boost::enable_shared_from_this< SerialConnection >
    {
        friend class Hive;

    private:
        boost::shared_ptr< Hive > m_hive;
        boost::asio::serial_port m_serialport;
        boost::asio::strand m_io_strand;
        boost::asio::deadline_timer m_timer;
        boost::posix_time::ptime m_last_time;
        boost::shared_ptr< std::vector< uint8 > > m_recv_buffer;
        std::list< int32 > m_pending_recvs;
        std::list< boost::shared_ptr< const std::vector< uint8 > > > m_pending_sends;
        int32 m_receive_buffer_size;
        int32 m_timer_interval;
        volatile uint32 m_error_state;

    protected:
        SerialConnection(boost::shared_ptr< Hive > hive);
        virtual ~SerialConnection();

    private:
        SerialConnection(const SerialConnection & rhs);
        SerialConnection & operator =(const SerialConnection & rhs);
        void StartSend();
        void StartRecv(int32 total_bytes);
        void StartTimer();
        void StartError(const boost::system::error_code & error);
        void DispatchSend(boost::shared_ptr< const std::vector< uint8 > > buffer);
        void DispatchRecv(int32 total_bytes);
        void DispatchTimer(const boost::system::error_code & error);
        //void HandleConnect(const boost::system::error_code & error);
        void HandleSend(const boost::system::error_code & error, std::list< boost::shared_ptr< const std::vector< uint8 > > >::iterator itr);
        void HandleRecv(const boost::system::error_code & error, size_t actual_bytes);
        void HandleTimer(const boost::system::error_code & error);

    private:
        // Called when the connection has successfully connected to the local
        // host.
//		virtual void OnAccept(const std::string & host, uint16 port) = 0;

        // Called when the connection has successfully connected to the remote
        // host.
        virtual void OnConnect(const std::string & comport, unsigned int baudrate) = 0;

        // Called when data has been sent by the connection.
        virtual void OnSend(boost::shared_ptr < const std::vector< uint8 > > buffer) = 0;

        // Called when data has been received by the connection.
        virtual void OnRecv(boost::shared_ptr < std::vector< uint8 > > buffer) = 0;

        // Called on each timer event.
        virtual void OnTimer(const boost::posix_time::time_duration & delta) = 0;

        // Called when an error is encountered.
        virtual void OnError(const boost::system::error_code & error) = 0;

    public:
        // Returns the Hive object.
        boost::shared_ptr< Hive > GetHive();

        // Returns the socket object.
        boost::asio::serial_port & GetSerialPort();

        // Returns the strand object.
        boost::asio::strand & GetStrand();

        // Sets the application specific receive buffer size used. For stream
        // based protocols such as HTTP, you want this to be pretty large, like
        // 64kb. For packet based protocols, then it will be much smaller,
        // usually 512b - 8kb depending on the protocol. The default value is
        // 4kb.
        void SetReceiveBufferSize(int32 size);

        // Returns the size of the receive buffer size of the current object.
        int32 GetReceiveBufferSize() const;

        // Sets the timer interval of the object. The interval is changed after
        // the next update is called.
        void SetTimerInterval(int32 timer_interval_ms);

        // Returns the timer interval of the object.
        int32 GetTimerInterval() const;

        // Returns true if this object has an error associated with it.
        bool HasError();

        // Binds the socket to the specified interface.
        void Bind(const char *com_port_name, unsigned int baud_rate = 9600);

        // Starts an a/synchronous connect.
        //void Connect(const std::string & host, uint16 port);

        // Posts data to be sent to the connection.
        void Send(boost::shared_ptr < const std::vector< uint8 > > buffer);

        // Posts a recv for the connection to process. If total_bytes is 0, then
        // as many bytes as possible up to GetReceiveBufferSize() will be
        // waited for. If Recv is not 0, then the connection will wait for exactly
        // total_bytes before invoking OnRecv.
        void Recv(int32 total_bytes = 0);

        // Posts an asynchronous disconnect event for the object to process.
        void Disconnect();
    };
    
    //-----------------------------------------------------------------------------
    
    class KOJEN_API Connection : public boost::enable_shared_from_this< Connection >
    {
        friend class Acceptor;
        friend class Hive;
        
    private:
        boost::shared_ptr< Hive > m_hive;
        boost::asio::ip::tcp::socket m_socket;
        boost::asio::strand m_io_strand;
        boost::asio::deadline_timer m_timer;
        boost::posix_time::ptime m_last_time;
        boost::shared_ptr< std::vector< uint8 > > m_recv_buffer;
        std::list< int32 > m_pending_recvs;
        std::list< boost::shared_ptr< const std::vector< uint8 > > > m_pending_sends;
        int32 m_receive_buffer_size;
        int32 m_timer_interval;
        volatile uint32 m_error_state;
        
    protected:
        Connection( boost::shared_ptr< Hive > hive );
        virtual ~Connection();
        
    private:
        Connection( const Connection & rhs );
        Connection & operator =( const Connection & rhs );
        void StartSend();
        void StartRecv( int32 total_bytes );
        void StartTimer();
        void StartError( const boost::system::error_code & error );
        void DispatchSend( boost::shared_ptr< const std::vector< uint8 > > buffer );
        void DispatchRecv( int32 total_bytes );
        void DispatchTimer( const boost::system::error_code & error );
        void HandleConnect( const boost::system::error_code & error );
        void HandleSend( const boost::system::error_code & error, std::list< boost::shared_ptr< const std::vector< uint8 > > >::iterator itr );
        void HandleRecv( const boost::system::error_code & error, size_t actual_bytes );
        void HandleTimer( const boost::system::error_code & error );
        
    private:
        // Called when the connection has successfully connected to the local
        // host.
        virtual void OnAccept( const std::string & host, uint16 port ) = 0;
        
        // Called when the connection has successfully connected to the remote
        // host.
        virtual void OnConnect( const std::string & host, uint16 port ) = 0;
        
        // Called when data has been sent by the connection.
        virtual void OnSend( boost::shared_ptr < const std::vector< uint8 > > buffer ) = 0;
        
        // Called when data has been received by the connection.
        virtual void OnRecv( boost::shared_ptr < std::vector< uint8 > > buffer ) = 0;
        
        // Called on each timer event.
        virtual void OnTimer( const boost::posix_time::time_duration & delta ) = 0;
        
        // Called when an error is encountered.
        virtual void OnError( const boost::system::error_code & error ) = 0;
        
    public:
        // Returns the Hive object.
        boost::shared_ptr< Hive > GetHive();
        
        // Returns the socket object.
        boost::asio::ip::tcp::socket & GetSocket();
        
        // Returns the strand object.
        boost::asio::strand & GetStrand();
        
        // Sets the application specific receive buffer size used. For stream
        // based protocols such as HTTP, you want this to be pretty large, like
        // 64kb. For packet based protocols, then it will be much smaller,
        // usually 512b - 8kb depending on the protocol. The default value is
        // 4kb.
        void SetReceiveBufferSize( int32 size );
        
        // Returns the size of the receive buffer size of the current object.
        int32 GetReceiveBufferSize() const;
        
        // Sets the timer interval of the object. The interval is changed after
        // the next update is called.
        void SetTimerInterval( int32 timer_interval_ms );
        
        // Returns the timer interval of the object.
        int32 GetTimerInterval() const;
        
        // Returns true if this object has an error associated with it.
        bool HasError();
        
        // Binds the socket to the specified interface.
        void Bind( const std::string & ip, uint16 port );
        
        // Starts an a/synchronous connect.
        void Connect( const std::string & host, uint16 port );
        
        // Posts data to be sent to the connection.
        void Send( boost::shared_ptr < const std::vector< uint8 > > buffer );
        
        // Posts a recv for the connection to process. If total_bytes is 0, then
        // as many bytes as possible up to GetReceiveBufferSize() will be
        // waited for. If Recv is not 0, then the connection will wait for exactly
        // total_bytes before invoking OnRecv.
        void Recv( int32 total_bytes = 0 );
        
        // Posts an asynchronous disconnect event for the object to process.
        void Disconnect();
    };
    
    //-----------------------------------------------------------------------------
    
    class KOJEN_API Acceptor : public boost::enable_shared_from_this< Acceptor >
    {
        friend class Hive;
        
    private:
        boost::shared_ptr< Hive > m_hive;
        boost::asio::ip::tcp::acceptor m_acceptor;
        boost::asio::strand m_io_strand;
        boost::asio::deadline_timer m_timer;
        boost::posix_time::ptime m_last_time;
        int32 m_timer_interval;
        volatile uint32 m_error_state;
        
    private:
        Acceptor( const Acceptor & rhs );
        Acceptor & operator =( const Acceptor & rhs );
        void StartTimer();
        void StartError( const boost::system::error_code & error );
        void DispatchAccept( boost::shared_ptr< Connection > connection );
        void HandleTimer( const boost::system::error_code & error );
        void HandleAccept( const boost::system::error_code & error, boost::shared_ptr< Connection > connection );
        
    protected:
        Acceptor( boost::shared_ptr< Hive > hive );
        virtual ~Acceptor();
        
    private:
        // Called when a connection has connected to the server. This function
        // should return true to invoke the connection's OnAccept function if the
        // connection will be kept. If the connection will not be kept, the
        // connection's Disconnect function should be called and the function
        // should return false.
        virtual bool OnAccept( boost::shared_ptr< Connection > connection, const std::string & host, uint16 port ) = 0;
        
        // Called on each timer event.
        virtual void OnTimer( const boost::posix_time::time_duration & delta ) = 0;
        
        // Called when an error is encountered. Most typically, this is when the
        // acceptor is being closed via the Stop function or if the Listen is
        // called on an address that is not available.
        virtual void OnError( const boost::system::error_code & error ) = 0;
        
    public:
        // Returns the Hive object.
        boost::shared_ptr< Hive > GetHive();
        
        // Returns the acceptor object.
        boost::asio::ip::tcp::acceptor & GetAcceptor();
        
        // Returns the strand object.
        boost::asio::strand & GetStrand();
        
        // Sets the timer interval of the object. The interval is changed after
        // the next update is called. The default value is 1000 ms.
        void SetTimerInterval( int32 timer_interval_ms );
        
        // Returns the timer interval of the object.
        int32 GetTimerInterval() const;
        
        // Returns true if this object has an error associated with it.
        bool HasError();
        
    public:
        // Begin listening on the specific network interface.
        void Listen( const std::string & host, const uint16 & port );
        
        // Posts the connection to the listening interface. The next client that
        // connections will be given this connection. If multiple calls to Accept
        // are called at a time, then they are accepted in a FIFO order.
        void Accept( boost::shared_ptr< Connection > connection );
        
        // Stop the Acceptor from listening.
        void Stop();
    };
    
    //-----------------------------------------------------------------------------
    
    class KOJEN_API Hive : public boost::enable_shared_from_this< Hive >
    {
    private:
        boost::asio::io_service m_io_service;
        boost::shared_ptr< boost::asio::io_service::work > m_work_ptr;
        volatile uint32 m_shutdown;
        
    private:
        Hive( const Hive & rhs );
        Hive & operator =( const Hive & rhs );
        
    public:
        Hive();
        virtual ~Hive();
        
        // Returns the io_service of this object.
        boost::asio::io_service & GetService();
        
        // Returns true if the Stop function has been called.
        bool HasStopped();
        
        // Polls the networking subsystem once from the current thread and 
        // returns.
        void Poll();
        
        // Runs the networking system on the current thread. This function blocks 
        // until the networking system is stopped, so do not call on a single 
        // threaded application with no other means of being able to call Stop 
        // unless you code in such logic.
        void Run();
        
        // Stops the networking system. All work is finished and no more 
        // networking interactions will be possible afterwards until Reset is called.
        void Stop();
        
        // Restarts the networking system after Stop as been called. A new work
        // object is created ad the shutdown flag is cleared.
        void Reset();
    };
    
    //-----------------------------------------------------------------------------
    
}
#else
#pragma WARNING("network requires the usage of BOOST libraries,and the preprocessor definition 'USE_BOOST'")
#endif // USING_BOOST
#endif // __arm__
