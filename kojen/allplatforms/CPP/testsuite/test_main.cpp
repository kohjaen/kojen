#include "minunit/minunit.h"

#ifdef __FREERTOS__

#include "basetypes.h"
#include "thread_FreeRTOS.h"
#define MAIN_THREAD_PRIORITY 3
#define MAIN_THREAD_STACK 1000

namespace {
	class CMain_thread : public XKoJen::thread
	{
	public:
		CMain_thread(char const* name, unsigned portBASE_TYPE priority, unsigned portSHORT stackDepth = configMINIMAL_STACK_SIZE)
			: XKoJen::thread(name, priority, stackDepth)
		{}
	protected:
		//CDPlayer_Test_Suite& fixture;
		virtual void Run() override
		{
			MU_RUN_ALL();
			MU_REPORT();
		}
	};
}
#ifdef __cplusplus
extern "C" {
#endif
	KOJEN_API int main_kojen(void)
	{
#if defined(__arm__) && !defined(WIN32) // arm/freertos can be defined to test embedded code on a FreeRTOS windows port
		system_init();
#endif

		// TODO : Figure out why I had to do this...
		// SYSTEM_CLOCK_SOURCE_DPLL     = 8,//GCLK_SOURCE_FDPLL,

		// In 'linker flags'
		// - set the following : -Wl,--defsym,__stack_size__=0x100 to try and reduce 'Data Memory Usage'.
		// - default is 0x2000...which we don't need, as each thread has its own stack.
		// But, depending on what happens here, before starting the scheduler...it might cause a problem.
		// 
		CMain_thread _main("MainThrd", MAIN_THREAD_PRIORITY, MAIN_THREAD_STACK);
		_main.Start();
		vTaskStartScheduler();
		while (1);
	}
#ifdef __cplusplus
}
#endif

#else

int main(int argc, char *argv[]) {
	MU_RUN_ALL();
	MU_REPORT();
	return MU_EXIT_CODE;
}

#endif