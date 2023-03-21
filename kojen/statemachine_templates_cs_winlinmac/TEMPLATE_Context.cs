/**
 * @file
 * @ingroup <<<GROUP>>>
 * @brief   The context interface for the <<<STATEMACHINENAME>>>.
 * @detail  <<<BRIEF>>>
 *
 *          This code is Autogenerated from '<<<PYIFGENNAME>>>' with the MIT License.
 *          As such, please only hand-code within 'USER' tags.
 *
 * @author  <<<AUTHOR>>>
 */

namespace <<<NAMESPACE>>>
{
    /// <summary>
    /// Parameterizable events for <<<STATEMACHINENAME>>>.
    /// </summary>
    <<<PER_EVENT_BEGIN>>>
    public partial class <<<EVENTNAME>>> : IDispatchable {
    <<<MEMBERSDECLARE>>>
    };
    <<<PER_EVENT_END>>>

    /// <summary>
    /// Context Interface for <<<STATEMACHINENAME>>>.
    /// </summary>
    public interface I<<<STATEMACHINENAME>>>Context
    {
        <<<PER_GUARD_BEGIN>>>
        /// <summary>
        /// <<<GUARDNAME>>> guard.
        /// </summary>
        bool <<<GUARDNAME>>>();
        <<<PER_GUARD_END>>>
        <<<PER_ACTION_SIGNATURE_BEGIN>>>
        /// <summary>
        /// The <<<ACTIONNAME>>> and event parameters.
        /// </summary>
        void <<<ACTIONNAME>>>(<<<EVENTNAME>>> data);
        <<<PER_ACTION_SIGNATURE_END>>>

        /// <summary>
        /// State Entry/Exit

        <<<PER_STATE_BEGIN>>>
        /// <summary>
        /// This function is called when <<<STATENAME>>> is entered.
        /// </summary>
        void On<<<STATENAME>>>Entry();
        /// <summary>
        /// This function is called when <<<STATENAME>>> is exited.
        /// </summary>
        void On<<<STATENAME>>>Exit();

        <<<PER_STATE_END>>>
        /// </summary>
    };
} // namespace <<<NAMESPACE>>>
