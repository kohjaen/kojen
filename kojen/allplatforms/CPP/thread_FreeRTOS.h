/// -----------------------------------------------------------------------------
///
/// \brief	This class wraps the FreeRTOS task into a derivable C++ class.
///			Adapted from (and thanks to) http://www.freertos.org/FreeRTOS_Support_Forum_Archive/July_2010/freertos_Is_it_possible_create_freertos_task_in_c_3778071.html
///
/// -----------------------------------------------------------------------------
#pragma once

#ifdef __FREERTOS__

#include "FreeRTOS.h"
#include "task.h"

namespace XKoJen
{
	class thread
	{
	public:
		TaskHandle_t m_handle;
	
		thread(char const*name, unsigned portBASE_TYPE priority,	unsigned portSHORT stackDepth=configMINIMAL_STACK_SIZE);
		
		/** Override this for your thread. Executing this will delete the task.
		*/
		virtual void Run() = 0;
	
		virtual ~thread();
	protected:
		static void handle_dispatch_internal(void* parm);
	private:
		thread();
		thread( const thread &c );
		thread& operator=( const thread &c );
	};
}

#endif