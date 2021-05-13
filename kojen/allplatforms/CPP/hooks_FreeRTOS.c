/**

This file is part of 'KoJen'.

'KoJen' is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

'KoJen' is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with 'KoJen'.  If not, see <http://www.gnu.org/licenses/>.
For any feedback please contact the original author : koh.jaen@yahoo.de.

*/
#include <asf.h>

#ifdef __FREERTOS__

void vApplicationMallocFailedHook( void )
{
    printf("Application Malloc Failed : Grosse scheisse...");

    /* vApplicationMallocFailedHook() will only be called if
    configUSE_MALLOC_FAILED_HOOK is set to 1 in FreeRTOSConfig.h.  It is a hook
    function that will get called if a call to pvPortMalloc() fails.
    pvPortMalloc() is called internally by the kernel whenever a task, queue,
    timer or semaphore is created.  It is also called by various parts of the
    demo application.  If heap_1.c or heap_2.c are used, then the size of the
    heap available to pvPortMalloc() is defined by configTOTAL_HEAP_SIZE in
    FreeRTOSConfig.h, and the xPortGetFreeHeapSize() API function can be used
    to query the size of free heap space that remains (although it does not
    provide information on how the remaining heap might be fragmented). */
    taskDISABLE_INTERRUPTS();
    for( ;; );
}

//-----------------------------------------------------------

void vApplicationStackOverflowHook(TaskHandle_t xTask, portCHAR* pcTaskName)
{
    printf("Application Stack Overflow : Grosse scheisse...");
    taskDISABLE_INTERRUPTS();
    for( ;; );
}

void NMI_Handler()
{
for( ;; );
};


////////////////////////////////////////////////////////////////////////////
//// http://www.freertos.org/Debugging-Hard-Faults-On-Cortex-M-Microcontrollers.html
//// and code from http://support.code-red-tech.com/CodeRedWiki/DebugHardFault

/**
 * HardFaultHandler_C:
 * This is called from the HardFault_HandlerAsm with a pointer the Fault stack
 * as the parameter. We can then read the values from the stack and place them
 * into local variables for ease of reading.
 * We then read the various Fault Status and Address Registers to help decode
 * cause of the fault.
 * The function ends with a BKPT instruction to force control back into the debugger
 */
void HardFault_HandlerC(unsigned long *hardfault_args){
        volatile unsigned long stacked_r0 ;
        volatile unsigned long stacked_r1 ;
        volatile unsigned long stacked_r2 ;
        volatile unsigned long stacked_r3 ;
        volatile unsigned long stacked_r12 ;
        volatile unsigned long stacked_lr ;
        volatile unsigned long stacked_pc ;
        volatile unsigned long stacked_psr ;
        volatile unsigned long _CFSR ;
        volatile unsigned long _HFSR ;
        volatile unsigned long _DFSR ;
        volatile unsigned long _AFSR ;
        volatile unsigned long _BFAR ;
        volatile unsigned long _MMAR ;

        stacked_r0 = ((unsigned long)hardfault_args[0]) ;
        stacked_r1 = ((unsigned long)hardfault_args[1]) ;
        stacked_r2 = ((unsigned long)hardfault_args[2]) ;
        stacked_r3 = ((unsigned long)hardfault_args[3]) ;
        stacked_r12 = ((unsigned long)hardfault_args[4]) ;
        stacked_lr = ((unsigned long)hardfault_args[5]) ;
        stacked_pc = ((unsigned long)hardfault_args[6]) ; // EUGENE : Open an assembly code window in the debugger, and manually enter the address to view the assembly 
        stacked_psr = ((unsigned long)hardfault_args[7]) ;

        // Configurable Fault Status Register
        // Consists of MMSR, BFSR and UFSR
        _CFSR = (*((volatile unsigned long *)(0xE000ED28))) ;   
                                                                                        
        // Hard Fault Status Register
        _HFSR = (*((volatile unsigned long *)(0xE000ED2C))) ;

        // Debug Fault Status Register
        _DFSR = (*((volatile unsigned long *)(0xE000ED30))) ;

        // Auxiliary Fault Status Register
        _AFSR = (*((volatile unsigned long *)(0xE000ED3C))) ;

        // Read the Fault Address Registers. These may not contain valid values.
        // Check BFARVALID/MMARVALID to see if they are valid values
        // MemManage Fault Address Register
        _MMAR = (*((volatile unsigned long *)(0xE000ED34))) ;
        // Bus Fault Address Register
        _BFAR = (*((volatile unsigned long *)(0xE000ED38))) ;

        __asm("BKPT #1\n") ; // Break into the debugger

}
/**
 * HardFault_HandlerAsm:
 * Alternative Hard Fault handler to help debug the reason for a fault.
 * To use, edit the vector table to reference this function in the HardFault vector
 * This code is suitable for Cortex-M3 and Cortex-M0 cores
 */

// Use the 'naked' attribute so that C stacking is not used.
__attribute__((naked))
void HardFault_HandlerAsm(void){
        /*
         * Get the appropriate stack pointer, depending on our mode,
         * and use it as the parameter to the C handler. This function
         * will never return
         */

        __asm(  ".syntax unified\n"
                        "MOVS   R0, #4  \n"
                        "MOV    R1, LR  \n"
                        "TST    R0, R1  \n"
                        "BEQ    _MSP    \n"
                        "MRS    R0, PSP \n"
                        "B      HardFault_HandlerC      \n"
                "_MSP:  \n"
                        "MRS    R0, MSP \n"
                        "B      HardFault_HandlerC      \n"
                ".syntax divided\n") ;
}

void HardFault_Handler()
{
    //for( ;; );
#ifdef DEBUG	
    HardFault_HandlerAsm();
#else
    // Eugene : Got the following from the book about M0. However, its pretty much the same as whats in 'NVIC_SystemReset'.

    // Use DMB/DSB to wait until all outstanding
    // memory accesses are completed. Here DSB is used
    // because the next instruction is CPS.
    __DSB();
    __disable_irq();			// Disable interrupts, optional
    SCB->AIRCR = 0x05FA0004;	// System reset
    __DSB();					// Ensure completion of memory access
    while(1); // Wait until reset happen
#endif
};


#ifdef __FREERTOS_LOW_POWER_TICKLESS__

// Eugene Additions : hooks to power external stuff up/down
void vPortEnteringSleepMode();
void vPortExitingSleepMode(uint32_t clock_ticks_slept, uint32_t clock_tick_hz);

// http://yurovsky.github.io/2015/04/09/freertos-low-power-samd20/

// The clock USED for this feature
#define LOW_POWER_TICKLESS_CLOCK GCLK_GENERATOR_1
// the timer used for this feature
#define LOW_POWER_TICKLESS_TIMER TC4

/* Number of timer counts that make up one RTOS tick. */
//#define TIMER_COUNTS_ONE_TICK   ((system_gclk_gen_get_hz(LOW_POWER_TICKLESS_CLOCK)) / configTICK_RATE_HZ)
volatile uint32_t TIMER_COUNTS_ONE_TICK = 65; // 65 approximation of the above

/* The maximum number of ticks we can suppress: that is, the number of ticks that fit into our 32-bit counter. */
// #define COUNTER_VAL_32_BIT 0xFFFFFFFFUL -> 36h till next wakeup
//#define COUNTER_VAL_32_BIT 0x0004F588UL // 10s
volatile uint32_t COUNTER_VAL_32_BIT =  0xFFFFFFFFUL; //  36h till next wakeup

//#define MAX_SUPPRESSED_TICKS     (COUNTER_VAL_32_BIT / (unsigned long)TIMER_COUNTS_ONE_TICK)
volatile unsigned long MAX_SUPPRESSED_TICKS = 66076419; // approximation of above.


void ConfigureLowPowerSleepPeriod(uint32_t counter_to_sleep)
{
    TIMER_COUNTS_ONE_TICK	= ((system_gclk_gen_get_hz(LOW_POWER_TICKLESS_CLOCK)) / configTICK_RATE_HZ);
    COUNTER_VAL_32_BIT		= counter_to_sleep;
    MAX_SUPPRESSED_TICKS	= ((unsigned long)COUNTER_VAL_32_BIT / (unsigned long)TIMER_COUNTS_ONE_TICK);
}

// Timer Setup
static struct tc_module tc;
void vPortSetupTimerInterrupt(void)
{
    struct tc_config config;

    tc_get_config_defaults(&config);
    config.clock_source     = LOW_POWER_TICKLESS_CLOCK;
    config.counter_size     = TC_COUNTER_SIZE_32BIT;
    config.run_in_standby   = true;
    config.clock_prescaler  = TC_CLOCK_PRESCALER_DIV1;
    config.wave_generation  = TC_WAVE_GENERATION_MATCH_FREQ;

    enum status_code st = tc_init(&tc, LOW_POWER_TICKLESS_TIMER, &config);
    configASSERT(st == STATUS_OK);

    /* Connect to FreeRTOS tick handler */
    tc_register_callback(&tc, (tc_callback_t)xPortSysTickHandler,TC_CALLBACK_CC_CHANNEL0);
    tc_enable_callback(&tc, TC_CALLBACK_CC_CHANNEL0);

    /* Set up the counter */
    tc_set_count_value(&tc, 0);
    // *(portNVIC_SYSTICK_LOAD) = ( configCPU_CLOCK_HZ / configTICK_RATE_HZ ) - 1UL;
    tc_set_top_value(&tc, TIMER_COUNTS_ONE_TICK);// ? TIMER_RELOAD_VALUE_ONE_TICK);

    /* Start */
    tc_enable(&tc);
}

// Tick Supression
static inline void resume_system_tick(void)
{
    /* Disconnect callback */
    tc_disable_callback(&tc, TC_CALLBACK_CC_CHANNEL0);
    tc_unregister_callback(&tc, TC_CALLBACK_CC_CHANNEL0);

    /* Connect the FreeRTOS system tick callback */
    tc_register_callback(&tc, (tc_callback_t)xPortSysTickHandler,TC_CALLBACK_CC_CHANNEL0);
    tc_enable_callback(&tc, TC_CALLBACK_CC_CHANNEL0);

    /* Resume system tick, the starting count is taken from whatever
       is in the counter right now.  This lets us literally resume
       or otherwise pre-load the counter. */
    tc_set_top_value(&tc, TIMER_COUNTS_ONE_TICK);// ? TIMER_RELOAD_VALUE_ONE_TICK);
    tc_start_counter(&tc);
}

// Dummy callback to take place of xPortSysTickHandler when we are in the tick suppression (sleep) state
static void empty_cb(struct tc_module *const module_inst) { }

static inline void suppress_system_tick(TickType_t xWakeUpAfterIdleTime)
{
    /* Disconnect the system tick */
    tc_disable_callback(&tc, TC_CALLBACK_CC_CHANNEL0);
    tc_unregister_callback(&tc, TC_CALLBACK_CC_CHANNEL0);
    /* Connect the dummy callback */
    tc_register_callback(&tc, empty_cb,TC_CALLBACK_CC_CHANNEL0);
    tc_enable_callback(&tc, TC_CALLBACK_CC_CHANNEL0);
    /* Set our wakeup alarm */
    tc_set_count_value(&tc, 0);
    tc_set_top_value(&tc, (xWakeUpAfterIdleTime * TIMER_COUNTS_ONE_TICK) - 1);
    /* Start timer */
    tc_start_counter(&tc);
}

void vPortSuppressTicksAndSleep(TickType_t xExpectedIdleTime)
{
    /* Make sure the expected idle time is in range */
    if (xExpectedIdleTime > MAX_SUPPRESSED_TICKS)
        xExpectedIdleTime = MAX_SUPPRESSED_TICKS;

    /* Pause the system tick timer while we reconfigure it */
    tc_stop_counter(&tc);
    /* Save the counter value at this time so that we can use it
       for tick accounting on wakeup. */
    uint32_t last_count = tc_get_count_value(&tc);	
    /* Make sure that the overflow interrupt flag is cleared, we
       will look for an overflow on wakeup so we can't start
       with one. */
    tc.hw->COUNT32.INTFLAG.bit.OVF = 1;

    /* Enter critical section */
    portDISABLE_INTERRUPTS();
    __asm volatile("dsb");
    __asm volatile("isb");

    switch (eTaskConfirmSleepModeStatus()) 
    {
        case eAbortSleep: /* Never mind, back to system tick */
            resume_system_tick();
            break;

        /* We are going to sleep indefinitely, an interrupt will
           wake us up.  In this implementation we do not have a
           way to count how long we slept if we were to actually
           do that, so we will treat this like eStandardSleep with
           maximum sleep time instead. */
        case eNoTasksWaitingTimeout:
            xExpectedIdleTime = MAX_SUPPRESSED_TICKS;
            /* fall through... */
        /* We are going to sleep for the specified amount of time
           (via wakeup alarm) or until another interrupt wakes us
           up. */
        case eStandardSleep:
        {
#ifdef CONFIG_SLEEPMGR_ENABLE
            // From 'sleepmgr_enter_sleep'
            enum sleepmgr_mode sleep_mode;
            // Find the deepest allowable sleep mode. Some peripheral (e.g. USB) might have locked modes.
            sleep_mode = sleepmgr_get_sleep_mode();
            // Return right away if first mode (ACTIVE) is locked.
            if (sleep_mode==SLEEPMGR_ACTIVE) {
                resume_system_tick();
                break;
            }
            ////
#else
            /* Configure desired low-power state.  This is up to you and you may want to pick a state based on resume
               time versus the expected sleep time or other factors.See the ASF documentation for details about
               SYSTEM_SLEEPMODE_IDLE_2 for instance 

               If the sleepmanager is enabled, it is best to query which states have been locked.
               Some peripheral (e.g. USB) might have locked modes -> if we bypass that, it wont necessarily function.
            */
            system_set_sleepmode(SYSTEM_SLEEPMODE_STANDBY);
#endif
            /* Switch the sys tick out for a dummy, and trigger an interrupt (waking the system if no other
               interrupt occured) after so much idle time
            */
            suppress_system_tick(xExpectedIdleTime);

            vPortEnteringSleepMode();
#ifdef CONFIG_SLEEPMGR_ENABLE
            // Enter the deepest allowable sleep mode with interrupts enabled
            sleepmgr_sleep(sleep_mode);
#else
            /* Enter low power sleep mode (ie: wfi) */
            system_sleep();
#endif

            /* We just woke up.  
                    How long did we sleep for?
            */
            uint32_t sleep_count = tc_get_count_value(&tc);
            uint32_t notify_ui = sleep_count;

            /* Pause the system tick timer while we reconfigure it */
            //tc_stop_counter(&tc); // Eugene : this wasnt here...gave me random HARDFaults!

            /* A counter overflow means that we slept for at least the expected time, so we can go ahead
               and adjust the RTOS tick count by that amount right now. */
            if (tc.hw->COUNT32.INTFLAG.bit.OVF){
                vTaskStepTick(xExpectedIdleTime);
                notify_ui += xExpectedIdleTime*TIMER_COUNTS_ONE_TICK;
            }

            vPortExitingSleepMode(notify_ui,system_gclk_gen_get_hz(LOW_POWER_TICKLESS_CLOCK)); // Not, if clock prescaler is changed, this needs to be modified accordingly...

            /* We must also adjust for time left over (if any) */
            uint32_t cur_count = (last_count + sleep_count);
            vTaskStepTick(cur_count / TIMER_COUNTS_ONE_TICK);
            
            /* Resume the system tick, starting at approximately the remainder of time until the next tick (that is, what
               we could not account for above) */
            tc_set_count_value(&tc, cur_count % TIMER_COUNTS_ONE_TICK);
            resume_system_tick();
            }
            break;
    }

    /* Leave critical section */
    portENABLE_INTERRUPTS();
    __asm volatile("dsb");
    __asm volatile("isb");
}

#endif

#endif