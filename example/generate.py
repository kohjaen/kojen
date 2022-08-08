#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'eugene'
'''

    MIT License

    Copyright (c) 2015 Eugene Grobbelaar (email : koh.jaen@yahoo.de)

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

'''

import kojen.Generate as Generate
import os

author = "yourname@yourdomain.com"
group  = "GROUP_EXAMPLE"
brief  = "An example demonstrating code-generation abilities."
#
# Generate Protocol
#
namespacename = "ExampleIO"
classname = "CExampleIF"
declspec = ""
outputdir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "autogen")
templatedir = "" # defaults
protocolfile = os.path.join(os.path.abspath(os.path.dirname(__file__)), "example_protocol.py")
Generate.Protocol(outputdir, protocolfile, namespacename, classname, declspec, author, group, brief)

#
# Generate Statemachine (C++)
#
namespacename = "CDPlayerSM"
statemachinenameprefix = "CDPlayer"
declspec = ""
templatedir = "" # use defaults

from kojen.kojentypes import *
EventPlay = Struct('EventPlay')
EventPlay.AddType('m_track_no','uint16_t')

eventsinterface = Interface('IMyIntefaceIO')
eventsinterface.AddStruct(EventPlay)

# Optional features
#eventsinterface.AddUserTag("StateMachineThread", 0) # 0 = SM runs on caller thread, 1 = SM runs on its own thread. Default is 1.
#eventsinterface.AddUserTag("Verbose", 0) # 0 = No printouts, 1 = printouts. Default is 1.

transition_table = []
#               		  StartState    Event			         NextState	    Action		           Guard
transition_table.append(['StateStop',  'EventOpen', 			 'StateOpen',  'OnOpenDrive', 		   'None'])
transition_table.append(['StateStop',  'EventPlay', 			 'StatePlay',  'OnPlayTrack', 		   'GuardCDInside'])
transition_table.append(['StateOpen',  'EventOpen', 			 'StateStop',  'OnCloseDrive', 		   'None'])
transition_table.append(['StatePlay',  'EventPlay', 			 'StatePause', 'OnPause',     		   'None'])
transition_table.append(['StatePlay',  'EventEndOfTrack', 		 'None', 	   'OnPlayNextTrack', 	   'GuardCDHasMoreTracks'])
transition_table.append(['StatePlay',  'EventEndOfTrack', 		 'StateStop',  'OnStop', 			   'GuardCDHasNoMoreTracks'])
transition_table.append(['StatePlay',  'EventSkipNextTrack', 	 'None', 	   'OnPlayNextTrack', 	   'GuardCDHasMoreTracks'])
transition_table.append(['StatePlay',  'EventSkipPreviousTrack', 'None', 	   'OnPlayPreviousTrack',  'GuardCDHasPreviousTrack'])
transition_table.append(['StatePlay',  'EventStop', 			 'StateStop',  'OnStop', 			   'None'])
transition_table.append(['StatePause', 'EventPlay', 			 'StatePlay',  'OnPlayTrack', 		   'None'])
transition_table.append(['StatePause', 'EventAfter10Minutes', 	 'StateStop',  'OnStop', 			   'None'])

Generate.StateMachine(outputdir, transition_table, eventsinterface, namespacename, statemachinenameprefix, declspec, author, group, brief, templatedir)

#
# Generate Statemachine (C#)
#
EventPlay = Struct('EventPlay')
EventPlay.AddType('trackNo','ushort','1')

eventsinterface = Interface('IMyIntefaceIO')
eventsinterface.AddStruct(EventPlay)

Generate.StateMachine_CSHARP(outputdir + "_cs", transition_table, eventsinterface, namespacename, statemachinenameprefix, declspec, author, group, brief, templatedir)

#
# Generate Statemachine (Python)
#
Generate.StateMachine_PYTHON(outputdir + "_py", transition_table, eventsinterface, namespacename, statemachinenameprefix, declspec, author, group, brief, templatedir)

#
# UML (C++/C# ... to do it directly from a model, please write to koh.jaen@yahoo.de)
#