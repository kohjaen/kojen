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

#include "<<<CLASSNAME>>>.h"

namespace <<<NAMESPACE>>>
{
    /******************************************************
     * @brief Message Payload Factories
     ******************************************************/

    <<<PER_STRUCT_BEGIN>>>
    <<<STRUCTNAME>>> Create<<<STRUCTNAME>>>(<<<SIGNATURE>>>)
    {
        return <<<AGGREGATEINITIALIZATION>>>;
    }

    <<<PER_STRUCT_END>>>

     /******************************************************
     * @brief Message factories
     ******************************************************/

    <<<PER_MSG_BEGIN>>>
    <<<MSGNAME>>> Create<<<MSGNAME>>>(<<<SIGNATURE>>>)
    {
        return <<<AGGREGATEINITIALIZATION>>>;
    }

    <<<PER_MSG_END>>>

} // namespace <<<NAMESPACE>>>