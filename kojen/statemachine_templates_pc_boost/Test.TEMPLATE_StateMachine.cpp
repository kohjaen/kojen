/**
 * @file
 * @ingroup <<<GROUP>>>
 * @brief   <<<BRIEF>>>
 *          <<<STATEMACHINENAME>>> State Machine Test Suite. Run this in the console to manually test your state machine.
 *
 *          This code is Autogenerated from '<<<PYIFGENNAME>>>' with the MIT License.
 *          As such, please only hand-code within 'USER' tags.
 *
 * @author  <<<AUTHOR>>>
 */
#include "MultiThreading.h"
#include <boost/test/unit_test.hpp>
#include "../<<<STATEMACHINENAME>>>StateMachine.h"

/// {{{USER_HEADER_INCLUDES}}}
/// {{{USER_HEADER_INCLUDES}}}

namespace <<<NAMESPACE>>>_Test
{
    using namespace <<<NAMESPACE>>>;

    CGEN_DECL_CLASS_PTR(C<<<STATEMACHINENAME>>>ConsoleEvent);
    class C<<<STATEMACHINENAME>>>ConsoleEvent
    {
    public:
        static C<<<STATEMACHINENAME>>>ConsoleEvent_ptr Create(char e){
            C<<<STATEMACHINENAME>>>ConsoleEvent_ptr result(new C<<<STATEMACHINENAME>>>ConsoleEvent(e));
            return result;
        }
        char m_event;
    protected:
        C<<<STATEMACHINENAME>>>ConsoleEvent(char e):m_event(e){}
    };

    CGEN_DECL_CLASS_PTR(CConsole<<<STATEMACHINENAME>>>);
    class CConsole<<<STATEMACHINENAME>>> : public MultiThreading::IQueueThread<C<<<STATEMACHINENAME>>>ConsoleEvent>, public I<<<STATEMACHINENAME>>>Controller
    {
    public:
        static CConsole<<<STATEMACHINENAME>>>_ptr Create()
        {
            CConsole<<<STATEMACHINENAME>>>_ptr result(new CConsole<<<STATEMACHINENAME>>>());
            bool run_ctrlr_async = false;//true? as you wish.
            result->m_sm = I<<<STATEMACHINENAME>>>StateMachine::Create(result,run_ctrlr_async);
            return result;
        }
        void Process(C<<<STATEMACHINENAME>>>ConsoleEvent_ptr next_state)
        {
            /* Todo :
            /// {{{USER_PROCESS_INITIALIZERS}}}
            /// {{{USER_PROCESS_INITIALIZERS}}}
            switch(next_state->m_event)
            {
            <<<PER_EVENT_BEGIN>>>
            case '<<<ALPH>>>':
                m_sm->Trigger<<<EVENTNAME>>>();
                break;
            <<<PER_EVENT_END>>>
            default:
                {
                    /// {{{USER_PROCESS_SWITCH_DEFAULT}}}
                    /// {{{USER_PROCESS_SWITCH_DEFAULT}}}
                    std::cout << "State non existant. Please try again." << std::endl;
                }
                break;
            }
            */
        }
        ~CConsole<<<STATEMACHINENAME>>>()
        {
            m_sm->Interrupt();
            m_sm.reset();
        }
        I<<<STATEMACHINENAME>>>StateMachine_ptr m_sm;

        /// @{ Guards
        <<<PER_GUARD_BEGIN>>>
        virtual bool <<<GUARDNAME>>>() override
        {
            /// {{{USER_<<<GUARDNAME>>>}}}
            /// {{{USER_<<<GUARDNAME>>>}}}
            return __super::<<<GUARDNAME>>>();
        }
        <<<PER_GUARD_END>>>
        /// @}
        /// @{ State Entry and Exit Overrides
        <<<PER_STATE_BEGIN>>>
        virtual void <<<STATENAME>>>_on_entry() override
        {
            __super::<<<STATENAME>>>_on_entry();
        }
        virtual void <<<STATENAME>>>_on_exit() override
        {
            __super::<<<STATENAME>>>_on_exit();
        }
        <<<PER_STATE_END>>>
        /// @}
        /// @{ Actions Override
        <<<PER_ACTION_SIGNATURE_BEGIN>>>
        virtual void <<<ACTIONNAME>>>(<<<STATEMACHINENAME>>>Events::<<<EVENTNAME>>> const& data) override
        {
            __super::<<<ACTIONNAME>>>(data);
            /// {{{USER_<<<ACTIONNAME>>>_<<<EVENTNAME>>>}}}
            /// {{{USER_<<<ACTIONNAME>>>_<<<EVENTNAME>>>}}}
        };
        <<<PER_ACTION_SIGNATURE_END>>>
        /// @}

        /// {{{USER_PUBLIC_MEMBERS}}}
        /// {{{USER_PUBLIC_MEMBERS}}}
    protected:
        CConsole<<<STATEMACHINENAME>>>()
        {
            /// {{{USER_CConsole<<<STATEMACHINENAME>>>_CONSTRUCTOR}}}
            /// {{{USER_CConsole<<<STATEMACHINENAME>>>_CONSTRUCTOR}}}
        }
    };
}

/// {{{USER_FIXTURES}}}
/// {{{USER_FIXTURES}}}

BOOST_AUTO_TEST_SUITE(<<<NAMESPACE>>>_suite)
BOOST_AUTO_TEST_SUITE(<<<STATEMACHINENAME>>>_suite)

BOOST_AUTO_TEST_CASE(Test<<<STATEMACHINENAME>>>UI)
{
    BOOST_WARN_MESSAGE(false, ("Test<<<STATEMACHINENAME>>>UI is for UI validation of state machine. Disabling."));
    return;

    using namespace <<<NAMESPACE>>>_Test;
    CConsole<<<STATEMACHINENAME>>>_ptr m_test = CConsole<<<STATEMACHINENAME>>>::Create();
    <<<PER_EVENT_BEGIN>>>
    std::cout << "<<<ALPH>>> : send <<<EVENTNAME>>> event." << std::endl;
    <<<PER_EVENT_END>>>
    /// {{{USER_CUSTOM_EVENT_TRIGGERING}}}
    /// {{{USER_CUSTOM_EVENT_TRIGGERING}}}
    std::cout << "x : EXIT" << std::endl;
    char in;
    std::cin >> in;
    while(in != 'x')
    {
        // ASync
        //m_test->Add(C<<<STATEMACHINENAME>>>ConsoleEvent::Create(in));
        // Sync
        m_test->Process(C<<<STATEMACHINENAME>>>ConsoleEvent::Create(in));
        std::cin >> in;
    }
}

BOOST_AUTO_TEST_CASE(Test<<<STATEMACHINENAME>>>_States)
{
    using namespace <<<NAMESPACE>>>_Test;
    // This should be manually crafted to finely tune the state changes, forks etc (intricacies) of the SM
    /// {{{USER_UNIT_TEST_STATES}}}
    /// {{{USER_UNIT_TEST_STATES}}}
}

/// {{{USER_TESTS}}}
/// {{{USER_TESTS}}}

BOOST_AUTO_TEST_SUITE_END()
BOOST_AUTO_TEST_SUITE_END()