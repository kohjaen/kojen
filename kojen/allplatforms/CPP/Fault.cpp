#include "Fault.h"
#include "basetypes.h"
#ifdef __FREERTOS__
#include <FreeRTOS.h>
#include <task.h>
#else
#include <assert.h>
#endif

//----------------------------------------------------------------------------
// FaultHandler
//----------------------------------------------------------------------------
void FaultHandler(const char* file, unsigned short line)
{
#if WIN32
	// If you hit this line, it means one of the ASSERT macros failed.
    DebugBreak();	
#endif
#ifdef __FREERTOS__
	configASSERT(0);
#else
	assert(0);
#endif
}