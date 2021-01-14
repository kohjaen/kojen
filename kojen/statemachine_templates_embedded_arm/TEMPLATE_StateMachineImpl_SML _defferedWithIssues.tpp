///  $Id: TEMPLATE_StateMachineImpl.tpp 726 2017-02-09 09:17:54Z eugene $
///
///
/// This code is Autogenerated. For manual changes, use the 'USER' tag pairs for preservation of manual additions between round-trips.
///
/// {{{USER_PCH}}}
/// {{{USER_PCH}}}
#include "I<<<STATEMACHINENAME>>>Controller.h"
#include "<<<STATEMACHINENAME>>>StateMachine.h"
#ifdef __arm__
#else
#include "allplatforms/threaded_dispatcher.h"
#endif

#include <boost/sml.hpp>
#include <deque>

/// {{{USER_HEADER_INCLUDES}}}
/// {{{USER_HEADER_INCLUDES}}}

/** Should you not wish to run the state machine on a threaded dispatcher,
    add '#define NO_THREAD' somewhere in the below 'USER_FORWARD_DECLARATIONS'.
*/
/// {{{USER_FORWARD_DECLARATIONS}}}
/// {{{USER_FORWARD_DECLARATIONS}}}

// this namespace is masqueraded as 'msm' due to the SML sharing parts of codegeneration with MSM. Makes for less messy scripts. Sorry.
namespace msm = boost::sml;

namespace boost{
	namespace msm {
		auto none = [] {};
		auto gnone = []{return true;};
	}
}

namespace {
	template <class R, class... Ts>
	auto call_impl(R(*f)(Ts...)) {
		return [f](Ts... args) { return f(args...); };
	}
	template <class T, class R, class... Ts>
	auto call_impl(T* self, R(T::*f)(Ts...)) {
		return [self, f](Ts... args) { return (self->*f)(args...); };
	}
	template <class T, class R, class... Ts>
	auto call_impl(const T* self, R(T::*f)(Ts...) const) {
		return [self, f](Ts... args) { return (self->*f)(args...); };
	}
	template <class T, class R, class... Ts>
	auto call_impl(const T* self, R(T::*f)(Ts...)) {
		return [self, f](Ts... args) { return (self->*f)(args...); };
	}
	/**
	* Simple wrapper to call free/member functions
	* @param args function, [optional] this
	* @return function(args...)
	*/
	auto call = [](auto... args) { return call_impl(args...); };
}

namespace <<<NAMESPACE>>>
{
	/// {{{USER_LOCALS}}}
	/// {{{USER_LOCALS}}}

#ifdef __arm__
	//// Event custom allocators //////////////////////////////
	/// @{ Events (defined in I<<<STATEMACHINENAME>>>Controller.h
	<<<PER_EVENT_BEGIN>>>
	IMPLEMENT_ALLOCATOR(<<<EVENTNAME>>>, 0, 0)
	<<<PER_EVENT_END>>>
	/// @}
#endif //__arm__

	/// @{ States
	<<<PER_STATE_BEGIN>>>
	auto <<<STATENAME>>> = msm::state<class <<<STATENAME>>>>;
	<<<PER_STATE_END>>>

	////////////////////////////////////////////////////////////
	// C<<<STATEMACHINENAME>>>StateMachine
	////////////////////////////////////////////////////////////
	#define CONCRETE C<<<STATEMACHINENAME>>>StateMachine
	struct C<<<STATEMACHINENAME>>>StateMachine
	{
		/// @{ Guards
		<<<PER_GUARD_BEGIN>>>
		struct <<<GUARDNAME>>>
		{
			bool operator() (I<<<STATEMACHINENAME>>>Controller*& controller)
			{
				if (controller)
					return controller-><<<GUARDNAME>>>();
				return false;
			}
		};
		<<<PER_GUARD_END>>>
		/// @}

		/// @{ States
		<<<PER_STATE_BEGIN>>>
		struct <<<STATENAME>>>OnEntry{
			void operator()(I<<<STATEMACHINENAME>>>Controller*& controller)
			{
				if (controller)
					controller-><<<STATENAME>>>_on_entry();
			}
		};
		struct <<<STATENAME>>>OnExit{
			void operator()(I<<<STATEMACHINENAME>>>Controller*& controller)
			{
				if (controller)
					controller-><<<STATENAME>>>_on_exit();
			}
		};
		<<<PER_STATE_END>>>
		/// @{ Actions
		<<<PER_ACTION_BEGIN>>>
		template <class Event>
		void <<<ACTIONNAME>>>(I<<<STATEMACHINENAME>>>Controller*& controller, const Event & e) const
		{
			if (controller)
				controller-><<<ACTIONNAME>>>(e);
		}
		<<<PER_ACTION_END>>>
		/// @}

		auto operator()() const noexcept
		{
			using namespace msm;
			// State Entry/Exit Actions
			<<<PER_STATE_BEGIN>>>
			<<<STATENAME>>>OnEntry	__<<<STATENAME>>>OnEntry;
			<<<STATENAME>>>OnExit	__<<<STATENAME>>>OnExit;
			<<<PER_STATE_END>>>
			// Guards
			<<<PER_GUARD_BEGIN>>>
			<<<GUARDNAME>>>			__<<<GUARDNAME>>>;
			<<<PER_GUARD_END>>>
			/// Transition table
			return make_transition_table(
				<<<TTT_LITE_SML_BEGIN>>>
				<<<TTT_LITE_SML_END>>>
				/// {{{USER_DEFERRED_EVENTS}}}
	            /// {{{USER_DEFERRED_EVENTS}}}
			);
		}
	};

	////////////////////////////////////////////////////////////
	// C<<<STATEMACHINENAME>>>StateMachineImpl
	////////////////////////////////////////////////////////////

	class C<<<STATEMACHINENAME>>>StateMachineImpl
		: public I<<<STATEMACHINENAME>>>StateMachine
#ifdef NO_THREAD
#else
#ifdef __arm__
#else
		  ,public XKoJen::threaded_dispatcher<Event>
#endif // __arm__
#endif // NO_THREAD
	{
	public:

#ifdef NO_THREAD
		typedef std::unique_ptr<Event> ptr_type;
#endif

		virtual ~C<<<STATEMACHINENAME>>>StateMachineImpl()
		{
			delete m_sm;
		};
		C<<<STATEMACHINENAME>>>StateMachineImpl(I<<<STATEMACHINENAME>>>Controller* controller)
#ifdef NO_THREAD
#else
#ifdef __arm__
#else
			: XKoJen::threaded_dispatcher<Event>("<<<STATEMACHINENAME>>> Dispatcher")
#endif // __arm__
#endif // NO_THREAD
		{
			m_sm = new msm::sm<C<<<STATEMACHINENAME>>>StateMachine, msm::defer_queue<std::deque>>(&(*controller));
		}

		<<<PER_STATE_BEGIN>>>
		virtual bool Is<<<STATENAME>>>() const override
		{
			return m_sm->is(<<<STATENAME>>>);
		}
		<<<PER_STATE_END>>>

		// Event triggering

		virtual void TriggerEvent(std::unique_ptr<Event> event) override
		{
#ifdef NO_THREAD
			handle_dispatch(std::move(event));
#else
			dispatch(event);
#endif
		}

		/*
		<<<PER_EVENT_BEGIN>>>
		virtual void Trigger<<<EVENTNAME>>>(<<<EVENTNAME>>> data) override
		{
#ifdef NO_THREAD
			m_sm->process_event(data);
#else
			dispatch(std::move(data));
#endif
		}
		virtual void Trigger<<<EVENTNAME>>>(<<<EVENTSIGNATURE>>>) override{}
		<<<PER_EVENT_END>>>
		*/

		/// {{{USER_SMIMPL_PUBLIC_MEMBERS}}}
		/// {{{USER_SMIMPL_PUBLIC_MEMBERS}}}
	protected:
		msm::sm<C<<<STATEMACHINENAME>>>StateMachine, msm::defer_queue<std::deque>> * m_sm;

#ifdef NO_THREAD
		void handle_dispatch(C<<<STATEMACHINENAME>>>StateMachineImpl::ptr_type item)
#else
		virtual void handle_dispatch(C<<<STATEMACHINENAME>>>StateMachineImpl::ptr_type item) override
#endif
		{
			/// {{{USER_DISPATCH_EVENT_PROCESSING}}}
			/// {{{USER_DISPATCH_EVENT_PROCESSING}}}
			<<<PER_EVENT_BEGIN>>>
			if (<<<EVENTNAME>>>* data = dynamic_cast<<<<EVENTNAME>>>*>(item.get())){
				m_sm->process_event(*data);
				return;
			}
			<<<PER_EVENT_END>>>
		}
	};

	////////////////////////////////////////////////////////////
	// I<<<STATEMACHINENAME>>>StateMachine
	////////////////////////////////////////////////////////////
	I<<<STATEMACHINENAME>>>StateMachine* I<<<STATEMACHINENAME>>>StateMachine::Create(I<<<STATEMACHINENAME>>>Controller* controller)
	{
		return new C<<<STATEMACHINENAME>>>StateMachineImpl(controller);
	}
}