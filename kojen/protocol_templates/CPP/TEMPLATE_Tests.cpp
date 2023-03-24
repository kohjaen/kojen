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
#include <array>
#include <variant>
#include "allplatforms/testsuite/minunit/minunit.h"
#pragma warning( disable : 4244 )

#include "<<<CLASSNAME>>>.h"
using namespace <<<NAMESPACE>>>;

/**
 * @brief Packedness Tests
 * 
 */
<<<PER_PROTOMSG_BEGIN>>>
MU_TEST(<<<PROTOMSGNAME>>>PackedNess)
{
    size_t sizeOf<<<PROTOMSGNAME>>> = sizeof(<<<PROTOMSGNAME>>>);
    size_t sizeAccumulated = 0;
    sizeAccumulated += sizeof(<<<ATTRIBUTETYPE>>>); // <<<ATTRIBUTENAME>>>
    mu_assert(sizeOf<<<PROTOMSGNAME>>> == sizeAccumulated, "ERROR : Size of <<<PROTOMSGNAME>>> does not equal the sum of its separate parts.");
}
<<<PER_PROTOMSG_END>>>

<<<PER_STRUCT_BEGIN>>>
MU_TEST(<<<STRUCTNAME>>>PackedNess)
{
    size_t sizeOf<<<STRUCTNAME>>> = sizeof(<<<STRUCTNAME>>>);
    size_t sizeAccumulated = 0;
    sizeAccumulated += sizeof(<<<ATTRIBUTETYPE>>>); // <<<ATTRIBUTENAME>>>
    mu_assert(sizeOf<<<STRUCTNAME>>> == sizeAccumulated, "ERROR : Size of <<<STRUCTNAME>>> does not equal the sum of its separate parts.");
}
<<<PER_STRUCT_END>>>

<<<PER_MSG_BEGIN>>>
MU_TEST(<<<MSGNAME>>>PackedNess)
{
    size_t sizeOf<<<MSGNAME>>> = sizeof(<<<MSGNAME>>>);
    size_t sizeAccumulated = 0;
    sizeAccumulated += sizeof(<<<ATTRIBUTETYPE>>>); // <<<ATTRIBUTENAME>>>
    mu_assert(sizeOf<<<MSGNAME>>> == sizeAccumulated, "ERROR : Size of <<<MSGNAME>>> does not equal the sum of its separate parts.");
}
<<<PER_MSG_END>>>

/**
 * @brief Payload size Tests
 * 
 */
<<<PER_MSG_BEGIN>>>
MU_TEST(<<<MSGNAME>>>PayloadSize)
{
    auto msg = Create<<<MSGNAME>>>();
    size_t sizePayload = 0;
    sizePayload += sizeof(<<<PAYLOADTYPE>>>); // <<<PAYLOADNAME>>>
    mu_assert(msg.Header.PayloadSize == sizePayload, "ERROR : Size of <<<MSGNAME>>> payload size does not equal the sum of its separate parts (less pointers to data).");
}
<<<PER_MSG_END>>>

/**
 * @brief To/From Bytestream
 * 
 */
size_t constexpr MaxSize = sizeof(std::variant<std::monostate
<<<PER_MSG_BEGIN>>>
, <<<MSGNAME>>>
<<<PER_MSG_END>>>
>);
std::array<uint8, MaxSize> buffer;

<<<PER_MSG_BEGIN>>>
MU_TEST(<<<MSGNAME>>>ByteStream)
{
    auto origin = Create<<<MSGNAME>>>();
    <<<MSGNAME>>> clone;
    auto* src = reinterpret_cast<uint8*>(&origin);
    auto* dst = reinterpret_cast<uint8*>(&clone);
    std::copy(src, src+sizeof(<<<MSGNAME>>>), buffer.begin());
    std::copy(buffer.begin(), buffer.begin()+sizeof(<<<MSGNAME>>>), dst);
    mu_assert(0 == std::memcmp(std::addressof(origin), std::addressof(clone), sizeof(<<<MSGNAME>>>)), "ERROR : Equality check for <<<MSGNAME>>> failed.");
}
<<<PER_MSG_END>>>

MU_TEST_SUITE(<<<CLASSNAME>>>ProtocolSuite)
{
    <<<PER_PROTOMSG_BEGIN>>>
    MU_RUN_TEST(<<<PROTOMSGNAME>>>PackedNess);
    <<<PER_PROTOMSG_END>>>
    <<<PER_STRUCT_BEGIN>>>
    MU_RUN_TEST(<<<STRUCTNAME>>>PackedNess);
    <<<PER_STRUCT_END>>>
    <<<PER_MSG_BEGIN>>>
    MU_RUN_TEST(<<<MSGNAME>>>PackedNess);
    MU_RUN_TEST(<<<MSGNAME>>>PayloadSize);
    MU_RUN_TEST(<<<MSGNAME>>>ByteStream);
    <<<PER_MSG_END>>>
}
