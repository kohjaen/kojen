#!/usr/bin/env python3

'''
  @file
  @ingroup <<<GROUP>>>
  @brief   <<<BRIEF>>>

           This statemachine has the following transition table:

           <<<TTT_SML_BEGIN>>>
           <<<TTT_SML_END>>>

           This code is Autogenerated from '<<<PYIFGENNAME>>>' with the MIT License.
           As such, please only hand-code within 'USER' tags.

  @author  <<<AUTHOR>>>
'''

from <<<STATEMACHINENAME>>>Controller import *
import threading
import queue
from enum import Enum, unique, auto
# {{{USER_IMPORTS}}}
# {{{USER_IMPORTS}}}

## State IDs
@unique
class <<<STATEMACHINENAME>>>StateId(Enum):
    <<<PER_STATE_BEGIN>>>
    c<<<STATENAME>>> = auto()
    <<<PER_STATE_END>>>

##  <<<STATEMACHINENAME>>>StateMachine Implementation
#
class <<<STATEMACHINENAME>>>StateMachine(threading.Thread):
    ## Constructor
    # @param controller context instance of the <<<STATEMACHINENAME>>>ControllerInterface
    def __init__(self, controller):
        threading.Thread.__init__(self)
        self.context        = controller
        self.__runThreaded  = <<<StateMachineThread::1>>>
        self.__fifoQueue    = queue.Queue() # threadsafe by default.
        self.context.On<<<STATE_0>>>Entry(EventStartup())
        self.currentState = <<<STATEMACHINENAME>>>StateId.c<<<STATE_0>>>
        if self.__runThreaded:
            self.start()

    ## @brief State check
    #
    #@{
    <<<PER_STATE_BEGIN>>>
    def Is<<<STATENAME>>>(self) -> bool:
        return self.currentState == <<<STATEMACHINENAME>>>StateId.c<<<STATENAME>>>
    <<<PER_STATE_END>>>
    #@}

    ## @brief Trigger events from other threads or interrupt service routines.
    #
    #@{
    <<<PER_EVENT_BEGIN>>>
    def Trigger<<<EVENTNAME>>>(self, <<<EVENTSIGNATURE>>>) -> None:
        event = <<<EVENTNAME>>>(<<<EVENTSIGNATURE>>>)
        if self.__runThreaded:
            self.__fifoQueue.put(event)
        else:
            self.process(event)
    <<<PER_EVENT_END>>>
    #@}

    ## @brief Threading
    #
    #@{
    def run(self) -> None:
        while self.__runThreaded:
            try:
                event = self.__fifoQueue.get(block=True, timeout=5) # 5s timeout for graceful shutdown.
                self.process(event)
                self.__fifoQueue.task_done()
            except queue.Empty:
                pass

    def stop(self) -> None:
        if self.__runThreaded:
            self.__runThreaded = False
            self.__fifoQueue.join()
            self.join()
    #@}

    ## @brief State Processing
    #
    #@{
    def process(self, event) -> None:
        print("<<<STATEMACHINENAME>>>StateMachine::process ", type(event));
        <<<PER_STATETRANSITION_BEGIN>>>
        if self.currentState == <<<STATEMACHINENAME>>>StateId.c<<<STATENAME>>>:
            self.process<<<STATENAME>>>(event)
            return
        <<<PER_STATETRANSITION_END>>>

    <<<PER_STATETRANSITION_BEGIN>>>
    def process<<<STATENAME>>>(self, event) -> None:
        <<<PER_EVENTTRANSITION_BEGIN>>>
        if isinstance(event, <<<EVENTNAME>>>):
            <<<PER_GUARDTRANSITION_BEGIN>>>
            if self.context.<<<GUARDNAME>>>(event):
                self.context.On<<<STATENAMEIFNEXTSTATE>>>Exit(event)
                self.context.<<<ACTIONNAME>>>(event)
                self.context.On<<<NEXTSTATENAME>>>Entry(event)
                self.currentState = <<<STATEMACHINENAME>>>StateId.c<<<NEXTSTATENAME>>>
                return
            <<<PER_GUARDTRANSITION_END>>>
        <<<PER_EVENTTRANSITION_END>>>
        print("<<<STATEMACHINENAME>>>StateMachine no transition in state '<<<STATENAME>>>' on event ", type(event));
        self.context.NoTransition(event)

    <<<PER_STATETRANSITION_END>>>
    #@}
