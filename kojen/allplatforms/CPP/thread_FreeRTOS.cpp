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
		: m_name{ name }, m_priority{ priority }, m_stackDepth{stackDepth}
	{
		 
	}

	bool thread::Start()
	{
		if (!m_started)
		{
			auto res = xTaskCreate(&thread::handle_dispatch_internal, (const char*)m_name, m_stackDepth, this, m_priority, &m_handle);
			m_started = (res == pdPASS);
			if (!m_started)
			{
#ifdef printf			 
				printf("ERROR : out of memory...\r\n");
#endif
			}
		}
		return m_started;
	}
	
	void thread::handle_dispatch_internal(void* parm)
	{
		auto* task = static_cast<thread*>(parm);
		task->Run();
	#if INCLUDE_vTaskDelete
		vTaskDelete(task->m_handle);
	#else
		while(1)
			vTaskDelay(portMAX_DELAY);
	#endif
	}

}

#endif
