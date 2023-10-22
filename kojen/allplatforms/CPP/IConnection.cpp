#include "basetypes.h"
#include "IConnection.h"
#include "MsgHeader.h"
#ifdef __arm__
#include <cassert>
#endif
#include <algorithm>

// Header used for connection message parsing
static constexpr uint16 SizeOfHeader = sizeof(sMsgHeader);

namespace XKoJen
{
    IConnection::~IConnection() {}

    IConnection::IConnection()
    : m_fragment_buffer_bytes_required{0}
    , m_msg_receiver{nullptr}
    , m_rawdata_receiver{nullptr}
#if defined(__arm__)
    , m_has_data_exceeding_fragment_buffer_size{false}
    , m_largest_message_size{FRAGMENT_BUF_SIZE}
    , m_fragment_buffer_cnt{0}
#else
    , m_request_disconnect{false}
#endif
    , m_receiver_preamble{0}
    {}

    void IConnection::SetMsgReceiver(IMsgReceiver& receiver)
    {
        m_rawdata_receiver = nullptr;
        m_msg_receiver = &receiver;
        m_receiver_preamble = receiver.Preamble();
        m_receiver_preamble_0 = m_receiver_preamble & 0x00FF;
        m_receiver_preamble_1 = m_receiver_preamble >> 8;
#if defined(__arm__)
        m_largest_message_size = receiver.LargestMessageSize();
        // Check that this is at least half the size of the fragment buffer.
        if (2 * m_largest_message_size > FRAGMENT_BUF_SIZE)
            printf("Warning : IConnection::SetMsgReceiver -> for safety fragment buffer(%i) needs to be at least twice the largest interface message size(%i).", m_largest_message_size, FRAGMENT_BUF_SIZE);
#endif // __arm__
    }

    bool IConnection::HasMsgReceiver() const
    {
        return (m_msg_receiver != nullptr);
    }

    void IConnection::SetRawDataReceiver(IRawDataReceiver& receiver)
    {
        m_msg_receiver = nullptr;
        m_rawdata_receiver = &receiver;
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

    void IConnection::ResetFragmentation()
    {
        m_fragment_buffer_bytes_required = 0;
#if defined(__arm__)
        m_fragment_buffer_cnt = 0;
        m_has_data_exceeding_fragment_buffer_size =false;
#else
        m_fragment_buffer.resize(0);
#endif
    }

    std::optional<uint32> IConnection::FindPreamble(const uint8* data, const uint32 count)
    {
        uint32 i = 0;
        while (i < count)
        {
            if (data[i] == m_receiver_preamble_0)
            {
                if (i < count - 1)
                {
                    if (data[i + 1] == m_receiver_preamble_1)
                    {
                        return i;
                    }
                }
                else if (i == (count - 1))// last one...potentially fragmented preamble.
                    return i;
            }
            i++;
        }
        return std::optional<uint16>();
    }
    void IConnection::PutIntoFragmentBuffer(const uint8* data, const uint32 count)
    {
#if defined(__arm__)
        auto fragmentLast = m_fragment_buffer_cnt;
        m_fragment_buffer_cnt += count;
        if (m_has_data_exceeding_fragment_buffer_size) // Keep account ... but no copy.
            return;
#else
        auto fragmentLast = m_fragment_buffer.size();
        m_fragment_buffer.resize(fragmentLast + count);
#endif
        std::copy(data, data + count, std::addressof(m_fragment_buffer[fragmentLast]));
    }

    void IConnection::HandleFragmentedData(const uint8* data, const uint32 count)
    {
#if defined(__arm__)
#else
        auto m_fragment_buffer_cnt = m_fragment_buffer.size();
#endif
        uint32 totalFragmentedByteCount = count + m_fragment_buffer_cnt;

        // Fragmented header support : if there is 1 byte only in the fragment buffer, then the header
        // was fragmented...or there was some garbage which just so happened to be the last byte of the last message (that matches)
        // the first byte of the header. For this fragmented data to be real, it would be expected that
        // the first byte of the next set is the second byte of the header...
        if ( (m_fragment_buffer_cnt == 1) && (data[0] != m_receiver_preamble_1) )
        {
            ResetFragmentation();
            if (data[0] == m_receiver_preamble_0)
            {
                OnDataReceived(data, count); // start new
            }
            return;
        }
#if defined(__arm__)
        // No crashing for garbage received...data is parsed over, but not written to buffer.
        m_has_data_exceeding_fragment_buffer_size = m_has_data_exceeding_fragment_buffer_size || (totalFragmentedByteCount > FRAGMENT_BUF_SIZE);//(/*totalFragmentedByteCount*/count > m_largest_message_size);
#endif

        if (m_fragment_buffer_bytes_required == 0)
        {
            if (totalFragmentedByteCount < SizeOfHeader)
            {
                // There is some data in the fragment buffer but it was not enough to extract message information.
                PutIntoFragmentBuffer(data, count);
            }
            else
            {
                // There is enough for a header. Extract the header.
                uint32 size_to_process = SizeOfHeader - m_fragment_buffer_cnt;
                PutIntoFragmentBuffer(data, size_to_process);
                // Enough data is present to determine the required message size.
                sMsgHeader* header = (sMsgHeader*)(&m_fragment_buffer[0]);
                uint32 msgSize = SizeOfHeader + header->PayloadSize;
#if defined(__arm__)
                // No crashing for garbage received...data is parsed over, but not written to buffer.
                m_has_data_exceeding_fragment_buffer_size = m_has_data_exceeding_fragment_buffer_size || (msgSize > m_largest_message_size);
#endif
                if (totalFragmentedByteCount < msgSize)
                {
                    PutIntoFragmentBuffer(std::addressof(data[size_to_process]), count - size_to_process);
#if defined(__arm__)
#else
                    m_fragment_buffer_cnt = m_fragment_buffer.size();
#endif
                    m_fragment_buffer_bytes_required = msgSize - m_fragment_buffer_cnt;
                }
                else
                {
                    uint32 rxBytesParsed = size_to_process;
                    // Enough data to handle a full message ... and maybe more...
                    PutIntoFragmentBuffer(std::addressof(data[size_to_process]), msgSize - SizeOfHeader);
                    rxBytesParsed += (msgSize - SizeOfHeader);
                    assert(m_fragment_buffer[0] == m_receiver_preamble_0 && m_fragment_buffer[1] == m_receiver_preamble_1); // TODO : remove? Handle?
                    m_msg_receiver->OnMessageReceived(std::addressof(m_fragment_buffer[0]), msgSize);
                    ResetFragmentation();

                    if (count > rxBytesParsed) // Recurse
                    {
                        OnDataReceived(std::addressof(data[rxBytesParsed]), count - rxBytesParsed);
                    }
                }
            }
        }
        else
        {
            if (count < m_fragment_buffer_bytes_required)		// Data is majorly fragmented
            {
                PutIntoFragmentBuffer(data, count);
                m_fragment_buffer_bytes_required -= count;
            }
            else
            {
                uint32 rxBytesParsed = m_fragment_buffer_bytes_required;
                PutIntoFragmentBuffer(data, m_fragment_buffer_bytes_required);
#if defined(__arm__)
#else
                m_fragment_buffer_cnt = m_fragment_buffer.size();
#endif
                assert(m_fragment_buffer[0] == m_receiver_preamble_0 && m_fragment_buffer[1] == m_receiver_preamble_1); // TODO : remove? Handle?
                m_msg_receiver->OnMessageReceived(std::addressof(m_fragment_buffer[0]), m_fragment_buffer_cnt);
                ResetFragmentation();

                if (count > rxBytesParsed) // Recurse
                {
                    OnDataReceived(std::addressof(data[rxBytesParsed]), count - rxBytesParsed);
                }
            }
        }
    }
    void IConnection::HandleUnfragmentedData(const uint8* data, const uint32 count)
    {
        DEBUG_CODE(assert(data[0] == m_receiver_preamble_0 && data[1] == m_receiver_preamble_1)); // TODO : remove? Handle?
        DEBUG_CODE(auto start = FindPreamble(data, count));
        DEBUG_CODE(assert(start.has_value()));
        DEBUG_CODE(assert(start.value() == 0));

        if (count < SizeOfHeader) // Less data RX than Header -> copy from start of header into fragment buffer.
        {
            PutIntoFragmentBuffer(std::addressof(data[0]), count);
        }
        else// More data RX than header
        {
            // Enough data is present to determine the required message size.
            sMsgHeader* header = (sMsgHeader*)(&data[0]);
            uint32 msgSize = SizeOfHeader + header->PayloadSize;
            if (count < msgSize)
            {
#if defined(__arm__)
                // No crashing for garbage received...data is parsed over, but not written to buffer.
                m_has_data_exceeding_fragment_buffer_size = m_has_data_exceeding_fragment_buffer_size || (msgSize > m_largest_message_size);
#endif
                PutIntoFragmentBuffer(std::addressof(data[0]), count);
                m_fragment_buffer_bytes_required = msgSize - count;
            }
            else
            {
                // Enough data to handle a full message ... and maybe more...
                m_msg_receiver->OnMessageReceived(std::addressof(data[0]), msgSize);
                if (count > msgSize) // Recurse
                {
                    OnDataReceived(std::addressof(data[0 + msgSize]), count - msgSize);
                }
            }
        }
    }
    void IConnection::OnDataReceived(const uint8* data, const uint32 count)
    {
        if (count == 0)
            return;

        if (m_rawdata_receiver)
        {
            m_rawdata_receiver->OnDataReceived(data, count);
        }

        if (m_msg_receiver)
        {
            // What if someone puts in chars that dont match anything? USE the max message size...clear once it get to that...
#if defined(__arm__)
            //if (m_fragment_buffer_cnt >= m_largest_message_size /*&& m_fragment_buffer_bytes_required == 0*/)
            //    ResetFragmentation();
#else
            size_t m_fragment_buffer_cnt = m_fragment_buffer.size();
#endif
            // Actual data starts at the preamble.
            const uint8* actualData  = data;
            uint32       actualCount = count;
            // Early filtering : if not processing fragmented data,
            // and the expected preamble is not found, then simply ignore the data.
            if (0 == m_fragment_buffer_cnt)
            {
                if (count == 1)
                {
                    if (data[0] != m_receiver_preamble_0)
                        return;
                }
                else if (count >= 2)
                {
                    auto start = FindPreamble(data, count);
                    if (!start.has_value())
                        return;

                    actualData = std::addressof(data[start.value()]);
                    actualCount= count - start.value();
                }
            }
            if (m_fragment_buffer_cnt > 0 || (actualCount < SizeOfHeader))
            {
                HandleFragmentedData(actualData, actualCount);
            }
            else
            {
                HandleUnfragmentedData(actualData, actualCount);
            }
        }
    }
}