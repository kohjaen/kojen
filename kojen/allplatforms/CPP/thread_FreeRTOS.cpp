#include "thread_FreeRTOS.h"

#ifdef __FREERTOS__

namespace XKoJen
{

	thread::thread(){}
	thread::~thread()
	{
	#if INCLUDE_vTaskDelete
		vTaskDelete(m_handle);
	#endif
	}
	thread::thread(char const*name, unsigned portBASE_TYPE priority,	unsigned portSHORT stackDepth)
	{
		 if (pdPASS != xTaskCreate(&handle_dispatch_internal, (const char*)name, stackDepth, this, priority, &m_handle))
		 {
#ifdef printf			 
			printf("ERROR : out of memory...\r\n");
#endif
		 }
	}
	
	void thread::handle_dispatch_internal(void* parm)
	{
		static_cast<thread*>(parm)->Run();
	#if INCLUDE_vTaskDelete
		vTaskDelete(static_cast<thread*>(parm)->m_handle);
	#else
		while(1)
			vTaskDelay(10000);
	#endif
	}

}

#endif
