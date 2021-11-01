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
/// {{{USER_PCH}}}
/// {{{USER_PCH}}}
#include "I<<<STATEMACHINENAME>>>Controller.h"
#include "<<<STATEMACHINENAME>>>StateMachine.h"
#ifdef __FREERTOS__
#include "allplatforms/threaded_dispatcher_FreeRTOS.h"
#else
#include "allplatforms/threaded_dispatcher.h"
#endif

#include <boost/sml.hpp>

/// {{{USER_INCLUDES}}}
/// {{{USER_INCLUDES}}}

// this namespace is masqueraded as 'msm' due to the SML sharing parts of codegeneration with MSM. Makes for less messy scripts. Sorry.
namespace msm = boost::sml;

namespace boost{
    namespace msm {
        auto none = [] {};
        auto gnone = []{return true;};
    }
}

namespace <<<NAMESPACE>>>
{
    using controllertype = I<<<STATEMACHINENAME>>>Controller;

    /// {{{USER_LOCALS}}}
    /// {{{USER_LOCALS}}}

    /// @{ States
    <<<PER_STATE_BEGIN>>>
    struct <<<STATENAME>>>;
    <<<PER_STATE_END>>>
    /// @}

    /**
     * s<<<STATEMACHINENAME>>>StateMachine
     */
    struct s<<<STATEMACHINENAME>>>StateMachine
    {
        /// @{ Guards
        <<<PER_GUARD_BEGIN>>>
        struct <<<GUARDNAME>>>
        {
            bool operator()(controllertype& ctrl) {
                return ctrl.<<<GUARDNAME>>>();
            }
        };
        <<<PER_GUARD_END>>>
        /// @}

        /// @{ States
        <<<PER_STATE_BEGIN>>>
        struct <<<STATENAME>>>OnEntry{
            void operator()(controllertype& ctrl) {
                ctrl.<<<STATENAME>>>_on_entry();
            }
        };
        struct <<<STATENAME>>>OnExit{
            void operator()(controllertype& ctrl) {
                ctrl.<<<STATENAME>>>_on_exit();
            }
        };
        <<<PER_STATE_END>>>
        /// @{ Actions
        <<<PER_ACTION_BEGIN>>>
        struct <<<ACTIONNAME>>>
        {
            template <class Event>
            void operator()(const Event & e, controllertype& ctrl) const {
                ctrl.<<<ACTIONNAME>>>(e);
            }
        };
        <<<PER_ACTION_END>>>
        /// @}

        auto operator()() const noexcept
        {
            using namespace msm;
            // State Entry/Exit Actions
            <<<PER_STATE_BEGIN>>>
            <<<STATENAME>>>OnEntry	<<<stateName>>>OnEntry;
            <<<STATENAME>>>OnExit	<<<stateName>>>OnExit;
            <<<PER_STATE_END>>>
            // Actions
            <<<PER_ACTION_BEGIN>>>
            <<<ACTIONNAME>>>		<<<actionName>>>;
            <<<PER_ACTION_END>>>
            // Guards
            <<<PER_GUARD_BEGIN>>>
            <<<GUARDNAME>>>			<<<guardName>>>;
            <<<PER_GUARD_END>>>
            /// Transition table
            return make_transition_table(
                <<<TTT_LITE_SML_BEGIN>>>
                <<<TTT_LITE_SML_END>>>
            );
        }
    };

    using statemachinetype = msm::sm<s<<<STATEMACHINENAME>>>StateMachine>;

    /// @{ Events (defined in I<<<STATEMACHINENAME>>>Controller.h
#ifdef __arm__
    /**
     * Event custom allocators
     */
    <<<PER_EVENT_BEGIN>>>
    IMPLEMENT_ALLOCATOR(<<<EVENTNAME>>>, 0, 0)
    <<<PER_EVENT_END>>>
#endif //__arm__
    /**
     * Double dispatch (no rtti)
     */
    <<<PER_EVENT_BEGIN>>>
    void <<<EVENTNAME>>>::Dispatch(void* sm){
        if(auto* _sm = (statemachinetype*) sm)
            _sm->process_event(*this);
    }
    <<<PER_EVENT_END>>>
    /// @}

    /**
     * C<<<STATEMACHINENAME>>>StateMachineImpl
     */
    class C<<<STATEMACHINENAME>>>StateMachineImpl
        : public I<<<STATEMACHINENAME>>>StateMachine
#ifdef THREADED
        , public XKoJen::threaded_dispatcher<Event>
#endif // THREADED
    {
    public:
#if !defined(THREADED)
        typedef std::unique_ptr<Event> ptr_type;
#endif
        virtual ~C<<<STATEMACHINENAME>>>StateMachineImpl(){};

#ifdef THREADED
    #ifdef __FREERTOS__
        explicit C<<<STATEMACHINENAME>>>StateMachineImpl(controllertype& controller, unsigned portBASE_TYPE priority, unsigned portSHORT stackDepth)
            : XKoJen::threaded_dispatcher<Event>("<<<STATEMACHINENAME>>> Dispatcher", priority, stackDepth)
            , _sm{controller}
    #else
        explicit C<<<STATEMACHINENAME>>>StateMachineImpl(controllertype& controller)
            : XKoJen::threaded_dispatcher<Event>("<<<STATEMACHINENAME>>> Dispatcher")
            , _sm{controller}
    #endif // __FREERTOS__
#else
        explicit C<<<STATEMACHINENAME>>>StateMachineImpl(controllertype& controller)
        : _sm{controller}
#endif //THREADED
        {}

        // State Query
        <<<PER_STATE_BEGIN>>>
        virtual bool Is<<<STATENAME>>>() const override {
            return _sm.is(msm::state<<<<STATENAME>>>>);
        }
        <<<PER_STATE_END>>>

        // Event triggering
        void TriggerEvent(std::unique_ptr<Event> event) {
#ifdef THREADED
            dispatch(event);
#else
            event->Dispatch((void*)&_sm);
#endif
        }
        <<<PER_EVENT_BEGIN>>>
        virtual void Trigger<<<EVENTNAME>>>(<<<EVENTSIGNATURE>>>) override {
            auto data = std::make_unique<<<<EVENTNAME>>>>(<<<EVENTNAME>>>());
            <<<EVENTMEMBERSINSTANTIATE>>>
            TriggerEvent(std::move(data));
        }
        <<<PER_EVENT_END>>>

        /// {{{USER_IMPL_PUBLIC}}}
        /// {{{USER_IMPL_PUBLIC}}}
    protected:
        statemachinetype _sm;

#ifdef THREADED
        virtual void handle_dispatch(C<<<STATEMACHINENAME>>>StateMachineImpl::ptr_type event) override {
#else
        void handle_dispatch(C<<<STATEMACHINENAME>>>StateMachineImpl::ptr_type event) {
#endif
            /// {{{USER_DISPATCH}}}
            /// {{{USER_DISPATCH}}}
            event->Dispatch((void*)&_sm);
        }
    };

    /**
     * I<<<STATEMACHINENAME>>>StateMachine
     */
#if defined(__FREERTOS__) && defined(THREADED)
    I<<<STATEMACHINENAME>>>StateMachine* I<<<STATEMACHINENAME>>>StateMachine::Create(controllertype& controller, unsigned portBASE_TYPE priority, unsigned portSHORT stackDepth) {
        auto res = new C<<<STATEMACHINENAME>>>StateMachineImpl(controller, priority, stackDepth);
        res->Start();
        return res;
    }
#else
    I<<<STATEMACHINENAME>>>StateMachine* I<<<STATEMACHINENAME>>>StateMachine::Create(controllertype& controller) {
        return new C<<<STATEMACHINENAME>>>StateMachineImpl(controller);
    }
#endif // #ifdef __FREERTOS__
}