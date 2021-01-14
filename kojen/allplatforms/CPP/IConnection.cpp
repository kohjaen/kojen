#include "IConnection.h"
#include "MsgHeader.h"
#ifdef __arm__
#include <stdio.h>
#include <string.h>
#endif

namespace XKoJen
{
	IConnection::~IConnection() {}
	IConnection::IConnection() :
		m_fragment_buffer_bytes_required(0),
		m_msg_receiver(nullptr),
#if defined(__arm__)
		m_has_data_exceeding_fragment_buffer_size(false),
		m_largest_message_size(FRAGMENT_BUF_SIZE),
		m_fragment_buffer_cnt(0),
#else
		m_request_disconnect(false),
#endif
		m_sizeofheader(sizeof(sMsgHeader)),
		m_receiver_preamble(0)
	{
	}

	void IConnection::SetMsgReceiver(IMsgReceiver* receiver)
	{
		// Warn if receiver is nullptr
		if (receiver) {
			m_rawdata_receiver = nullptr;
			m_msg_receiver = receiver;
			m_receiver_preamble = receiver->Preamble();
			m_receiver_preamble_0 = m_receiver_preamble & 0x00FF;
			m_receiver_preamble_1 = m_receiver_preamble >> 8;
#if defined(__arm__)
			m_largest_message_size = receiver->LargestMessageSize();
			// Check that this is at least half the size of the fragment buffer.
			if (2 * m_largest_message_size > FRAGMENT_BUF_SIZE)
				printf("Warning : IConnection::SetMsgReceiver -> for safety fragment buffer(%i) needs to be at least twice the largest interface message size(%i).", m_largest_message_size, FRAGMENT_BUF_SIZE);
#endif // __arm__
		}
		//else
		//	printf("ERROR : IConnection::SetMsgReceiver -> m_receiver is a nullptr...no messages can be received.");
	}
	bool IConnection::HasMsgReceiver() const
	{
		return (m_msg_receiver != nullptr);
	}

	void IConnection::SetRawDataReceiver(IRawDataReceiver* receiver)
	{
		if (receiver)
		{
			m_msg_receiver = nullptr;
			m_rawdata_receiver = receiver;
		}
	}
	bool IConnection::HasRawDataReceiver() const
	{
		return (m_rawdata_receiver != nullptr);
	}

#if !defined(__arm__)
	void IConnection::RequestDisconnect()
	{
		std::unique_lock<std::mutex> lock(m_request_disconnect_mutex);
		m_request_disconnect = true;
	}
#else
	bool IConnection::HasDataExceedingFragmentBufferSize()
	{
		return m_has_data_exceeding_fragment_buffer_size;
	}
#endif
	
#if defined(__arm__)

#define RESET_FRAG \
	{\
		m_fragment_buffer_cnt = 0;\
		m_fragment_buffer_bytes_required = 0;\
	}

#else

#define RESET_FRAG \
	{\
		m_fragment_buffer_cnt = 0;\
		m_fragment_buffer_bytes_required = 0;\
		m_fragment_buffer.resize(0);\
	}

#endif

#define PREAMBLE_SAFETY \
if(header->Preamble != m_receiver_preamble){\
	RESET_FRAG \
	return;\
}

	void IConnection::OnDataReceived(const uint8* data_buffer, const uint32& number_of_bytes_rx)
	{
		if (number_of_bytes_rx == 0) return;
		if (m_rawdata_receiver)
		{
			m_rawdata_receiver->OnDataReceived(data_buffer, number_of_bytes_rx);
		}
		else if (m_msg_receiver)
		{
			// What if someone puts in chars that dont match anything? USE the max message size...clear once it get to that...
#if defined(__arm__)
			if (m_fragment_buffer_cnt >= m_largest_message_size /*&& m_fragment_buffer_bytes_required == 0*/) // this might fail a unit test on arm ... need to check...
				RESET_FRAG;
#else
			size_t m_fragment_buffer_cnt = m_fragment_buffer.size();
#endif

			// For unfragmented data, and less than headersize rx, check preamble...and ignore if not found
			if (0 == m_fragment_buffer_cnt)
			{
				if (number_of_bytes_rx < 2) { // 1
					if (data_buffer[0] != m_receiver_preamble_0)
						return;
				}
				else if (number_of_bytes_rx >= 2) {
					if ((data_buffer[0] != m_receiver_preamble_0) || (data_buffer[1] != m_receiver_preamble_1))
						return;
				}
				// rest will be process in header
			}

			uint32 bytes_for_msg = 0;
			uint32 no_bytes_rx_plus_in_frag_buf = number_of_bytes_rx + m_fragment_buffer_cnt;

			// What if we don't get a full header?
			if (no_bytes_rx_plus_in_frag_buf < m_sizeofheader)
			{
#if defined(__arm__)
				memcpy((void*)&m_fragment_buffer[m_fragment_buffer_cnt], (void*)data_buffer, number_of_bytes_rx);
				m_fragment_buffer_cnt += number_of_bytes_rx;
#else
				m_fragment_buffer.resize(m_fragment_buffer_cnt + number_of_bytes_rx);
				memcpy((void*)&m_fragment_buffer[m_fragment_buffer_cnt], (void*)data_buffer, number_of_bytes_rx);
				m_fragment_buffer_cnt = m_fragment_buffer.size();
#endif
				// For unfragmented data, and less than headersize rx, check preamble...and ignore if not found
				if (m_fragment_buffer_cnt < 2) { // 1
					if (m_fragment_buffer[0] != m_receiver_preamble_0) {
						RESET_FRAG
					}
				}
				else if (m_fragment_buffer_cnt >= 2) {
					if ((m_fragment_buffer[0] != m_receiver_preamble_0) || (m_fragment_buffer[1] != m_receiver_preamble_1)) {
						RESET_FRAG
					}
				}
				return;
			}
			else if (no_bytes_rx_plus_in_frag_buf == m_sizeofheader) // Rx'd a full header...
			{
#if defined(__arm__)
				memcpy((void*)&m_fragment_buffer[m_fragment_buffer_cnt], (void*)data_buffer, number_of_bytes_rx);
				m_fragment_buffer_cnt += number_of_bytes_rx;

				// Should now have a full header...how much is still required?
				sMsgHeader* header = (sMsgHeader*)(m_fragment_buffer);
				bytes_for_msg = m_sizeofheader + header->PayloadSize;

				// No crashing for garbage received...data is parsed over, but not written to buffer.
				if (bytes_for_msg > m_largest_message_size) {
					m_has_data_exceeding_fragment_buffer_size = true;
				}
#else
				m_fragment_buffer.resize(m_fragment_buffer_cnt + number_of_bytes_rx);
				memcpy((void*)&m_fragment_buffer[m_fragment_buffer_cnt], (void*)data_buffer, number_of_bytes_rx);
				m_fragment_buffer_cnt += number_of_bytes_rx;

				// Should now have a full header...how much is still required?
				sMsgHeader* header = (sMsgHeader*)(&m_fragment_buffer[0]);
				bytes_for_msg = m_sizeofheader + header->PayloadSize;
#endif
				PREAMBLE_SAFETY;

				m_fragment_buffer_bytes_required = bytes_for_msg - m_fragment_buffer_cnt;

				if (m_fragment_buffer_bytes_required == 0) // header only message
				{
#if defined(__arm__)
					m_msg_receiver->OnMessageReceived(m_fragment_buffer, m_fragment_buffer_cnt);
#else
					m_msg_receiver->OnMessageReceived(&m_fragment_buffer[0], m_fragment_buffer_cnt);
#endif
					RESET_FRAG;
				}
				return;
			}

			// Are we already processing fragmented data?
			if (m_fragment_buffer_cnt == 0)
			{
				// Should now have a full header...how much is still required?
				sMsgHeader* header = (sMsgHeader*)(data_buffer);
				bytes_for_msg = m_sizeofheader + header->PayloadSize;
				PREAMBLE_SAFETY;
#if defined(__arm__)
				// No crashing for garbage received...
				if (bytes_for_msg > m_largest_message_size)
				{
					m_has_data_exceeding_fragment_buffer_size = true;
				}
#endif // __arm__

				if (number_of_bytes_rx == bytes_for_msg)			// Ideal case : the match
				{
					m_msg_receiver->OnMessageReceived(data_buffer, number_of_bytes_rx);
#if defined(__arm__)
					m_has_data_exceeding_fragment_buffer_size = false;
#endif // __arm__
				}
				else if (number_of_bytes_rx < bytes_for_msg)		// Fragmented data received
				{
					m_fragment_buffer_cnt = number_of_bytes_rx;
#if defined(__arm__)
					// Check that there is enough space in the fragment buffer...
					if (!m_has_data_exceeding_fragment_buffer_size)
						memcpy((void*)&m_fragment_buffer[0], (void*)data_buffer, number_of_bytes_rx);
#else				
					m_fragment_buffer.resize(number_of_bytes_rx);
					memcpy((void*)&m_fragment_buffer[0], (void*)data_buffer, number_of_bytes_rx);
#endif // __arm__
					m_fragment_buffer_bytes_required = bytes_for_msg - number_of_bytes_rx;
				}
				else if (number_of_bytes_rx > bytes_for_msg)		// Concatenated data received
				{
					m_msg_receiver->OnMessageReceived(data_buffer, bytes_for_msg);
					// Recurse
					OnDataReceived(&data_buffer[bytes_for_msg], number_of_bytes_rx - bytes_for_msg);
				}
			}
			else
			{
				// **** CASE 5 : NEW
				//There is some data in the frag buffer, but it wasnt enough to extract a header...
				if (m_fragment_buffer_bytes_required == 0 && bytes_for_msg == 0 && m_fragment_buffer_cnt < m_sizeofheader)
				{
					if (no_bytes_rx_plus_in_frag_buf < m_sizeofheader)
					{
#if defined(__arm__)
						memcpy((void*)&m_fragment_buffer[m_fragment_buffer_cnt], (void*)data_buffer, number_of_bytes_rx);
#else
						m_fragment_buffer.resize(m_fragment_buffer_cnt + number_of_bytes_rx);
						memcpy((void*)&m_fragment_buffer[m_fragment_buffer_cnt], (void*)data_buffer, number_of_bytes_rx);
#endif
						m_fragment_buffer_cnt += number_of_bytes_rx;
						return;
					}
					else
					{
						// There is enough for a header. Dont unneccessarily use the frag buffer...just extract the header
						uint16 size_to_process = m_sizeofheader - m_fragment_buffer_cnt;
#if defined(__arm__)
						memcpy((void*)&m_fragment_buffer[m_fragment_buffer_cnt], (void*)data_buffer, size_to_process);
#else
						m_fragment_buffer.resize(m_fragment_buffer_cnt + size_to_process);
						memcpy((void*)&m_fragment_buffer[m_fragment_buffer_cnt], (void*)data_buffer, size_to_process);
#endif
						m_fragment_buffer_cnt += size_to_process;

						// Should now have a full header...how much is still required?
#if defined(__arm__)
						sMsgHeader* header = (sMsgHeader*)(m_fragment_buffer);
#else
						sMsgHeader* header = (sMsgHeader*)(&m_fragment_buffer[0]);
#endif
						bytes_for_msg = m_sizeofheader + header->PayloadSize;
						PREAMBLE_SAFETY;
#if defined(__arm__)
						// No crashing for garbage received...data is parsed over, but not written to buffer.
						if (bytes_for_msg > m_largest_message_size) {
							m_has_data_exceeding_fragment_buffer_size = true;
						}
#endif

						m_fragment_buffer_bytes_required = bytes_for_msg - m_fragment_buffer_cnt;
						// Recurse...
						if (number_of_bytes_rx - size_to_process > 0)
							OnDataReceived(&data_buffer[size_to_process], number_of_bytes_rx - size_to_process);
						return;
					}
				}
				// **** CASE 5 : NEW

				if (number_of_bytes_rx < m_fragment_buffer_bytes_required)		// Data is majorly fragmented
				{
#if defined(__arm__)
					// Check that there is enough space in the fragment buffer...
					if (!m_has_data_exceeding_fragment_buffer_size)
						memcpy((void*)&m_fragment_buffer[m_fragment_buffer_cnt], (void*)data_buffer, number_of_bytes_rx);
#else
					m_fragment_buffer.resize(m_fragment_buffer_cnt + number_of_bytes_rx);
					memcpy((void*)&m_fragment_buffer[m_fragment_buffer_cnt], (void*)data_buffer, number_of_bytes_rx);
#endif // __arm__

					m_fragment_buffer_cnt += number_of_bytes_rx;
					m_fragment_buffer_bytes_required -= number_of_bytes_rx;
				}
				else if (number_of_bytes_rx == m_fragment_buffer_bytes_required)	// We have everything we need
				{
#if defined(__arm__)
					// Check that there is enough space in the fragment buffer...
					if (!m_has_data_exceeding_fragment_buffer_size)
						memcpy((void*)&m_fragment_buffer[m_fragment_buffer_cnt], (void*)data_buffer, number_of_bytes_rx);
#else
					m_fragment_buffer.resize(m_fragment_buffer_cnt + number_of_bytes_rx);
					memcpy((void*)&m_fragment_buffer[m_fragment_buffer_cnt], (void*)data_buffer, number_of_bytes_rx);
#endif // __arm__

					m_fragment_buffer_cnt += number_of_bytes_rx;

#if defined(__arm__)
					m_msg_receiver->OnMessageReceived(m_fragment_buffer, m_fragment_buffer_cnt);
#else
					m_msg_receiver->OnMessageReceived(&m_fragment_buffer[0], m_fragment_buffer_cnt);
#endif

					RESET_FRAG;

#if defined(__arm__)
					m_has_data_exceeding_fragment_buffer_size = false;
#endif // __arm__
				}
				else if (number_of_bytes_rx > m_fragment_buffer_bytes_required)	// We received more : so the remained of the last fragment, concatenated to something else.
				{


#if defined(__arm__)
					// Check that there is enough space in the fragment buffer...
					if (!m_has_data_exceeding_fragment_buffer_size)
						memcpy((void*)&m_fragment_buffer[m_fragment_buffer_cnt], (void*)data_buffer, m_fragment_buffer_bytes_required);
#else
					// Resize, only if non-zero
					if (m_fragment_buffer_bytes_required > 0) {
						m_fragment_buffer.resize(m_fragment_buffer_cnt + m_fragment_buffer_bytes_required);
						memcpy((void*)&m_fragment_buffer[m_fragment_buffer_cnt], (void*)data_buffer, m_fragment_buffer_bytes_required);
					}
#endif // __arm__

					m_fragment_buffer_cnt += m_fragment_buffer_bytes_required;

#if defined(__arm__)
					m_msg_receiver->OnMessageReceived(m_fragment_buffer, m_fragment_buffer_cnt);
#else
					m_msg_receiver->OnMessageReceived(&m_fragment_buffer[0], m_fragment_buffer_cnt);
#endif

					// Pass unhandled remainder recursively, but need to reset fragment buffer, as recursive call might use it...
					uint32 start = m_fragment_buffer_bytes_required;
					uint32 cnt = number_of_bytes_rx - m_fragment_buffer_bytes_required;
					RESET_FRAG;
#if defined(__arm__)
					m_has_data_exceeding_fragment_buffer_size = false;
#endif // __arm__
					OnDataReceived(&data_buffer[start], cnt);
				}
			}
		}
	}
}