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

namespace <<<NAMESPACE>>>
{
    /// <summary>
    /// E<<<STATEMACHINENAME>>>State internal enumeration.
    /// </summary>
    internal enum E<<<STATEMACHINENAME>>>State : ushort                                                                                                      
    {
    <<<PER_STATE_BEGIN>>>
        <<<STATENAME>>>,
    <<<PER_STATE_END>>>
    };
    /// <summary>
    /// <<<STATEMACHINENAME>>>State internal base class.
    /// </summary>
    internal class <<<STATEMACHINENAME>>>State
    {
        <<<PER_EVENT_BEGIN>>>
        internal virtual void Trigger<<<EVENTNAME>>>(ref <<<STATEMACHINENAME>>>Context context, /*ref*/ <<<STATEMACHINENAME>>>StateMachine sm, ref <<<EVENTNAME>>> data)
        {}
        <<<PER_EVENT_END>>>
        internal virtual void OnEntry(ref <<<STATEMACHINENAME>>>Context context)
        {}
        internal virtual void OnExit(ref <<<STATEMACHINENAME>>>Context context)
        {}
    };
    <<<PER_STATETRANSITION_BEGIN>>>
    /// <summary>
    /// <<<STATENAME>>> specific internal implementation.
    /// </summary>
    internal class <<<STATENAME>>> : <<<STATEMACHINENAME>>>State
    {
        <<<PER_EVENTTRANSITION_BEGIN>>>
        /// <summary>
        /// Overridden on Trigger<<<EVENTNAME>>> function.
        /// </summary>
        internal override void Trigger<<<EVENTNAME>>>(ref <<<STATEMACHINENAME>>>Context context, /*ref*/ <<<STATEMACHINENAME>>>StateMachine sm, ref <<<EVENTNAME>>> data)
        {
            <<<PER_GUARDTRANSITION_BEGIN>>>
            if (context.<<<GUARDNAME>>>())
            {
                sm.Exit<<<<NEXTSTATENAME>>>>(ref context);
                context.<<<ACTIONNAME>>>(ref data);
                sm.Enter<<<<NEXTSTATENAME>>>>(ref context);
                sm.estate = E<<<STATEMACHINENAME>>>State.<<<NEXTSTATENAME>>>;
                return;
            }
            <<<PER_GUARDTRANSITION_END>>>
        }
        <<<PER_EVENTTRANSITION_END>>>
        /// <summary>
        /// <<<STATENAME>>> overridden on entry action.
        /// </summary>
        internal override void OnEntry(ref <<<STATEMACHINENAME>>>Context context)
        {
            context.On<<<STATENAME>>>Entry();
        }
        /// <summary>
        /// <<<STATENAME>>> overridden on exit action.
        /// </summary>
        internal override void OnExit(ref <<<STATEMACHINENAME>>>Context context)
        {
            context.On<<<STATENAME>>>Exit();
        }
    };
    <<<PER_STATETRANSITION_END>>>

    /// <summary>
    /// <<<STATEMACHINENAME>>>StateMachine public implementation.
    /// </summary>
    public class <<<STATEMACHINENAME>>>StateMachine
    {
        public <<<STATEMACHINENAME>>>StateMachine(/*ref*/ <<<STATEMACHINENAME>>>Context context)
        {
            controller = context;
            Reset(ref controller);
        }
        internal void Reset(ref <<<STATEMACHINENAME>>>Context context)
        {
            Enter<<<<STATE_0>>>>(ref context);
            estate = E<<<STATEMACHINENAME>>>State.<<<STATE_0>>>;
        }
        <<<PER_STATE_BEGIN>>>
        /// <summary>
        /// Returns true if this statemachine is in the <<<STATENAME>>> state.
        /// </summary>
        public bool Is<<<STATENAME>>>()
        {
            return (estate == E<<<STATEMACHINENAME>>>State.<<<STATENAME>>>);
        }
        <<<PER_STATE_END>>>
        <<<PER_EVENT_BEGIN>>>
        /// <summary>
        /// Triggers the <<<EVENTNAME>>> event.
        /// </summary>
        public void Trigger<<<EVENTNAME>>>(<<<EVENTSIGNATURE>>>)
        {
            <<<EVENTNAME>>> evt = new <<<EVENTNAME>>>();
            <<<EVENTMEMBERSLITEINSTANTIATE::evt>>>
            state.Trigger<<<EVENTNAME>>>(ref controller, /*ref*/ this, ref evt);
        }
        <<<PER_EVENT_END>>>
        /// <summary>
        /// Generic function to enter the state 'StateT'.
        /// </summary>
        internal void Enter<StateT>(ref <<<STATEMACHINENAME>>>Context context) where StateT : new()  
        {
            state = new StateT() as <<<STATEMACHINENAME>>>State;
            state.OnEntry(ref context);
        }
        /// <summary>
        /// Generic function to exit the state 'StateT'.
        /// </summary>
        internal void Exit<StateT>(ref <<<STATEMACHINENAME>>>Context context)
        {
            state.OnExit(ref context);
        }
        internal <<<STATEMACHINENAME>>>Context controller;
        internal E<<<STATEMACHINENAME>>>State estate;
        internal <<<STATEMACHINENAME>>>State state;
    };
} // namespace <<<NAMESPACE>>>

