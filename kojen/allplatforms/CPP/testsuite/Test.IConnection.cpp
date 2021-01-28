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

#include "minunit/minunit.h"

#ifdef __arm__

#else

#pragma warning( disable : 4244 )
#pragma warning( disable : 4127 )

#endif // __arm__

#include "../IConnection.h"
#include "../MsgHeader.h"
#include <string.h>

	#define TEST_PREAMBLE 0xDEAD

	/************************************************************************/
	/* Test Interface...usually autogenerated                               */
	/************************************************************************/
	struct sCustomStruct
	{
		uint16 reusable1                                 __attribute__ ((packed));
		uint16 reusable2                                 __attribute__ ((packed));
		uint32 reusable3                                 __attribute__ ((packed));
	};
	
	struct sSomeCmd
	{
		sMsgHeader Header;
		uint8 plEnableBla                                __attribute__ ((packed));
	};
	
	struct sSomeCmdRsp
	{
		sMsgHeader Header;
		sCustomStruct CommonData;
		uint8 plStatus                                   __attribute__ ((packed));
	};
	struct sSomeReq
	{
		sMsgHeader Header;
		uint8 PLEASE                                __attribute__ ((packed));
	};
	
	struct sSomeReqRsp
	{
		sMsgHeader Header;
		sCustomStruct CommonData1;
		sCustomStruct CommonData2;
		uint32 plHere1                                   __attribute__ ((packed));
		uint32 plHere2                                   __attribute__ ((packed));
		uint32 plHere3                                   __attribute__ ((packed));
	};

	struct sHeaderOnlyCmd
	{
		sMsgHeader Header;
	};

	void IsEqual(const sCustomStruct& customstruct,const sCustomStruct& customstruct2)
	{
		mu_assert(customstruct.reusable1 == customstruct2.reusable1, "sCustomStruct.reusable1 is not equal");
		mu_assert(customstruct.reusable1 == customstruct2.reusable1, "sCustomStruct.reusable2 is not equal");
		mu_assert(customstruct.reusable1 == customstruct2.reusable1, "sCustomStruct.reusable3 is not equal");
	}
	void IsEqual(const sMsgHeader& header,const sMsgHeader& header2)
	{
		mu_assert(header.Preamble			== header2.Preamble			, "sMsgHeader.Preamble is not equal");
		mu_assert(header.PayloadSize		== header2.PayloadSize		, "sMsgHeader.PayloadSize is not equal");
		mu_assert(header.TypeID				== header2.TypeID			, "sMsgHeader.TypeID is not equal");
	}
	void IsEqual(const sSomeCmd& cmd,const sSomeCmd& cmd2)
	{
		IsEqual(cmd.Header, cmd2.Header);
		mu_assert(cmd.plEnableBla == cmd2.plEnableBla, "sSomeCmd.plEnableBla is not equal");
	}
	void IsEqual(const sSomeCmdRsp& rsp,const sSomeCmdRsp& rsp2)
	{
		IsEqual(rsp.Header, rsp2.Header);
		IsEqual(rsp.CommonData, rsp2.CommonData);
		mu_assert(rsp.plStatus == rsp2.plStatus, "sSomeCmdRsp.plStatus is not equal");
	}
	void IsEqual(const sSomeReq& rsp,const sSomeReq& rsp2)
	{
		IsEqual(rsp.Header, rsp2.Header);
		mu_assert(rsp.PLEASE == rsp2.PLEASE, "sSomeReq.PLEASE is not equal");
	}
	void IsEqual(const sSomeReqRsp& rsp,const sSomeReqRsp& rsp2)
	{
		IsEqual(rsp.Header, rsp2.Header);
		IsEqual(rsp.CommonData1, rsp2.CommonData1);
		IsEqual(rsp.CommonData2, rsp2.CommonData2);
		mu_assert(rsp.plHere1 == rsp2.plHere1, "sSomeReqRsp.plHere1 is not equal");
		mu_assert(rsp.plHere2 == rsp2.plHere2, "sSomeReqRsp.plHere2 is not equal");
		mu_assert(rsp.plHere3 == rsp2.plHere3, "sSomeReqRsp.plHere3 is not equal");
	}
	void IsEqual(const sHeaderOnlyCmd& rsp, const sHeaderOnlyCmd& rsp2)
	{
		IsEqual(rsp.Header, rsp2.Header);
	}

	/************************************************************************/
	/*  Test classes                                                        */
	/************************************************************************/

	/** Message Receiver
	*/
	class CTestMsgReceiver : public XKoJen::IMsgReceiver
	{
	public:
		bool m_unknown_message_received;
		CTestMsgReceiver():m_unknown_message_received(false){};
		virtual uint16 Preamble() const override
		{
			return TEST_PREAMBLE;
		}
		virtual void OnMessageReceived( const uint8* data_buffer, const uint32& number_of_bytes ) override
		{
			sMsgHeader* header = (sMsgHeader*)(&(data_buffer)[0]);
			int16 TypeID = header->TypeID;

			if(TypeID == 6)
			{
				if(number_of_bytes != sizeof(sSomeCmd))
					printf("\r\nMsg sSomeCmd wrong size returned.\r\n");
				memcpy((void*)&m_rxsomecmd, (void*)data_buffer, number_of_bytes);
				return;
			}
			if(TypeID == 7)
			{
				if(number_of_bytes != sizeof(sSomeCmdRsp))
					printf("\r\nMsg sSomeCmdRsp wrong size returned.\r\n");
				memcpy((void*)&m_rxsomecmdrsp, (void*)data_buffer, number_of_bytes);
				return;
			}
			if(TypeID == 8)
			{
				if(number_of_bytes != sizeof(sSomeReq))
					printf("\r\nMsg sSomeReq wrong size returned.\r\n");
				memcpy((void*)&m_rxsomereq, (void*)data_buffer, number_of_bytes);
				return;
			}
			if(TypeID == 9)
			{
				if(number_of_bytes != sizeof(sSomeReqRsp))
					printf("\r\nMsg sSomeReqRsp wrong size returned.\r\n");
				memcpy((void*)&m_rxsomereqrsp, (void*)data_buffer, number_of_bytes);
				return;
			}
			if (TypeID == 12)
			{
				if (number_of_bytes != sizeof(sHeaderOnlyCmd))
					printf("\r\nMsg sHeaderOnlyCmd wrong size returned.\r\n");
				memcpy((void*)&m_rxheaderonlycmd, (void*)data_buffer, number_of_bytes);
				return;
			}
			else {
				printf("\r\nUnknown message TypeID (%i) size (%i bytes) received.\r\n", TypeID, number_of_bytes);
				m_unknown_message_received = true;
			}
		}
#ifdef __arm__
		virtual uint16 LargestMessageSize() override
		{
			return sizeof(sSomeReqRsp);
		}
#endif
		// Received
		sSomeCmd		m_rxsomecmd;
		sSomeCmdRsp		m_rxsomecmdrsp;
		sSomeReq		m_rxsomereq;
		sSomeReqRsp		m_rxsomereqrsp;
		sHeaderOnlyCmd	m_rxheaderonlycmd;
	};

	/** Raw Data Receiver
	*/
	class CTestRawDataReceiver : public XKoJen::IRawDataReceiver
	{
	public:
		CTestRawDataReceiver() : m_rxbuffer{ nullptr }, m_rxcnt{ 0 }{};
		void SetRxBuf(uint8*& rxbuffer) { m_rxbuffer = rxbuffer; };
		virtual void OnDataReceived(const uint8* data_buffer, const uint32& number_of_bytes) override
		{
			if (nullptr != m_rxbuffer) 
			{
				m_rxcnt = number_of_bytes;
				memcpy(m_rxbuffer, data_buffer, number_of_bytes);
			}
		}
		uint16 NumberOfBytedRx() { return m_rxcnt; }
	private:
		uint8* m_rxbuffer;
		uint16 m_rxcnt;
	};

	/** Connection
	*/
	class CTestConnection : public XKoJen::IConnection
	{
	public:
		CTestConnection(){};
		~CTestConnection(){};

		virtual bool SendData(const uint8* data_buffer, const uint16& number_of_bytes) override {
			// Loopback
			OnDataReceived(data_buffer, number_of_bytes);
			return true;
		}
		
	private:
		CTestConnection( const CTestConnection &c );
		CTestConnection& operator=( const CTestConnection &c );
	};

/// This testgroup should cover the following test scenarios:
///
/// 1) data received in very small fragments (i.e. less than sMsgHeader in size).
/// 2) data received in larger fragments (i.e. greater than sMsgHeader in size, but less than full message).
/// 3) data received in full (i.e. a full command message).
/// 4) data received concatenated.
/// 5) data received concatenated and fragmented.
/// - several messages received with fragmented messages at the end.
/// - followed by more fragmented messages...
/// 6) unknown data received, that is very large (potentially larger then fragment buffer on arm).
/// - same preamble / message marker -> message is processed, but should be ignored
/// - typically happens only on a PC (i.e. TCPIP) where the socket layer does its own buffering
/// - scenario : somebody transmits BullS__.
/// - different preamble / message marker -> message should not be processed at all
/// 7) messages with zero payload (header only messages)
/// 8) random bytes that are not protocol based before and after real data -> sync to stream

#ifdef __arm__
	// This is defined in arm. In non-arm, vectors are used.
#else
	#define FRAGMENT_BUF_SIZE 1024
#endif

	namespace {
		struct MsgByteStreamHandlingGroup
		{
			CTestMsgReceiver m_rx;
			CTestConnection m_tx;

			uint8 buffer[FRAGMENT_BUF_SIZE];

			// TX Data...
			sSomeCmd		m_somecmd;
			sSomeCmdRsp		m_somecmdrsp;
			sSomeReq		m_somereq;
			sSomeReqRsp		m_somereqrsp;
			sHeaderOnlyCmd	m_headeronlycmd;

			MsgByteStreamHandlingGroup()
			{
				m_tx.SetMsgReceiver(&m_rx);
				// Seeing as this unit test IF is not autogenerated, this needs to be set manually.
				uint16 preamble = m_rx.Preamble();
				// Setup defaults...
				m_somecmd.Header.Preamble = preamble;
				m_somecmd.Header.PayloadSize = sizeof(sSomeCmd) - sizeof(sMsgHeader);
				m_somecmd.Header.TypeID = 6;
				m_somecmd.plEnableBla = 111;

				m_somecmdrsp.Header.Preamble = preamble;
				m_somecmdrsp.Header.PayloadSize = sizeof(sSomeCmdRsp) - sizeof(sMsgHeader);
				m_somecmdrsp.Header.TypeID = 7;
				m_somecmdrsp.CommonData.reusable1 = 3;
				m_somecmdrsp.CommonData.reusable2 = 2;
				m_somecmdrsp.CommonData.reusable3 = 1;
				m_somecmdrsp.plStatus = 123;

				// Setup defaults...
				m_somereq.Header.Preamble = preamble;
				m_somereq.Header.PayloadSize = sizeof(sSomeReq) - sizeof(sMsgHeader);
				m_somereq.Header.TypeID = 8;
				m_somereq.PLEASE = 222;

				m_somereqrsp.Header.Preamble = preamble;
				m_somereqrsp.Header.PayloadSize = sizeof(sSomeReqRsp) - sizeof(sMsgHeader);
				m_somereqrsp.Header.TypeID = 9;
				m_somereqrsp.CommonData1.reusable1 = 333;
				m_somereqrsp.CommonData1.reusable2 = 222;
				m_somereqrsp.CommonData1.reusable3 = 111;
				m_somereqrsp.CommonData2.reusable1 = 3333;
				m_somereqrsp.CommonData2.reusable2 = 2222;
				m_somereqrsp.CommonData2.reusable3 = 1111;
				m_somereqrsp.plHere1 = 123456;
				m_somereqrsp.plHere2 = 123456;
				m_somereqrsp.plHere3 = 123456;

				m_headeronlycmd.Header.Preamble = preamble;
				m_headeronlycmd.Header.TypeID = 12;
				m_headeronlycmd.Header.PayloadSize = sizeof(sHeaderOnlyCmd) - sizeof(sMsgHeader);

				clear_rx();
			}
			void clear_rx()
			{
				memset((void*)&m_rx.m_rxsomecmd, 0, sizeof(sSomeCmd));
				memset((void*)&m_rx.m_rxsomecmdrsp, 0, sizeof(sSomeCmdRsp));
				memset((void*)&m_rx.m_rxsomereq, 0, sizeof(sSomeReq));
				memset((void*)&m_rx.m_rxsomereqrsp, 0, sizeof(sSomeReqRsp));
				memset((void*)&m_rx.m_rxheaderonlycmd, 0, sizeof(sHeaderOnlyCmd));
			}
		};
	}

MU_TEST(Scenario1_ByteForByteIndividualPackets)
{
	MsgByteStreamHandlingGroup fixture;
	mu_assert(fixture.m_tx.HasMsgReceiver(),	  "Does not have a message receiver, but should have.");
	mu_assert(!fixture.m_tx.HasRawDataReceiver(), "Has a raw data receiver, but should not have.");


	// Scenario 1...Byte For byte...per message...
	memcpy((void*)fixture.buffer, &fixture.m_somecmd, sizeof(sSomeCmd));
	uint16 total = sizeof(sSomeCmd);
	for(uint16 cnt = 0; cnt < total;cnt=cnt+1)
	{
		fixture.m_tx.SendData(&fixture.buffer[cnt],1);
	}
	IsEqual(fixture.m_somecmd, fixture.m_rx.m_rxsomecmd);
	
	memcpy((void*)fixture.buffer, &fixture.m_somecmdrsp, sizeof(sSomeCmdRsp));
	for(uint16 cnt = 0; cnt < sizeof(sSomeCmdRsp);++cnt)
	{
		fixture.m_tx.SendData(&fixture.buffer[cnt],1);
	}
	IsEqual(fixture.m_somecmdrsp, fixture.m_rx.m_rxsomecmdrsp);

	memcpy((void*)fixture.buffer, &fixture.m_somereq, sizeof(sSomeReq));
	for(uint16 cnt = 0; cnt < sizeof(sSomeReq);++cnt)
	{
		fixture.m_tx.SendData(&fixture.buffer[cnt],1);
	}
	IsEqual(fixture.m_somereq, fixture.m_rx.m_rxsomereq);

	memcpy((void*)fixture.buffer, &fixture.m_somereqrsp, sizeof(sSomeReqRsp));
	for(uint16 cnt = 0; cnt < sizeof(sSomeReqRsp);++cnt)
	{
		fixture.m_tx.SendData(&fixture.buffer[cnt],1);
	}
	IsEqual(fixture.m_somereqrsp, fixture.m_rx.m_rxsomereqrsp);

	mu_assert(!fixture.m_rx.m_unknown_message_received, "Unknown message received");
}

MU_TEST(Scenario2_SmallFragments)
{
	MsgByteStreamHandlingGroup fixture;

	mu_assert(fixture.m_tx.HasMsgReceiver(), "Does not have a message receiver, but should have.");
	mu_assert(!fixture.m_tx.HasRawDataReceiver(), "Has a raw data receiver, but should not have.");

	/// Scenario 2...greater than header, but less than message...
	{
		memcpy((void*)fixture.buffer, &fixture.m_somecmdrsp, sizeof(sSomeCmdRsp));
		uint16 size_1 = sizeof(sMsgHeader) + (sizeof(sSomeCmdRsp) - sizeof(sMsgHeader))*0.5;
		uint16 size_2 = sizeof(sSomeCmdRsp) - size_1;
		fixture.m_tx.SendData(&fixture.buffer[0],size_1);
		fixture.m_tx.SendData(&fixture.buffer[size_1],size_2);
		IsEqual(fixture.m_somecmdrsp, fixture.m_rx.m_rxsomecmdrsp);
	}
	{
		memcpy((void*)fixture.buffer, &fixture.m_somereqrsp, sizeof(sSomeReqRsp));
		uint16 size_1 = sizeof(sMsgHeader) + (sizeof(sSomeReqRsp) - sizeof(sMsgHeader))*0.5;
		uint16 size_2 = sizeof(sSomeReqRsp) - size_1;
		fixture.m_tx.SendData(&fixture.buffer[0],size_1);
		fixture.m_tx.SendData(&fixture.buffer[size_1],size_2);
		IsEqual(fixture.m_somereqrsp, fixture.m_rx.m_rxsomereqrsp);
	}

	mu_assert(!fixture.m_rx.m_unknown_message_received, "Unknown message received");
}

MU_TEST(Scenario3_FullPackets)
{
	MsgByteStreamHandlingGroup fixture;

	mu_assert(fixture.m_tx.HasMsgReceiver(), "Does not have a message receiver, but should have.");
	mu_assert(!fixture.m_tx.HasRawDataReceiver(), "Has a raw data receiver, but should not have.");

	/// Scenario 3...full...
	memcpy((void*)fixture.buffer, &fixture.m_somecmd, sizeof(sSomeCmd));
	fixture.m_tx.SendData(&fixture.buffer[0],sizeof(sSomeCmd));
	IsEqual(fixture.m_somecmd, fixture.m_rx.m_rxsomecmd);
	
	memcpy((void*)fixture.buffer, &fixture.m_somecmdrsp, sizeof(sSomeCmdRsp));
	fixture.m_tx.SendData(&fixture.buffer[0],sizeof(sSomeCmdRsp));
	IsEqual(fixture.m_somecmdrsp, fixture.m_rx.m_rxsomecmdrsp);

	memcpy((void*)fixture.buffer, &fixture.m_somereq, sizeof(sSomeReq));
	fixture.m_tx.SendData(&fixture.buffer[0],sizeof(sSomeReq));
	IsEqual(fixture.m_somereq, fixture.m_rx.m_rxsomereq);
	
	memcpy((void*)fixture.buffer, &fixture.m_somereqrsp, sizeof(sSomeReqRsp));
	fixture.m_tx.SendData(&fixture.buffer[0],sizeof(sSomeReqRsp));
	IsEqual(fixture.m_somereqrsp, fixture.m_rx.m_rxsomereqrsp);

	mu_assert(!fixture.m_rx.m_unknown_message_received, "Unknown message received");
}

MU_TEST(Scenario4_1_FullPacketsConcatenated)
{
	MsgByteStreamHandlingGroup fixture;

	mu_assert(fixture.m_tx.HasMsgReceiver(), "Does not have a message receiver, but should have.");
	mu_assert(!fixture.m_tx.HasRawDataReceiver(), "Has a raw data receiver, but should not have.");

	/// Scanerio 4...data received concatenated...
	memcpy((void*)fixture.buffer, &fixture.m_somecmd, sizeof(sSomeCmd));
	memcpy((void*) &fixture.buffer[sizeof(sSomeCmd)], &fixture.m_somecmdrsp, sizeof(sSomeCmdRsp));
	memcpy((void*) &fixture.buffer[sizeof(sSomeCmd)+sizeof(sSomeCmdRsp)], &fixture.m_somereq, sizeof(sSomeReq));
	memcpy((void*) &fixture.buffer[sizeof(sSomeCmd)+sizeof(sSomeCmdRsp)+sizeof(sSomeReq)], &fixture.m_somereqrsp, sizeof(sSomeReqRsp));
	fixture.m_tx.SendData(&fixture.buffer[0],sizeof(sSomeCmd) + sizeof(sSomeCmdRsp) + sizeof(sSomeReq) + sizeof(sSomeReqRsp));
	IsEqual(fixture.m_somecmd, fixture.m_rx.m_rxsomecmd);
	IsEqual(fixture.m_somecmdrsp, fixture.m_rx.m_rxsomecmdrsp);
	IsEqual(fixture.m_somereq, fixture.m_rx.m_rxsomereq);
	IsEqual(fixture.m_somereqrsp, fixture.m_rx.m_rxsomereqrsp);

	mu_assert(!fixture.m_rx.m_unknown_message_received, "Unknown message received");
}

MU_TEST(Scenario4_2_FullPacketsConcatenated_ByteForByte)
{
	MsgByteStreamHandlingGroup fixture;

	mu_assert(fixture.m_tx.HasMsgReceiver(), "Does not have a message receiver, but should have.");
	mu_assert(!fixture.m_tx.HasRawDataReceiver(), "Has a raw data receiver, but should not have.");

	/// Scanerio 4...data received concatenated...but byte for byte
	memcpy((void*)fixture.buffer, &fixture.m_somecmd, sizeof(sSomeCmd));
	memcpy((void*) &fixture.buffer[sizeof(sSomeCmd)], &fixture.m_somecmdrsp, sizeof(sSomeCmdRsp));
	memcpy((void*) &fixture.buffer[sizeof(sSomeCmd)+sizeof(sSomeCmdRsp)], &fixture.m_somereq, sizeof(sSomeReq));
	memcpy((void*) &fixture.buffer[sizeof(sSomeCmd)+sizeof(sSomeCmdRsp)+sizeof(sSomeReq)], &fixture.m_somereqrsp, sizeof(sSomeReqRsp));
	for(uint16 cnt = 0; cnt < sizeof(sSomeCmd) + sizeof(sSomeCmdRsp)+sizeof(sSomeReq) + sizeof(sSomeReqRsp);++cnt)
	{
		fixture.m_tx.SendData(&fixture.buffer[cnt],1);
	}
	IsEqual(fixture.m_somecmd, fixture.m_rx.m_rxsomecmd);
	IsEqual(fixture.m_somecmdrsp, fixture.m_rx.m_rxsomecmdrsp);
	IsEqual(fixture.m_somereq, fixture.m_rx.m_rxsomereq);
	IsEqual(fixture.m_somereqrsp, fixture.m_rx.m_rxsomereqrsp);

	mu_assert(!fixture.m_rx.m_unknown_message_received, "Unknown message received");
}

MU_TEST(Scenario_5_FragmentedAndMoreFragmented)
{
	MsgByteStreamHandlingGroup fixture;

	mu_assert(fixture.m_tx.HasMsgReceiver(), "Does not have a message receiver, but should have.");
	mu_assert(!fixture.m_tx.HasRawDataReceiver(), "Has a raw data receiver, but should not have.");


	/// 5) data received concatenated and fragmented.
	/// - several messages received with fragmented messages at the end.
	/// - followed by more fragmented messages...
	/// --> this is a good test!
	memcpy((void*)fixture.buffer, &fixture.m_somecmd, sizeof(sSomeCmd));
	memcpy((void*) &fixture.buffer[sizeof(sSomeCmd)], &fixture.m_somecmdrsp, sizeof(sSomeCmdRsp));
	memcpy((void*) &fixture.buffer[sizeof(sSomeCmd)+sizeof(sSomeCmdRsp)], &fixture.m_somereq, sizeof(sSomeReq));
	memcpy((void*) &fixture.buffer[sizeof(sSomeCmd)+sizeof(sSomeCmdRsp)+sizeof(sSomeReq)], &fixture.m_somereqrsp, sizeof(sSomeReqRsp));

	size_t total_size = sizeof(sSomeCmd) + sizeof(sSomeCmdRsp) + sizeof(sSomeReq) + sizeof(sSomeReqRsp);
	size_t size_1 = sizeof(sSomeCmd) + sizeof(sSomeCmdRsp) + sizeof(sSomeReq)*0.3;
	size_t size_2 = (total_size - size_1) * 0.7;
	size_t size_3 = total_size - size_1 - size_2;

	mu_check(total_size == size_1 + size_2 + size_3);

	size_t cnt = 0;

	// Vary byte-for-byte betwe the 3 transmissions...

	// 1
	fixture.m_tx.SendData(&fixture.buffer[cnt], size_1);
	cnt+=size_1;
	fixture.m_tx.SendData(&fixture.buffer[cnt], size_2);
	cnt+=size_2;
	for(uint16 i = 0; i < size_3 ;++i)
	{
		fixture.m_tx.SendData(&fixture.buffer[cnt],1);
		++cnt;
	}
	IsEqual(fixture.m_somecmd, fixture.m_rx.m_rxsomecmd);
	IsEqual(fixture.m_somecmdrsp, fixture.m_rx.m_rxsomecmdrsp);
	IsEqual(fixture.m_somereq, fixture.m_rx.m_rxsomereq);
	IsEqual(fixture.m_somereqrsp, fixture.m_rx.m_rxsomereqrsp);
	fixture.clear_rx();
	cnt = 0;
	// 2
	fixture.m_tx.SendData(&fixture.buffer[cnt], size_1);
	cnt+=size_1;
	for(uint16 i = 0; i < size_2 ;++i)
	{
		fixture.m_tx.SendData(&fixture.buffer[cnt],1);
		++cnt;
	}
	fixture.m_tx.SendData(&fixture.buffer[cnt], size_3);
	cnt+=size_3;
	IsEqual(fixture.m_somecmd, fixture.m_rx.m_rxsomecmd);
	IsEqual(fixture.m_somecmdrsp, fixture.m_rx.m_rxsomecmdrsp);
	IsEqual(fixture.m_somereq, fixture.m_rx.m_rxsomereq);
	IsEqual(fixture.m_somereqrsp, fixture.m_rx.m_rxsomereqrsp);
	fixture.clear_rx();
	cnt = 0;
	// 3
	for(uint16 i = 0; i < size_1 ;++i)
	{
		fixture.m_tx.SendData(&fixture.buffer[cnt],1);
		++cnt;
	}
	fixture.m_tx.SendData(&fixture.buffer[cnt], size_2);
	cnt+=size_2;
	fixture.m_tx.SendData(&fixture.buffer[cnt], size_3);
	cnt+=size_3;
	IsEqual(fixture.m_somecmd, fixture.m_rx.m_rxsomecmd);
	IsEqual(fixture.m_somecmdrsp, fixture.m_rx.m_rxsomecmdrsp);
	IsEqual(fixture.m_somereq, fixture.m_rx.m_rxsomereq);
	IsEqual(fixture.m_somereqrsp, fixture.m_rx.m_rxsomereqrsp);
	fixture.clear_rx();
	cnt = 0;

	mu_assert(!fixture.m_rx.m_unknown_message_received, "Unknown message received");
}

//////////////////////////////////////////////////////////////////////////

namespace {
	struct sUnknownToCommunicationLayer
	{
		sMsgHeader Header;
		sCustomStruct CommonData;
		uint8 plStatus[2 * FRAGMENT_BUF_SIZE]   __attribute__((packed));
	};
}
#define INIT_DATA_UNKNOWN_DIFFERENT_PREAMBLE \
	data_unknown.Header.Preamble = 0x66;\
	data_unknown.Header.PayloadSize = sizeof(sUnknownToCommunicationLayer) - sizeof(sMsgHeader);\
	data_unknown.Header.TypeID = 66;\
	memset((void*)&data_unknown.plStatus,23,2*FRAGMENT_BUF_SIZE*sizeof(uint8));
	
#define INIT_DATA_UNKNOWN_SAME_PREAMBLE \
	data_unknown.Header.Preamble = TEST_PREAMBLE;\
	data_unknown.Header.PayloadSize = sizeof(sUnknownToCommunicationLayer) - sizeof(sMsgHeader);\
	data_unknown.Header.TypeID = 66;\
	memset((void*)&data_unknown.plStatus,23,2*FRAGMENT_BUF_SIZE*sizeof(uint8));

MU_TEST(Scenario_6_1_UnknownDataBiggerThanFragmentBuf_SAME_PREAMBLE_ByteForByte)
{
	MsgByteStreamHandlingGroup fixture;

	mu_assert(fixture.m_tx.HasMsgReceiver(), "Does not have a message receiver, but should have.");
	mu_assert(!fixture.m_tx.HasRawDataReceiver(), "Has a raw data receiver, but should not have.");

	sUnknownToCommunicationLayer data_unknown;
	INIT_DATA_UNKNOWN_SAME_PREAMBLE;
	uint8* start_data = (uint8*)&data_unknown;
	// Shouldnt crash, should simply get a printout...
	for(size_t i = 0; i < sizeof(sUnknownToCommunicationLayer); ++i){
		fixture.m_tx.SendData(&start_data[i],1);
	}
	// Other messages should still work
#ifdef __arm__
	mu_check(!fixture.m_tx.HasDataExceedingFragmentBufferSize()); // Would have already been cleared.
#endif

	/// Scanerio 4...data received concatenated...
	memcpy((void*)fixture.buffer, &fixture.m_somecmd, sizeof(sSomeCmd));
	memcpy((void*) &fixture.buffer[sizeof(sSomeCmd)], &fixture.m_somecmdrsp, sizeof(sSomeCmdRsp));
	fixture.m_tx.SendData(&fixture.buffer[0],sizeof(sSomeCmd) + sizeof(sSomeCmdRsp));
	IsEqual(fixture.m_somecmd, fixture.m_rx.m_rxsomecmd);
	IsEqual(fixture.m_somecmdrsp, fixture.m_rx.m_rxsomecmdrsp);

	mu_assert(fixture.m_rx.m_unknown_message_received, "Unknown message NOT received");
}

MU_TEST(Scenario_6_2_UnknownDataBiggerThanFragmentBuf_SAME_PREAMBLE_Fragmented)
{
	MsgByteStreamHandlingGroup fixture;

	mu_assert(fixture.m_tx.HasMsgReceiver(), "Does not have a message receiver, but should have.");
	mu_assert(!fixture.m_tx.HasRawDataReceiver(), "Has a raw data receiver, but should not have.");

	sUnknownToCommunicationLayer data_unknown;
	INIT_DATA_UNKNOWN_SAME_PREAMBLE;
	uint8* start_data = (uint8*)&data_unknown;
	// Shouldnt crash, should simply get a printout...
	size_t tx_cnt = 50;
	size_t tx_rem = sizeof(sUnknownToCommunicationLayer);
	size_t i_cnt = 0;
	while(tx_rem != 0){
		if(tx_cnt > tx_rem)
			tx_cnt = tx_rem;
		fixture.m_tx.SendData(&start_data[i_cnt],tx_cnt);
		tx_rem -= tx_cnt;
		i_cnt  += tx_cnt;
#ifdef __arm__
		if(tx_rem > 0){
			mu_check(fixture.m_tx.HasDataExceedingFragmentBufferSize());
		}
		else{ // Would have been reset once all the bytes were parsed...
			mu_check(!fixture.m_tx.HasDataExceedingFragmentBufferSize());
		}
#endif
	}
	// Other messages should still work
#ifdef __arm__
	mu_check(!fixture.m_tx.HasDataExceedingFragmentBufferSize()); // Would have already been cleared.
#endif

	/// Scanerio 4...data received concatenated...
	memcpy((void*)fixture.buffer, &fixture.m_somecmd, sizeof(sSomeCmd));
	memcpy((void*) &fixture.buffer[sizeof(sSomeCmd)], &fixture.m_somecmdrsp, sizeof(sSomeCmdRsp));
	fixture.m_tx.SendData(&fixture.buffer[0],sizeof(sSomeCmd) + sizeof(sSomeCmdRsp));
	IsEqual(fixture.m_somecmd, fixture.m_rx.m_rxsomecmd);
	IsEqual(fixture.m_somecmdrsp, fixture.m_rx.m_rxsomecmdrsp);

	mu_assert(fixture.m_rx.m_unknown_message_received, "Unknown message NOT received");
}

MU_TEST(Scenario_6_3_UnknownDataBiggerThanFragmentBuf_SAME_PREAMBLE_Whole)
{
	MsgByteStreamHandlingGroup fixture;

	mu_assert(fixture.m_tx.HasMsgReceiver(), "Does not have a message receiver, but should have.");
	mu_assert(!fixture.m_tx.HasRawDataReceiver(), "Has a raw data receiver, but should not have.");

	sUnknownToCommunicationLayer data_unknown;
	INIT_DATA_UNKNOWN_SAME_PREAMBLE;
	// Shouldnt crash, should simply get a printout...
	fixture.m_tx.SendData((uint8*)&data_unknown,sizeof(sUnknownToCommunicationLayer));
	// Other messages should still work
#ifdef __arm__
	mu_check(!fixture.m_tx.HasDataExceedingFragmentBufferSize()); // Would have already been cleared.
#endif

	/// Scanerio 4...data received concatenated...
	memcpy((void*)fixture.buffer, &fixture.m_somecmd, sizeof(sSomeCmd));
	memcpy((void*) &fixture.buffer[sizeof(sSomeCmd)], &fixture.m_somecmdrsp, sizeof(sSomeCmdRsp));
	fixture.m_tx.SendData(&fixture.buffer[0],sizeof(sSomeCmd) + sizeof(sSomeCmdRsp));
	IsEqual(fixture.m_somecmd, fixture.m_rx.m_rxsomecmd);
	IsEqual(fixture.m_somecmdrsp, fixture.m_rx.m_rxsomecmdrsp);

	mu_assert(fixture.m_rx.m_unknown_message_received, "Unknown message NOT received");
}

MU_TEST(Scenario_6_4_UnknownDataBiggerThanFragmentBuf_DIFFERENT_PREAMBLE_ByteForByte)
{
	MsgByteStreamHandlingGroup fixture;

	mu_assert(fixture.m_tx.HasMsgReceiver(), "Does not have a message receiver, but should have.");
	mu_assert(!fixture.m_tx.HasRawDataReceiver(), "Has a raw data receiver, but should not have.");

	sUnknownToCommunicationLayer data_unknown;
	INIT_DATA_UNKNOWN_DIFFERENT_PREAMBLE;
	uint8* start_data = (uint8*)&data_unknown;
	// Shouldnt crash, should simply get a printout...
	for (size_t i = 0; i < sizeof(sUnknownToCommunicationLayer); ++i) {
		fixture.m_tx.SendData(&start_data[i], 1);
	}
	// Other messages should still work
#ifdef __arm__
	mu_check(!fixture.m_tx.HasDataExceedingFragmentBufferSize()); // data should never make it this far from a different preamble/interface
#endif

													   /// Scanerio 4...data received concatenated...
	memcpy((void*)fixture.buffer, &fixture.m_somecmd, sizeof(sSomeCmd));
	memcpy((void*)&fixture.buffer[sizeof(sSomeCmd)], &fixture.m_somecmdrsp, sizeof(sSomeCmdRsp));
	fixture.m_tx.SendData(&fixture.buffer[0], sizeof(sSomeCmd) + sizeof(sSomeCmdRsp));
	IsEqual(fixture.m_somecmd, fixture.m_rx.m_rxsomecmd);
	IsEqual(fixture.m_somecmdrsp, fixture.m_rx.m_rxsomecmdrsp);

	mu_assert(!fixture.m_rx.m_unknown_message_received, "Unknown message received...data should never make it this far in this case");
}

MU_TEST(Scenario_6_5_UnknownDataBiggerThanFragmentBuf_DIFFERENT_PREAMBLE_Fragmented)
{
	MsgByteStreamHandlingGroup fixture;

	mu_assert(fixture.m_tx.HasMsgReceiver(), "Does not have a message receiver, but should have.");
	mu_assert(!fixture.m_tx.HasRawDataReceiver(), "Has a raw data receiver, but should not have.");

	sUnknownToCommunicationLayer data_unknown;
	INIT_DATA_UNKNOWN_DIFFERENT_PREAMBLE;
	uint8* start_data = (uint8*)&data_unknown;
	// Shouldnt crash, should simply get a printout...
	size_t tx_cnt = 50;
	size_t tx_rem = sizeof(sUnknownToCommunicationLayer);
	size_t i_cnt = 0;
	while (tx_rem != 0) {
		if (tx_cnt > tx_rem)
			tx_cnt = tx_rem;
		fixture.m_tx.SendData(&start_data[i_cnt], tx_cnt);
		tx_rem -= tx_cnt;
		i_cnt += tx_cnt;
#ifdef __arm__
		if (tx_rem > 0) {
			mu_check(!fixture.m_tx.HasDataExceedingFragmentBufferSize()); // data should never make it this far from a different preamble/interface
		}
		else {
			mu_check(!fixture.m_tx.HasDataExceedingFragmentBufferSize()); // data should never make it this far from a different preamble/interface
		}
#endif
	}
	// Other messages should still work
#ifdef __arm__
	mu_assert(!fixture.m_tx.HasDataExceedingFragmentBufferSize(),"Has data exceeding fragment buffer size."); // data should never make it this far from a different preamble/interface
#endif

													   /// Scanerio 4...data received concatenated...
	memcpy((void*)fixture.buffer, &fixture.m_somecmd, sizeof(sSomeCmd));
	memcpy((void*)&fixture.buffer[sizeof(sSomeCmd)], &fixture.m_somecmdrsp, sizeof(sSomeCmdRsp));
	fixture.m_tx.SendData(&fixture.buffer[0], sizeof(sSomeCmd) + sizeof(sSomeCmdRsp));
	IsEqual(fixture.m_somecmd, fixture.m_rx.m_rxsomecmd);
	IsEqual(fixture.m_somecmdrsp, fixture.m_rx.m_rxsomecmdrsp);

	mu_assert(!fixture.m_rx.m_unknown_message_received, "Unknown message received...data should never make it this far in this case");
}

MU_TEST(Scenario_6_6_UnknownDataBiggerThanFragmentBuf_DIFFERENT_PREAMBLE_Whole)
{
	MsgByteStreamHandlingGroup fixture;

	mu_assert(fixture.m_tx.HasMsgReceiver(), "Does not have a message receiver, but should have.");
	mu_assert(!fixture.m_tx.HasRawDataReceiver(), "Has a raw data receiver, but should not have.");

	sUnknownToCommunicationLayer data_unknown;
	INIT_DATA_UNKNOWN_DIFFERENT_PREAMBLE;
	// Shouldnt crash, should simply get a printout...
	fixture.m_tx.SendData((uint8*)&data_unknown, sizeof(sUnknownToCommunicationLayer));
	// Other messages should still work
#ifdef __arm__
	mu_check(!fixture.m_tx.HasDataExceedingFragmentBufferSize()); // data should never make it this far from a different preamble/interface
#endif

													   /// Scanerio 4...data received concatenated...
	memcpy((void*)fixture.buffer, &fixture.m_somecmd, sizeof(sSomeCmd));
	memcpy((void*)&fixture.buffer[sizeof(sSomeCmd)], &fixture.m_somecmdrsp, sizeof(sSomeCmdRsp));
	fixture.m_tx.SendData(&fixture.buffer[0], sizeof(sSomeCmd) + sizeof(sSomeCmdRsp));
	IsEqual(fixture.m_somecmd, fixture.m_rx.m_rxsomecmd);
	IsEqual(fixture.m_somecmdrsp, fixture.m_rx.m_rxsomecmdrsp);

	mu_assert(!fixture.m_rx.m_unknown_message_received, "Unknown message received...data should never make it this far in this case");
}

MU_TEST(Scenario_7_HeaderOnlyMessages)
{
	MsgByteStreamHandlingGroup fixture;

	mu_assert(fixture.m_tx.HasMsgReceiver(), "Does not have a message receiver, but should have.");
	mu_assert(!fixture.m_tx.HasRawDataReceiver(), "Has a raw data receiver, but should not have.");

	/// 7) messages with zero payload (header only messages)
	memcpy((void*)fixture.buffer, &fixture.m_headeronlycmd, sizeof(sHeaderOnlyCmd));
	fixture.m_tx.SendData(&fixture.buffer[0], sizeof(sHeaderOnlyCmd));
	IsEqual(fixture.m_headeronlycmd, fixture.m_rx.m_rxheaderonlycmd);

	fixture.clear_rx();

	for(size_t i = 0; i < sizeof(sHeaderOnlyCmd); ++i)
		fixture.m_tx.SendData(&fixture.buffer[i], 1);
	IsEqual(fixture.m_headeronlycmd, fixture.m_rx.m_rxheaderonlycmd);

	mu_assert(!fixture.m_rx.m_unknown_message_received, "Unknown message received");
}

uint8 garbage_buffer[FRAGMENT_BUF_SIZE];
MU_TEST(Scenario_8_RealDataBetweenGARBAGE_sync_to_stream)
{
	MsgByteStreamHandlingGroup fixture;

	/// 8) Random bytes that are not protocol based. GARBAGE.
	for (auto i = 0; i < FRAGMENT_BUF_SIZE; ++i)
		garbage_buffer[i] = i;

	// Randomise the amount of garbage sent before...try break it
	for (int j = 1; j < FRAGMENT_BUF_SIZE; ++j)
	{
		// VArying amounts of garbage at the beginning...
		//for (size_t i = 0; i < j; ++i)
		//	m_tx.SendData(&garbage_buffer[i], 1);
		//
		// Above is a nice test -> the momeny j = 174, the last sent char is 173.
		// This corresponds with the LSB of the preamble (i.e. 0xAD in 0xDEAD)...
		// As such the data is discarded, as the preamble is wrong...
		// How to treat this? And how likely is such a scenario? This could be fixed with 'ack' style ping-pong...no ack sent, so transmitter tries again...
		// For now...I do this
		// VArying amounts of garbage at the end...asd blob
		fixture.m_tx.SendData(&garbage_buffer[0], j);

				/// Scanerio 4...data received concatenated...
		memcpy((void*)fixture.buffer, &fixture.m_somecmd, sizeof(sSomeCmd));
		memcpy((void*)&fixture.buffer[sizeof(sSomeCmd)], &fixture.m_somecmdrsp, sizeof(sSomeCmdRsp));
		fixture.m_tx.SendData(&fixture.buffer[0], sizeof(sSomeCmd) + sizeof(sSomeCmdRsp));
		IsEqual(fixture.m_somecmd, fixture.m_rx.m_rxsomecmd);
		IsEqual(fixture.m_somecmdrsp, fixture.m_rx.m_rxsomecmdrsp);

		fixture.clear_rx();

		// VArying amounts of garbage at the end...asd blob
		fixture.m_tx.SendData(&garbage_buffer[0], j);
	}

	mu_assert(!fixture.m_rx.m_unknown_message_received, "Unknown message received");
}


MU_TEST_SUITE(MsgByteStreamHandling_Suite) {
	MU_RUN_TEST(Scenario1_ByteForByteIndividualPackets);
	MU_RUN_TEST(Scenario2_SmallFragments);
	MU_RUN_TEST(Scenario3_FullPackets);
	MU_RUN_TEST(Scenario4_1_FullPacketsConcatenated);
	MU_RUN_TEST(Scenario4_2_FullPacketsConcatenated_ByteForByte);
	MU_RUN_TEST(Scenario_5_FragmentedAndMoreFragmented);
	MU_RUN_TEST(Scenario_6_1_UnknownDataBiggerThanFragmentBuf_SAME_PREAMBLE_ByteForByte);
	MU_RUN_TEST(Scenario_6_2_UnknownDataBiggerThanFragmentBuf_SAME_PREAMBLE_Fragmented);
	MU_RUN_TEST(Scenario_6_3_UnknownDataBiggerThanFragmentBuf_SAME_PREAMBLE_Whole);
	MU_RUN_TEST(Scenario_6_4_UnknownDataBiggerThanFragmentBuf_DIFFERENT_PREAMBLE_ByteForByte);
	MU_RUN_TEST(Scenario_6_5_UnknownDataBiggerThanFragmentBuf_DIFFERENT_PREAMBLE_Fragmented);
	MU_RUN_TEST(Scenario_6_6_UnknownDataBiggerThanFragmentBuf_DIFFERENT_PREAMBLE_Whole);
	MU_RUN_TEST(Scenario_7_HeaderOnlyMessages);
	MU_RUN_TEST(Scenario_8_RealDataBetweenGARBAGE_sync_to_stream);
}

/// This testgroup should cover the following test scenarios:
///
/// 1) raw data is passed through

struct RawDataByteStreamHandlingGroup
{
	CTestRawDataReceiver m_rx;
	CTestConnection		 m_tx;

	uint8 txbuffer[FRAGMENT_BUF_SIZE];
	uint8 rxbuffer[FRAGMENT_BUF_SIZE];


	RawDataByteStreamHandlingGroup()
	{
		uint8* r = &rxbuffer[0];
		m_rx.SetRxBuf(r);
		m_tx.SetRawDataReceiver(&m_rx);
		
		for (uint16 i = 0; i < FRAGMENT_BUF_SIZE; ++i)
		{
			txbuffer[i] = i & 0x00FF;
		}

		clear_rx();
	}
	void clear_rx()
	{
		memset((void*)&rxbuffer[0], 0, sizeof(uint8)*FRAGMENT_BUF_SIZE);
	}
};

MU_TEST(Scenario_1_RawDataThroughput)
{
	RawDataByteStreamHandlingGroup fixture;

	mu_assert(!fixture.m_tx.HasMsgReceiver(), "Has a message data receiver, but should not have.");
	mu_assert(fixture.m_tx.HasRawDataReceiver(), "Does not have a raw receiver, but should have.");

	/// 1) Raw data is passed through...
	fixture.m_tx.SendData(&fixture.txbuffer[0], sizeof(uint8)*FRAGMENT_BUF_SIZE);
	
	mu_assert(fixture.m_rx.NumberOfBytedRx() == FRAGMENT_BUF_SIZE, "Unequal number of bytes throughtput.");

	for (uint16 i = 0; i < FRAGMENT_BUF_SIZE; ++i)
	{
		mu_assert(fixture.txbuffer[i] == fixture.rxbuffer[i], "Unequal byte in bytestream.");
	}
}

MU_TEST_SUITE(RawDataByteStreamHandling_Suite) {
	MU_RUN_TEST(Scenario_1_RawDataThroughput);
}