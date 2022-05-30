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

'''
Step 1) Load template files to memory
Step 2) Search and replace these tags in memory (including filenames).

<<<NAMESPACE>>>
<<<STATEMACHINENAME>>> or <<<CLASSNAME>>>
<<<AUTHOR>>>

Step 3) Search for the following pairs of tags

<<<PER_STATE_BEGIN>>>
<<<PER_STATE_END>>>

<<<PER_EVENT_BEGIN>>>
<<<PER_EVENT_END>>>

<<<PER_ACTION_BEGIN>>>
<<<PER_ACTION_END>>>
<<<PER_ACTION_SIGNATURE_BEGIN>>>
<<<PER_ACTION_SIGNATURE_END>>>

<<<PER_GUARD_BEGIN>>>
<<<PER_GUARD_END>>>

and duplicate the following for each item, replacing each tag with the item name

<<<STATENAME>>>
<<<EVENTNAME>>>
<<<ACTIONNAME>>>
<<<GUARDNAME>>>

These need to be expanded for event structs

<<<EVENTSIGNATURE>>>
<<<EVENTMEMBERSINSTANTIATE>>>
<<<EVENTMEMBERSDECLARE>>>

When looping <<<ALPH>>> should increment from a through Z.
When looping <<<NUM>>> should increment from 1 through 10000.
When reading the transition table, first state name (top, left) should be set to the value for this tag : <<<STATE_0>>>

Then, the transition table needs to go here, following the rules.
<<<TTT_BEGIN>>>
<<<TTT_END>>>

or

<<<TTT_LITE_BEGIN>>>
<<<TTT_LITE_END>>>

or

<<<TTT_LITE_SML_BEGIN>>>
<<<TTT_LITE_SML_END>>>
'''
__TAG_AUTHOR__                      = '<<<AUTHOR>>>'
__TAG_GROUP__                       = '<<<GROUP>>>'
__TAG_BRIEF__                       = '<<<BRIEF>>>'
__TAG_NAMESPACE__                   = '<<<NAMESPACE>>>'
__TAG_SM_NAME__                     = '<<<STATEMACHINENAME>>>'       # As given
__TAG_SM_NAME_SMALL_CAMEL__         = '<<<stateMachineName>>>'       # camelCaps
__TAG_SM_NAME_UPPER__               = '<<<STATEMACHINENAMEUPPER>>>'  # ALL UPPER
__TAG_CLASS_NAME__                  = '<<<CLASSNAME>>>'
__TAG_PyIFGen_NAME__                = '<<<PYIFGENNAME>>>'

__TAG_PS_BEGIN__                    = "<<<PER_STATE_BEGIN>>>"
__TAG_PS_END__                      = "<<<PER_STATE_END>>>"

__TAG_PST_BEGIN__                   = "<<<PER_STATETRANSITION_BEGIN>>>"
__TAG_PST_END__                     = "<<<PER_STATETRANSITION_END>>>"
__TAG_PET_BEGIN__                   = "<<<PER_EVENTTRANSITION_BEGIN>>>"
__TAG_PET_END__                     = "<<<PER_EVENTTRANSITION_END>>>"
__TAG_PGT_BEGIN__                   = "<<<PER_GUARDTRANSITION_BEGIN>>>"
__TAG_PGT_END__                     = "<<<PER_GUARDTRANSITION_END>>>"

__TAG_PE_BEGIN__                    = "<<<PER_EVENT_BEGIN>>>"
__TAG_PE_END__                      = "<<<PER_EVENT_END>>>"

__TAG_PA_BEGIN__                    = "<<<PER_ACTION_BEGIN>>>"
__TAG_PA_END__                      = "<<<PER_ACTION_END>>>"

__TAG_PASIG_BEGIN__                 = "<<<PER_ACTION_SIGNATURE_BEGIN>>>"
__TAG_PASIG_END__                   = "<<<PER_ACTION_SIGNATURE_END>>>"

__TAG_PG_BEGIN__                    = "<<<PER_GUARD_BEGIN>>>"
__TAG_PG_END__                      = "<<<PER_GUARD_END>>>"

__TAG_EVENT_SIGNATURE__             = "<<<EVENTSIGNATURE>>>"
__TAG_EVENT_MEMBERINST__            = "<<<EVENTMEMBERSINSTANTIATE>>>"
__TAG_LITE_EVENT_MEMBERINST__       = "<<<EVENTMEMBERSLITEINSTANTIATE>>>"
__TAG_EVENT_MEMBERDECL__            = "<<<EVENTMEMBERSDECLARE>>>"

__TAG_STATENAME__                   = '<<<STATENAME>>>'            # As given
__TAG_STATENAME_SMALL_CAMEL__       = '<<<stateName>>>'            # camelCaps
__TAG_NEXTSTATENAME__               = '<<<NEXTSTATENAME>>>'        # As given
__TAG_NEXTSTATENAME_SMALL_CAMEL__   = '<<<nextStateName>>>'        # camelCaps
__TAG_STATENAME_IF_NEXTSTATE__      = '<<<STATENAMEIFNEXTSTATE>>>' # As given
__TAG_EVENTNAME__                   = '<<<EVENTNAME>>>'            # As given
__TAG_EVENTNAME_SMALL_CAMEL__       = '<<<eventName>>>'            # camelCaps
__TAG_ACTIONNAME__                  = '<<<ACTIONNAME>>>'           # As given
__TAG_ACTIONNAME_SMALL_CAMEL__      = '<<<actionName>>>'           # camelCaps
__TAG_GUARDNAME__                   = '<<<GUARDNAME>>>'            # As given
__TAG_GUARDNAME_SMALL_CAMEL__       = '<<<guardName>>>'            # camelCaps

__TAG_ABC__                         = '<<<ALPH>>>'
__TAG_123__                         = '<<<NUM>>>'
__TAG_INIT_STATE__                  = '<<<STATE_0>>>'

__TAG_TTT_BEGIN__                   = '<<<TTT_BEGIN>>>'
__TAG_TTT_END___                    = '<<<TTT_END>>>'

__TAG_TTT_LITE_BEGIN__              = '<<<TTT_LITE_BEGIN>>>'
__TAG_TTT_LITE_END__                = '<<<TTT_LITE_END>>>'

__TAG_TTT_SML_BEGIN__               = '<<<TTT_SML_BEGIN>>>'
__TAG_TTT_SML_BEGIN_ENTRYEXIT__     = '<<<TTT_SML_BEGIN_ENTRYEXIT>>>'
__TAG_TTT_SML_END__                 = '<<<TTT_SML_END>>>'

__TAG_DECLSPEC_DLL_EXPORT__         = "<<<DLL_EXPORT>>>"

# Python2 -> 3 shennanigans...try support both
try:
    from kojentypes import *		# py2
except (ModuleNotFoundError, ImportError) as e:
    from .kojentypes import *		# py3

try:
    from .preservative import *
except (ModuleNotFoundError, ImportError) as e:
    from preservative import *

try:
    from .cgen import CBASEGenerator, CCodeModel, alpha, __getnextalphabet__, __resetalphabet__, even_space, FileCopyUtil, caps, camel_case_small, camel_case
except (ModuleNotFoundError, ImportError) as e:
    from cgen import CBASEGenerator, CCodeModel, alpha, __getnextalphabet__, __resetalphabet__, even_space, FileCopyUtil, caps, camel_case_small, camel_case

try:
    from LanguageCPP import LanguageCPP
except  (ModuleNotFoundError, ImportError) as e:
    from .LanguageCPP import LanguageCPP

# Model that describes a state machine.
class CStateMachineModel:
    def __init__(self):
        self.statemachinename = ""
        self.namespacename    = ""
        self.declspecdllexport = ""
        self.pythoninterfacegeneratorfilename = ""
        self.states           = []
        self.actions          = []
        self.events           = []
        self.guards           = []
        self.actionsignatures = OrderedDict()
        self.transitionsperstate = OrderedDict()

# Transition Table Model uses State Machine Model to generate all code required for a working state machine.
class CTransitionTableModel(CStateMachineModel):
    START_STATE = 0
    EVENT       = 1
    NEXT_STATE  = 2
    ACTION      = 3
    GUARD       = 4

    def __init__(self, tt, nn, smn, dclspc = ""):
        CStateMachineModel.__init__(self)
        self.transition_table   = tt
        self.statemachinename   = smn
        self.namespacename      = nn
        self.declspecdllexport  = dclspc
        tstate  = OrderedDict()
        taction = OrderedDict()
        tevent  = OrderedDict()
        tguard  = OrderedDict()
        self.maxlenSTART_STATE = 0
        self.maxlenEVENT = 0
        self.maxlenACTION = 0
        self.maxlenGUARD = 0

        length = 0
        # Filter
        for tableline in self.transition_table:
            if tableline[self.START_STATE] != "" and tableline[self.START_STATE].lower() != "none":
                tstate[tableline[self.START_STATE]] = 0
                length = len(tableline[self.START_STATE])
                if self.maxlenSTART_STATE < length:
                    self.maxlenSTART_STATE = length
            if tableline[self.NEXT_STATE] != "" and tableline[self.NEXT_STATE].lower() != "none":
                tstate[tableline[self.NEXT_STATE]] = 0
            if tableline[self.EVENT] != "" and tableline[self.EVENT].lower() != "none":
                tevent[tableline[self.EVENT]] = 0
                length = len(tableline[self.EVENT])
                if self.maxlenEVENT < length:
                    self.maxlenEVENT = length
            if tableline[self.ACTION] != "" and tableline[self.ACTION].lower() != "none":
                taction[tableline[self.ACTION]] = 0
                length = len(tableline[self.ACTION])
                if self.maxlenACTION < length:
                    self.maxlenACTION = length
                if not ((tableline[self.ACTION] + tableline[self.EVENT]) in self.actionsignatures):
                    self.actionsignatures[tableline[self.ACTION] + tableline[self.EVENT]] = (tableline[self.ACTION], tableline[self.EVENT])  #, tableline[self.START_STATE],tableline[self.NEXT_STATE]))
            if tableline[self.GUARD] != "" and tableline[self.GUARD].lower() != "none":
                tguard[tableline[self.GUARD]] = 0
                length = len(tableline[self.GUARD])
                if self.maxlenGUARD < length:
                    self.maxlenGUARD = length
        # Populate CStateMachineModel
        for s in tstate:
            self.states.append(s)
        for e in tevent:
            self.events.append(e)
        for a in taction:
            self.actions.append(a)
        for g in tguard:
            self.guards.append(g)
        self.set_transitions_per_state()

    ''' Returns a dictionary of dictionaries of lists of dictionaries.
    
        {'StateName': {'EventName',[{'GuardName':'', 'ActionName':'val'},{}...]}}
        First dictionary key is the 'state'.
        Second dictionary is the 'event' name.
        These contain a list of dictionaries, as multiple of the same events can
        cause different transitions based on guards.
    '''
    def set_transitions_per_state(self):
        for tableline in self.transition_table:
            transition = OrderedDict()
            if tableline[self.ACTION] != "" and tableline[self.ACTION].lower() != "none":
                transition[__TAG_ACTIONNAME__] = tableline[self.ACTION]
                transition[__TAG_ACTIONNAME_SMALL_CAMEL__] = camel_case_small(tableline[self.ACTION])
            if tableline[self.GUARD] != "" and tableline[self.GUARD].lower() != "none":
                transition[__TAG_GUARDNAME__] = tableline[self.GUARD]
                transition[__TAG_GUARDNAME_SMALL_CAMEL__] = camel_case_small(tableline[self.GUARD])
            if tableline[self.NEXT_STATE] != "" and tableline[self.NEXT_STATE].lower() != "none":
                transition[__TAG_STATENAME_IF_NEXTSTATE__] = tableline[self.START_STATE]
                transition[__TAG_NEXTSTATENAME__] = tableline[self.NEXT_STATE]
                transition[__TAG_NEXTSTATENAME_SMALL_CAMEL__] = camel_case_small(tableline[self.NEXT_STATE])

            if tableline[self.START_STATE] != "" and tableline[self.START_STATE].lower() != "none":
                if not tableline[self.START_STATE] in self.transitionsperstate:
                    self.transitionsperstate[tableline[self.START_STATE]] = OrderedDict()

            if tableline[self.EVENT] != "" and tableline[self.EVENT].lower() != "none":
                if not tableline[self.EVENT] in self.transitionsperstate[tableline[self.START_STATE]]:
                    self.transitionsperstate[tableline[self.START_STATE]][tableline[self.EVENT]] = []
                self.transitionsperstate[tableline[self.START_STATE]][tableline[self.EVENT]].append(transition)

    def getfirststate(self):
        if not self.transition_table:
            return "NO TT PRESENT!"
        return self.transition_table[0][0]


class CStateMachineGenerator(CBASEGenerator):

    def __init__(self, inputfiledir, outputfiledir, events_interface=None, language=None, author='Anonymous', group='', brief=''):
        CBASEGenerator.__init__(self,inputfiledir,outputfiledir,language, author, group, brief)
        self.events_interface = events_interface

    def loadtemplates_firstfiltering(self, smmodel):
        """
        See baseclass implementation. This just prepares the dictionary of things to replace
        for this type of codegeneration.

        @param smmodel:
        @return: cgen.CCodeModel, a dictionary -> {filename,[lines]}
        """

        dict_to_replace_lines = {}
        dict_to_replace_lines[__TAG_SM_NAME_UPPER__] = caps(smmodel.statemachinename)
        dict_to_replace_lines[__TAG_SM_NAME_SMALL_CAMEL__] = camel_case_small(smmodel.statemachinename)
        dict_to_replace_lines[__TAG_SM_NAME__] = smmodel.statemachinename
        dict_to_replace_lines[__TAG_CLASS_NAME__] = smmodel.statemachinename
        dict_to_replace_lines[__TAG_PyIFGen_NAME__] = smmodel.pythoninterfacegeneratorfilename.replace('.py', '')  # hack : for tcpgen simple templates,
        if not dict_to_replace_lines[__TAG_PyIFGen_NAME__]:
            dict_to_replace_lines[__TAG_PyIFGen_NAME__] = self.vpp_filename
        dict_to_replace_lines[__TAG_NAMESPACE__] = smmodel.namespacename
        dict_to_replace_lines[__TAG_AUTHOR__] = self.author
        dict_to_replace_lines[__TAG_GROUP__] = self.group
        dict_to_replace_lines[__TAG_BRIEF__] = self.brief
        dict_to_replace_lines[__TAG_DECLSPEC_DLL_EXPORT__] = smmodel.declspecdllexport

        dict_to_replace_filenames = {}
        dict_to_replace_filenames["TEMPLATE_"] = smmodel.statemachinename

        return CBASEGenerator.loadtemplates_firstfiltering(self,dict_to_replace_lines,dict_to_replace_filenames)

    def get_event_signature(self,name):
        if self.events_interface is None or self.language is None:
            return ""
        for s in self.events_interface.Structs():
            if s.Name == name:
                return self.language.ParameterString(self.language.GetFactoryCreateParams(s, self.events_interface))

        return ""

    def instantiate_event_struct_member(self, name, whitespace_cnt, is_ptr=True, instancename="data"):
        if self.events_interface is None or self.language is None:
            return ""
        for s in self.events_interface.Structs():
            if s.Name == name:
                guts = self.language.InstantiateStructMembers(s, self.events_interface, '', instancename, self.language.Accessor(is_ptr))
                result = ''
                cnt = 0
                for g in guts:
                    result = result + (whitespace_cnt*'    ' if cnt > 0 else '') + g + '\n'
                    cnt = cnt + 1
                return result.rsplit('\n', 1)[0]
        return ""

    def declare_event_struct_members(self, name, whitespace_cnt):
        if self.events_interface is None or self.language is None:
            return ""

        for s in self.events_interface.Structs():
            if s.Name == name:
                guts = self.language.DeclareStructMembers(s, self.events_interface, '', False)
                result = ''
                cnt = 0
                for g in guts:
                    result = result + ((whitespace_cnt+1)*'    ' if cnt > 0 else '    ') + g + '\n'
                    cnt = cnt + 1
                return result.rsplit('\n', 1)[0]
        return ""

    def innerexpand_secondfiltering(self, names2x, lines2x, puthere):
        global alpha
        __resetalphabet__()
        cnt = 0
        for name in names2x:
            for line in lines2x:
                newline = line
                newline = newline.replace(__TAG_STATENAME_SMALL_CAMEL__, camel_case_small(name))
                newline = newline.replace(__TAG_STATENAME__, name)
                newline = newline.replace(__TAG_EVENTNAME_SMALL_CAMEL__, camel_case_small(name))
                newline = newline.replace(__TAG_EVENTNAME__, name)
                newline = newline.replace(__TAG_ACTIONNAME__, name)
                newline = newline.replace(__TAG_ACTIONNAME_SMALL_CAMEL__, camel_case_small(name))
                newline = newline.replace(__TAG_GUARDNAME__, name)
                newline = newline.replace(__TAG_GUARDNAME_SMALL_CAMEL__, camel_case_small(name))
                newline = newline.replace(__TAG_ABC__, chr(alpha))
                newline = newline.replace(__TAG_123__, str(cnt))
                tabcnt = newline.count('    ')
                newline = newline.replace(__TAG_EVENT_SIGNATURE__, self.get_event_signature(name))
                # __TAG_EVENT_MEMBERINST__ -> PTR
                if self.hasSpecificTag(newline,__TAG_EVENT_MEMBERINST__) and self.hasDefault(newline):
                    line_member = self.extractDefaultAndTag(newline)
                    newline = newline.replace(line_member[0],self.instantiate_event_struct_member(name, tabcnt, True, line_member[1]))
                else:
                    newline = newline.replace(__TAG_EVENT_MEMBERINST__, self.instantiate_event_struct_member(name, tabcnt, True))        # PTR
                # __TAG_LITE_EVENT_MEMBERINST__ -> NO PTR
                if self.hasSpecificTag(newline,__TAG_LITE_EVENT_MEMBERINST__) and self.hasDefault(newline):
                    line_member = self.extractDefaultAndTag(newline)
                    newline = newline.replace(line_member[0],self.instantiate_event_struct_member(name, tabcnt, False, line_member[1]))
                else:
                    newline = newline.replace(__TAG_LITE_EVENT_MEMBERINST__, self.instantiate_event_struct_member(name, tabcnt, False))  # NO PTR
                newline = newline.replace(__TAG_EVENT_MEMBERDECL__, self.declare_event_struct_members(name, tabcnt))
                if newline == '\n' or newline == '' or newline == '\r\n' or newline.replace(' ','') == "" or newline.replace(' ','').replace('\n','').replace('\r','') == "":
                    continue
                puthere.append(newline)
            cnt = cnt + 1
            __getnextalphabet__()

    def innerexpand_actionsignatures(self, states2x, lines2x, puthere):
        global alpha
        __resetalphabet__()
        cnt = 0
        for key, (actionname, eventname) in states2x.items():
            if eventname == "" or eventname.lower() == 'none':
                eventname = "NONE"
            elif eventname.lower() == 'any':
                eventname = "ANY"
            for line in lines2x:
                puthere.append(line
                            .replace(__TAG_ACTIONNAME_SMALL_CAMEL__, camel_case_small(actionname))
                            .replace(__TAG_ACTIONNAME__, actionname)
                            .replace(__TAG_EVENTNAME_SMALL_CAMEL__, camel_case_small(eventname))
                            .replace(__TAG_EVENTNAME__, eventname)
                            .replace(__TAG_ABC__, chr(alpha))
                            .replace(__TAG_123__, str(cnt)))
            cnt = cnt + 1
            __getnextalphabet__()

    def innerexpand_msm(self, smmodel, puthere):
        len_tt = len(smmodel.transition_table)
        tt_out = "        // " + len("msmf::Row < ") * ' ' + even_space("Start") + even_space("Event") + even_space("Next") + even_space("Action") + even_space("Guard") + '\n'
        for i, ttline in enumerate(smmodel.transition_table):
            tt_out += '        msmf::Row < '
            tt_out += even_space(self.transitiontable_replace_NONE(ttline[smmodel.START_STATE])) + ','
            tt_out += even_space(self.transitiontable_replace_NONE(ttline[smmodel.EVENT])) + ','
            tt_out += even_space(self.transitiontable_replace_NONE(ttline[smmodel.NEXT_STATE])) + ','
            tt_out += even_space(self.transitiontable_replace_NONE(ttline[smmodel.ACTION])) + ','
            tt_out += even_space(self.transitiontable_replace_NONE(ttline[smmodel.GUARD])) + '>    '
            if i != len_tt - 1:
                tt_out += ","
            tt_out += "    // " + str(i) + '\n'
            puthere.append(tt_out)
            tt_out = ""

    def innerexpand_msmlite(self, smmodel, puthere):
        tt_out = "                // " + even_space("Start + ") + even_space("Event") + even_space("[ Guard ] ") + even_space("/ Action") + even_space(" = Next") + '\n'
        startStateHasEntryExit = {}
        for i, ttline in enumerate(smmodel.transition_table):
            if i == 0:  # initial state
                tt_out += "                 *"
            else:
                tt_out += "                , "
            tt_out += even_space(self.transitiontable_replace_NONE(ttline[smmodel.START_STATE])) + '+'
            tt_out += even_space('event<' + self.transitiontable_replace_NONE(ttline[smmodel.EVENT]) + ">") + ' '
            tt_out += even_space('[' + self.transitiontableLITE_guard_replace_NONE('__' + ttline[smmodel.GUARD]) + ']') + ' / '
            tt_out += even_space(self.transitiontableLITE_action_replace_NONE('__' + ttline[smmodel.ACTION]))
            if ttline[smmodel.NEXT_STATE].lower() != 'none':  # to not get transitions into/outof state on actions that dont change the state...
                tt_out += ' = ' + even_space(self.transitiontableLITE_nextstate_replace_NONE(ttline[smmodel.NEXT_STATE], ttline[smmodel.START_STATE]))
            tt_out = tt_out.rstrip()
            tt_out += '\n'
            puthere.append(tt_out)
            tt_out = ""
            # State entry/exit, once only
            if not (ttline[smmodel.START_STATE] in startStateHasEntryExit):
                startStateHasEntryExit[ttline[smmodel.START_STATE]] = True
                tt_out += "                , " + ttline[smmodel.START_STATE] + " + msm::on_entry / __" + ttline[smmodel.START_STATE] + 'OnEntry\n'
                tt_out += "                , " + ttline[smmodel.START_STATE] + " + msm::on_exit / __" + ttline[smmodel.START_STATE] + 'OnExit'
                tt_out = tt_out.rstrip()
                tt_out += '\n'
                puthere.append(tt_out)
                tt_out = ""

    def innerexpand_sml(self, smmodel, whitespace, sml_entry_exit, puthere):
        tt_out = whitespace + "// " + even_space("Start", smmodel.maxlenSTART_STATE + 8) + even_space("+Event", smmodel.maxlenEVENT + 10) + even_space("[ Guard ]", smmodel.maxlenGUARD + 6) + even_space("/ Action", smmodel.maxlenACTION + 4) + even_space(" = Next", 0) + '\n'
        startStateHasEntryExit = {}
        for i, ttline in enumerate(smmodel.transition_table):
            if i == 0:  # initial state
                tt_out += whitespace + " *"
            else:
                tt_out += whitespace + ", "
            tt_out += even_space('state<' + self.transitiontable_replace_NONE(ttline[smmodel.START_STATE]) + '>', smmodel.maxlenSTART_STATE + 9) + '+'
            tt_out += even_space('event<' + self.transitiontable_replace_NONE(ttline[smmodel.EVENT]) + '>', smmodel.maxlenEVENT + 9) + ' '
            tt_out += even_space('[' + self.transitiontableLITE_guard_replace_NONE(camel_case_small(ttline[smmodel.GUARD])) + ']', smmodel.maxlenGUARD + 4) + ' / '
            tt_out += even_space(self.transitiontableLITE_action_replace_NONE(camel_case_small(ttline[smmodel.ACTION])), smmodel.maxlenACTION + 2)
            if ttline[smmodel.NEXT_STATE].lower() != 'none':  # to not get transitions into/outof state on actions that dont change the state...
                tt_out += ' = ' + even_space('state<' + self.transitiontableLITE_nextstate_replace_NONE(ttline[smmodel.NEXT_STATE], ttline[smmodel.START_STATE]) + '>', 0)
            tt_out = tt_out.rstrip()
            tt_out += '\n'
            puthere.append(tt_out)
            tt_out = ""
            # State entry/exit, once only
            if not (ttline[smmodel.START_STATE] in startStateHasEntryExit) and sml_entry_exit:
                startStateHasEntryExit[ttline[smmodel.START_STATE]] = True
                tt_out += whitespace + ", state<" + ttline[smmodel.START_STATE] + "> + boost::sml::on_entry<_> / " + camel_case_small(ttline[smmodel.START_STATE]) + 'OnEntry\n'
                tt_out += whitespace + ", state<" + ttline[smmodel.START_STATE] + "> + boost::sml::on_exit<_> / " + camel_case_small(ttline[smmodel.START_STATE]) + 'OnExit'
                tt_out = tt_out.rstrip()
                tt_out += '\n'
                puthere.append(tt_out)
                tt_out = ""

    def innerexpand_transitionsperstate(self, transitionperstate, lines2x, puthere):
        for state, dict in transitionperstate.items():
            ex_transition = False
            snipped_to_expand = []
            for line in lines2x:
                begin = line.find(__TAG_PET_BEGIN__) > -1
                ex_transition = begin  or ex_transition

                if ex_transition and line.find(__TAG_PET_END__) > -1:
                    # ----
                    # Should now have all the Event repeats.
                    for ev, transitionList in dict.items():
                        # guard/action/next state repeats
                        self.innerexpand_transitionsperguard(ev, state, transitionList, snipped_to_expand, puthere)
                    # ----
                    ex_transition = False

                if ex_transition:
                    if not begin:
                        snipped_to_expand.append(line)
                else:
                    if line.find(__TAG_PET_END__) == -1:
                        puthere.append(line.replace(__TAG_STATENAME__, state).replace(__TAG_STATENAME_SMALL_CAMEL__, state))

    def innerexpand_transitionsperguard(self, eventName, stateName, transitionList,lines2x, puthere):
        ex_transition = False
        snipped_to_expand = []
        for line in lines2x:
            begin = line.find(__TAG_PGT_BEGIN__) > -1
            ex_transition = begin or ex_transition
            if ex_transition and line.find(__TAG_PGT_END__) > -1:
                # Should now have all the guard/action/next repeats.
                #----
                for transitionDict in transitionList:
                    for l in snipped_to_expand:
                        for k, v in transitionDict.items():
                            # for those that are present but who have alternate text when not present.
                            if self.hasSpecificTag(l, k):
                                l = self.removeDefault(l)
                            l = l.replace(k, v)
                        l = l.replace(__TAG_EVENTNAME__, eventName)
                        l = l.replace(__TAG_EVENTNAME_SMALL_CAMEL__, camel_case_small(eventName))
                        # If there is no guard, or next state (transitions are not mandated to have either), just remove it (or replace it with the alternative text). Leave no hanging code.
                        if self.hasSpecificTag(l,__TAG_GUARDNAME__)  or self.hasSpecificTag(l, __TAG_NEXTSTATENAME__) or self.hasSpecificTag(l,__TAG_STATENAME_IF_NEXTSTATE__):
                            line_member = self.extractDefaultAndTag(l)
                            if line_member[1]: # alternative text is embedded in the tag.
                                whitespace = len(l) - len(l.lstrip())
                                puthere.append(whitespace*' ' + line_member[1] + '\n')
                        elif l.find(__TAG_GUARDNAME__) == -1 and l.find(__TAG_NEXTSTATENAME__) == -1 and l.find(__TAG_STATENAME_IF_NEXTSTATE__) == -1:
                            puthere.append(l)
                #----
                ex_transition = False
            if ex_transition:
                if not begin:
                    snipped_to_expand.append(line)
            else:
                if line.find(__TAG_PGT_END__) == -1:
                    puthere.append(line.replace(__TAG_EVENTNAME__, eventName).replace(__TAG_EVENTNAME_SMALL_CAMEL__, camel_case_small(eventName)))

    def transitiontable_replace_NONE(self, val):
        if val == "" or val.lower() == 'none':
            val = "msmf::none"
        return val

    def transitiontableLITE_guard_replace_NONE(self, val):
        tmp_val = val.replace('__', '')
        if tmp_val == "" or tmp_val.lower() == 'none':
            val = "gnone"
        return val

    def transitiontableLITE_action_replace_NONE(self, val):
        tmp_val = val.replace('__', '')
        if tmp_val == "" or tmp_val.lower() == 'none' or tmp_val.lower().find('::none<') > -1:
            val = "none"
        return val

    ''' This SM doesnt seem to allow 'none' transitions -> make it transition to the source state'''
    def transitiontableLITE_nextstate_replace_NONE(self, val, source_state):
        tmp_val = val.replace('__', '')
        tmp_val = tmp_val.replace('msmf::', '')
        if tmp_val == "" or tmp_val.lower() == 'none':
            val = source_state
        return val


    def expand_secondfiltering(self, smmodel, cmmodel):
        for file in cmmodel.filenames_to_lines:

            ex_state       = False
            ex_event       = False
            ex_action      = False
            ex_actionsig   = False
            ex_transition  = False
            ex_guard       = False
            ex_tt          = False
            ex_tt_lite     = False
            ex_tt_lite_sml = False
            sml_entry_exit = False

            snipped_to_expand = []
            alllinesexpanded = []
            for line in cmmodel.filenames_to_lines[file]:
                begin          = line.find(__TAG_PS_BEGIN__) > -1 or \
                                 line.find(__TAG_PE_BEGIN__) > -1 or \
                                 line.find(__TAG_PA_BEGIN__) > -1 or \
                                 line.find(__TAG_PASIG_BEGIN__) > -1 or \
                                 line.find(__TAG_PST_BEGIN__) > -1 or \
                                 line.find(__TAG_PG_BEGIN__) > -1 or \
                                 line.find(__TAG_TTT_BEGIN__) > -1 or \
                                 line.find(__TAG_TTT_LITE_BEGIN__) > -1 or \
                                 line.find(__TAG_TTT_SML_BEGIN__.replace(">","")) > -1

                ex_state       = line.find(__TAG_PS_BEGIN__) > -1 or ex_state
                ex_event       = line.find(__TAG_PE_BEGIN__) > -1 or ex_event
                ex_action      = line.find(__TAG_PA_BEGIN__) > -1 or ex_action
                ex_actionsig   = line.find(__TAG_PASIG_BEGIN__) > -1 or ex_actionsig
                ex_transition  = line.find(__TAG_PST_BEGIN__) > -1 or ex_transition
                ex_guard       = line.find(__TAG_PG_BEGIN__) > -1 or ex_guard
                ex_tt          = line.find(__TAG_TTT_BEGIN__) > -1 or ex_tt
                ex_tt_lite     = line.find(__TAG_TTT_LITE_BEGIN__) > -1 or ex_tt_lite
                ex_tt_lite_sml = line.find(__TAG_TTT_SML_BEGIN__.replace(">","")) > -1 or ex_tt_lite_sml
                sml_entry_exit = line.find(__TAG_TTT_SML_BEGIN_ENTRYEXIT__) > -1 or sml_entry_exit

                if not ex_state and not ex_event and not ex_action and not ex_actionsig and not ex_transition and not ex_guard and not ex_tt and not ex_tt_lite and not ex_tt_lite_sml:
                    alllinesexpanded.append(line.replace(__TAG_INIT_STATE__, smmodel.getfirststate()))

                if ex_state and line.find(__TAG_PS_END__) > -1:
                    self.innerexpand_secondfiltering(smmodel.states, snipped_to_expand, alllinesexpanded)
                    snipped_to_expand = []
                    ex_state = False
                if ex_event and line.find(__TAG_PE_END__) > -1:
                    self.innerexpand_secondfiltering(smmodel.events, snipped_to_expand, alllinesexpanded)
                    snipped_to_expand = []
                    ex_event = False
                if ex_action and line.find(__TAG_PA_END__) > -1:
                    self.innerexpand_secondfiltering(smmodel.actions, snipped_to_expand, alllinesexpanded)
                    snipped_to_expand = []
                    ex_action = False
                if ex_actionsig and line.find(__TAG_PASIG_END__) > -1:
                    self.innerexpand_actionsignatures(smmodel.actionsignatures, snipped_to_expand, alllinesexpanded)
                    snipped_to_expand = []
                    ex_actionsig = False
                if ex_transition and line.find(__TAG_PST_END__) > -1:
                    self.innerexpand_transitionsperstate(smmodel.transitionsperstate, snipped_to_expand, alllinesexpanded)
                    snipped_to_expand = []
                    ex_transition = False
                if ex_guard and line.find(__TAG_PG_END__) > -1:
                    self.innerexpand_secondfiltering(smmodel.guards, snipped_to_expand, alllinesexpanded)
                    snipped_to_expand = []
                    ex_guard = False
                if ex_tt and line.find(__TAG_TTT_END___) > -1:
                    self.innerexpand_msm(smmodel, alllinesexpanded)
                    ex_tt = False
                if ex_tt_lite and line.find(__TAG_TTT_LITE_END__) > -1:
                    self.innerexpand_msmlite(smmodel, alllinesexpanded)
                    ex_tt_lite = False
                if ex_tt_lite_sml and line.find(__TAG_TTT_SML_END__) > -1:
                    whitespace = line[0:line.find("<<<")]
                    self.innerexpand_sml(smmodel, whitespace, sml_entry_exit, alllinesexpanded)
                    ex_tt_lite_sml = False

                if (ex_state or ex_event or ex_action or ex_actionsig or ex_transition or ex_guard or ex_tt or ex_tt_lite or ex_tt_lite_sml) and not begin:
                    snipped_to_expand.append(line)

            cmmodel.filenames_to_lines[file] = alllinesexpanded

    ''' Used for State Machine Generation
    '''
    def Generate(self, transitiontable, namespacenname, statemachinename, dclspc="", copyotherfiles = True):

        print("*************************************")
        print("******* SMGen ***********************")
        print("*************************************")
        print(" Output Dir   : " + self.output_gen_file_dir)
        print(" State Machine: " + statemachinename)
        print(" Executing in : " + os.path.realpath(__file__))
        print("*************************************")

        sm = CTransitionTableModel(transitiontable, namespacenname, statemachinename, dclspc)
        cm = self.loadtemplates_firstfiltering(sm)
        self.expand_secondfiltering(sm, cm)

        # user tags.
        if self.events_interface != None:
            self.do_user_tags(cm, self.events_interface.UserTags())

        # Preserve user code.
        self.preserve_usercode_in_files(cm)
        '''
        # Round-trip Code Preservation. Will load the code to preserve upon creation (if the output dir is not-empty/the same as the one in the compile path).
        preservation = Preservative(self.output_gen_file_dir)
        preservation.Emplace(cm.filenames_to_lines)
        '''
        # Write output to file.
        self.createoutput(cm.filenames_to_lines)

        # Copy non-autogenerated required files to output.
        if isinstance(self.language, LanguageCPP) and copyotherfiles:

            # Files...
            files_to_copy = []
            files_to_copy.append("allocator.h")
            files_to_copy.append("allocator.cpp")
            files_to_copy.append("basetypes.h")
            files_to_copy.append("CMakeLists.txt")
            files_to_copy.append("Fault.h")
            files_to_copy.append("Fault.cpp")
            files_to_copy.append("stl_allocator.h")
            files_to_copy.append("thread_FreeRTOS.h")
            files_to_copy.append("thread_FreeRTOS.cpp")
            files_to_copy.append("threaded_dispatcher.h")
            files_to_copy.append("threaded_dispatcher_FreeRTOS.h")
            files_to_copy.append("threadsafe_queue.h")
            files_to_copy.append("threadsafe_queue_FreeRTOS.h")
            files_to_copy.append("waitcondition.h")
            files_to_copy.append("waitcondition.cpp")
            files_to_copy.append("xallocator.h")
            files_to_copy.append("xallocator.cpp")
            files_to_copy.append("xlist.h")
            files_to_copy.append("xmap.h")
            files_to_copy.append("xqueue.h")
            files_to_copy.append("xset.h")
            files_to_copy.append("xsstream.h")
            files_to_copy.append("xstring.h")

            allplatformsfrom = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.join("allplatforms", "CPP"))
            allplatformsto = os.path.join(os.path.abspath(self.output_gen_file_dir), "allplatforms")

            FileCopyUtil(allplatformsfrom, allplatformsto, files_to_copy)

            # Boost SML ...
            smlfrom = os.path.join(allplatformsfrom,	os.path.join("sml", os.path.join("include","boost")))
            smlto = os.path.join(allplatformsto, "boost")
            smlfiles_to_copy = []
            smlfiles_to_copy.append("sml.hpp")
            FileCopyUtil(smlfrom, smlto, smlfiles_to_copy)

            # Tests...
            testfiles_to_copy = []
            testfiles_to_copy.append("CMakeLists.txt")
            testfiles_to_copy.append("Test.ThreadingConcepts.cpp")
            testfiles_to_copy.append("test_main.cpp")

            tests_allplatformsfrom = os.path.join(allplatformsfrom, "testsuite")
            tests_allplatformsto = os.path.join(allplatformsto, "testsuite")

            FileCopyUtil(tests_allplatformsfrom, tests_allplatformsto, testfiles_to_copy)

            # Micro Unit Test Framework
            microunit_files_to_copy = []
            microunit_files_to_copy.append("minunit.h")
            microunit_files_to_copy.append("minunit.cpp")

            microunit_allplatformsfrom = os.path.join(tests_allplatformsfrom, "minunit")
            microunit_allplatformsto = os.path.join(tests_allplatformsto, "minunit")

            FileCopyUtil(microunit_allplatformsfrom, microunit_allplatformsto, microunit_files_to_copy)


    ''' Used for Protocol Generation
    '''
    def GenerateProtocol(self, pythoninterfacegeneratorfilename, namespacenname, classname, dclspc="", preserve_dir=""):
        sm = CTransitionTableModel([], namespacenname, classname, dclspc)
        sm.pythoninterfacegeneratorfilename = pythoninterfacegeneratorfilename
        cm = self.loadtemplates_firstfiltering(sm)
        self.expand_secondfiltering(sm, cm)

        # Round-trip Code Preservation. Will load the code to preserve upon creation (if the output dir is not-empty/the same as the one in the compile path).
        # TCP gen might have a different output directory (typically COG will put files into an intermediate dir, and them copy them elsewhere
        preservation = None
        if preserve_dir == "":
            preservation = Preservative(self.output_gen_file_dir)
        else:
            preservation = Preservative(preserve_dir)

        preservation.Emplace(cm.filenames_to_lines)
        # Write output to file.
        self.createoutput(cm.filenames_to_lines)

        # return the filenames
        filenames = []
        for filename in cm.filenames_to_lines.keys():
            filenames.append(filename)
        return filenames
