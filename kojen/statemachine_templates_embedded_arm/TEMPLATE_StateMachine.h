/**
 * @file
 * @ingroup <<<GROUP>>>
 * @brief   <<<BRIEF>>>
 *
 *          This statemachine has the following transition table:
 *
 *          <<<TTT_SML_BEGIN>>>
 *          <<<TTT_SML_END>>>
 *
 *          This code is Autogenerated from '<<<PYIFGENNAME>>>' with the MIT License.
 *          As such, please only hand-code within 'USER' tags.
 *
 * @author  <<<AUTHOR>>>
 */
#pragma once
#include "I<<<STATEMACHINENAME>>>Controller.h"
#include <memory>

#ifdef __FREERTOS__
#include "FreeRTOS.h"
#endif


#define SM_THREAD <<<StateMachineThread::1>>>
#if SM_THREAD == 1
#define THREADED
#endif

/// {{{USER_HEADER_INCLUDES}}}
/// {{{USER_HEADER_INCLUDES}}}

/// {{{USER_FORWARD_DECLARATIONS}}}
/// {{{USER_FORWARD_DECLARATIONS}}}

namespace <<<NAMESPACE>>>
{
    /// {{{USER_LOCALS}}}
    /// {{{USER_LOCALS}}}

    class <<<DLL_EXPORT>>> I<<<STATEMACHINENAME>>>StateMachine
    {
    public:
        // The memory of what is returned is NEW'd. This means that you are responsible for it.
        // Luckily a SM is created once, and lives throughout the application lifetime, so 'free' should not be necessary.
#if defined(__FREERTOS__) && defined(THREADED)
        static I<<<STATEMACHINENAME>>>StateMachine* Create(I<<<STATEMACHINENAME>>>Controller& controller, unsigned portBASE_TYPE priority, unsigned portSHORT stackDepth=configMINIMAL_STACK_SIZE);
#else
        static I<<<STATEMACHINENAME>>>StateMachine* Create(I<<<STATEMACHINENAME>>>Controller& controller);
#endif // __FREERTOS__
        virtual ~I<<<STATEMACHINENAME>>>StateMachine(){};

        // Flag check
        <<<PER_STATE_BEGIN>>>
        virtual bool Is<<<STATENAME>>>() const = 0;
        <<<PER_STATE_END>>>

        // Event triggering
        <<<PER_EVENT_BEGIN>>>
        virtual void Trigger<<<EVENTNAME>>>(<<<EVENTSIGNATURE>>>) = 0;
        <<<PER_EVENT_END>>>

        /// {{{USER_PUBLIC_MEMBERS}}}
        /// {{{USER_PUBLIC_MEMBERS}}}
    protected:
        I<<<STATEMACHINENAME>>>StateMachine(){};

        /// {{{USER_PROTECTED_MEMBERS}}}
        /// {{{USER_PROTECTED_MEMBERS}}}
    };
}