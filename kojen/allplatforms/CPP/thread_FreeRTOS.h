/// -----------------------------------------------------------------------------
///
/// \brief	This class wraps the FreeRTOS task into a derivable C++ class.
///			Adapted from (and thanks to) http://www.freertos.org/FreeRTOS_Support_Forum_Archive/July_2010/freertos_Is_it_possible_create_freertos_task_in_c_3778071.html
///
/// -----------------------------------------------------------------------------
#pragma once

#ifdef __FREERTOS__

#include "basetypes.h"
#include "FreeRTOS.h"
#include "task.h"

namespace XKoJen
{
    class KOJEN_API thread
    {
    public:
        thread(char const*name, unsigned portBASE_TYPE priority,	unsigned portSHORT stackDepth=configMINIMAL_STACK_SIZE);

        /** Start your thread after creation.
            Its bad practice to try and start it in the constructor because
            depending on when a thread is started (i.e. if the taskdispatcher is already running) and its a higher priority
            thread than the one creating it, the created thread could be run before its left its constructor,
            which causes a problem with the virtual function table (the derived virtual pointer does not yet exist and is NULL)
            and this makes for a fault on an embedded device which leaves one stumped.
        */
        bool Start();

        virtual ~thread();
    protected:
        TaskHandle_t m_handle;
        char const* m_name;
        unsigned portBASE_TYPE m_priority;
        unsigned portSHORT m_stackDepth;
        bool m_started = false;

        /** Override this for your thread. Executing this will delete the task.
        */
        virtual void Run() = 0;

        static void handle_dispatch_internal(void* parm);
    private:
        thread();
        thread( const thread &c );
        thread& operator=( const thread &c );
    };
}

#endif