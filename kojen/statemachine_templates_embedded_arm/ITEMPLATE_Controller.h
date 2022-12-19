/**
 * @file
 * @ingroup <<<GROUP>>>
 * @brief   <<<BRIEF>>>
 *
 *          This code is Autogenerated from '<<<PYIFGENNAME>>>' with the MIT License.
 *          As such, please only hand-code within 'USER' tags.
 *
 * @author  <<<AUTHOR>>>
 */
#pragma once

#ifdef __arm__
#include <allplatforms/allocator.h>
#endif //__arm__
#include <memory>
/// {{{USER_HEADER}}}
/// {{{USER_HEADER}}}

#define VERBOSE <<<Verbose::1>>>
#if VERBOSE == 1
#define _OUT_<<<STATEMACHINENAME>>>_DISP_
#include <cstdio>
#endif

/// {{{USER_FORWARD_DECL}}}
/// {{{USER_FORWARD_DECL}}}

#define MOVE_ONLY(name)                     \
    name(const name& other) = delete;       \
    name& operator=(name& other) = delete;  \
    name(name&& other) = default;           \
    name& operator=(name&& other) = default;

namespace <<<NAMESPACE>>>
{
    /// {{{USER_LOCALS}}}
    /// {{{USER_LOCALS}}}

    /// @{ Events
    struct Event
    {
    public:
        virtual ~Event(){}
        Event(){};
        MOVE_ONLY(Event)
    protected:
        friend class C<<<STATEMACHINENAME>>>StateMachineImpl;
        //virtual void Dispatch(void* sm) = 0; -> Fails on Linx (but not Mac/Win)
        virtual void Dispatch(void* sm) {};
    };
    typedef std::unique_ptr<Event> Event_ptr;

    <<<PER_EVENT_BEGIN>>>
    struct <<<EVENTNAME>>> : public Event
    {
        <<<EVENTNAME>>>(){};
        MOVE_ONLY(<<<EVENTNAME>>>)
    <<<EVENTMEMBERSDECLARE>>>
#ifdef __arm__
    DECLARE_ALLOCATOR
#endif //__arm__
    protected:
        virtual void Dispatch(void* sm) override;
    };
    typedef std::unique_ptr<<<<EVENTNAME>>>> <<<EVENTNAME>>>_ptr;

    <<<PER_EVENT_END>>>
    /// @}

    /**
     * Controller interface.
     */
    class <<<DLL_EXPORT>>> I<<<STATEMACHINENAME>>>Controller
    {
    public:
        virtual ~I<<<STATEMACHINENAME>>>Controller(){}

        /// @{ Guards
        <<<PER_GUARD_BEGIN>>>
        virtual bool <<<GUARDNAME>>>()
        {
            /// {{{USER_<<<GUARDNAME>>>}}}
            /// {{{USER_<<<GUARDNAME>>>}}}
#ifdef _OUT_<<<STATEMACHINENAME>>>_DISP_
            printf("I<<<STATEMACHINENAME>>>Controller : Guard >> <<<GUARDNAME>>> : %s \r\n", (m_<<<GUARDNAME>>>) ? ("True") : ("False"));
#endif
            return m_<<<GUARDNAME>>>;
        }
        <<<PER_GUARD_END>>>
        /// @}

        /// @{ State Entry and Exit
        <<<PER_STATE_BEGIN>>>
        virtual void <<<STATENAME>>>_on_entry()
        {
            /// {{{USER_<<<STATENAME>>>_on_entry}}}
            /// {{{USER_<<<STATENAME>>>_on_entry}}}
#ifdef _OUT_<<<STATEMACHINENAME>>>_DISP_
            printf("I<<<STATEMACHINENAME>>>Controller : State Enter >> <<<STATENAME>>> ...\r\n");
#endif
        }

        virtual void <<<STATENAME>>>_on_exit()
        {
            /// {{{USER_<<<STATENAME>>>_on_exit}}}
            /// {{{USER_<<<STATENAME>>>_on_exit}}}
#ifdef _OUT_<<<STATEMACHINENAME>>>_DISP_
            printf("I<<<STATEMACHINENAME>>>Controller : State Exit >> <<<STATENAME>>> ...\r\n");
#endif
        }
        <<<PER_STATE_END>>>
        /// @}

        /// @{ Actions
        <<<PER_ACTION_SIGNATURE_BEGIN>>>
        virtual void <<<ACTIONNAME>>>(<<<EVENTNAME>>> const& data)
        {
            /// {{{USER_<<<ACTIONNAME>>>_<<<EVENTNAME>>>}}}
            /// {{{USER_<<<ACTIONNAME>>>_<<<EVENTNAME>>>}}}
#ifdef _OUT_<<<STATEMACHINENAME>>>_DISP_
            printf("I<<<STATEMACHINENAME>>>Controller : Action >> <<<ACTIONNAME>>> on event <<<EVENTNAME>>> ... \r\n");
#endif
        };
        <<<PER_ACTION_SIGNATURE_END>>>
        /// @}

        /// {{{USER_PUBLIC_MEMBERS}}}
        /// {{{USER_PUBLIC_MEMBERS}}}

    protected:
        I<<<STATEMACHINENAME>>>Controller()
        {
            <<<PER_GUARD_BEGIN>>>
            m_<<<GUARDNAME>>> = false;
            <<<PER_GUARD_END>>>
            /// {{{USER_CONSTRUCTOR}}}
            /// {{{USER_CONSTRUCTOR}}}
        }

        <<<PER_GUARD_BEGIN>>>
        bool m_<<<GUARDNAME>>>;
        <<<PER_GUARD_END>>>

        /// {{{USER_PROTECTED_MEMBERS}}}
        /// {{{USER_PROTECTED_MEMBERS}}}
    };
}
