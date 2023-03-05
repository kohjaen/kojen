#!/usr/bin/env python3
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
__TAG_AUTHOR__                      = '<<<AUTHOR>>>'
__TAG_GROUP__                       = '<<<GROUP>>>'
__TAG_BRIEF__                       = '<<<BRIEF>>>'
__TAG_NAMESPACE__                   = '<<<NAMESPACE>>>'
__TAG_SM_NAME__                     = '<<<STATEMACHINENAME>>>'       # As given
__TAG_SM_NAME_SMALL_CAMEL__         = '<<<stateMachineName>>>'       # camelCaps
__TAG_SM_NAME_UPPER__               = '<<<STATEMACHINENAMEUPPER>>>'  # ALL UPPER
__TAG_CLASS_NAME__                  = '<<<CLASSNAME>>>'
__TAG_PyIFGen_NAME__                = '<<<PYIFGENNAME>>>'
__TAG_ENUMERATIONS__                = '<<<ENUMS>>>'

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
__TAG_EVENT_SIGNATURE_DEF__         = "<<<EVENTSIGNATUREWITHDEFAULTS>>>"
__TAG_EVENT_MEMBERINST__            = "<<<EVENTMEMBERSINSTANTIATE>>>"
__TAG_LITE_EVENT_MEMBERINST__       = "<<<EVENTMEMBERSLITEINSTANTIATE>>>"
__TAG_EVENT_MEMBERDECL__            = "<<<EVENTMEMBERSDECLARE>>>"

__TAG_STATENAME__                   = '<<<STATENAME>>>'            # As given
__TAG_STATENAME_SMALL_CAMEL__       = '<<<stateName>>>'            # camelCaps
__TAG_NEXTSTATENAME__               = '<<<NEXTSTATENAME>>>'        # As given
__TAG_NEXTSTATENAME_SMALL_CAMEL__   = '<<<nextStateName>>>'        # camelCaps
__TAG_STATENAME_IF_NEXTSTATE__      = '<<<STATENAMEIFNEXTSTATE>>>' # As given
__TAG_STATENAME_IF_NEXTSTATE_SMALL_CAMEL__      = '<<<stateNameIfNextState>>>' # As given
__TAG_EVENTNAME__                   = '<<<EVENTNAME>>>'            # As given
__TAG_EVENTNAME_SMALL_CAMEL__       = '<<<eventName>>>'            # camelCaps
__TAG_ACTIONNAME__                  = '<<<ACTIONNAME>>>'           # As given
__TAG_ACTIONNAME_SMALL_CAMEL__      = '<<<actionName>>>'           # camelCaps
__TAG_GUARDNAME__                   = '<<<GUARDNAME>>>'            # As given
__TAG_GUARDNAME_SMALL_CAMEL__       = '<<<guardName>>>'            # camelCaps

__TAG_ABC__                         = '<<<ALPH>>>'
__TAG_123__                         = '<<<NUM>>>'
__TAG_INIT_STATE__                  = '<<<STATE_0>>>'              # As given
__TAG_INIT_STATE_SMALL_CAMEL__      = '<<<state_0>>>'              # camelCaps

__TAG_TTT_BOOST_MSM__               = '<<<TTT_BOOST_MSM>>>'
__TAG_TTT_BOOST_MSMLITE__           = '<<<TTT_BOOST_MSMLITE>>>'
__TAG_TTT_PLANT_UML__               = '<<<TTT_PLANT_UML>>>'
__TAG_TTT_BOOST_SML__               = '<<<TTT_BOOST_SML>>>'
__TAG_TTT_BOOST_SML_ENTRYEXIT__     = '<<<TTT_BOOST_SML_ENTRY_EXIT>>>'

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
    from .cgen import *
except (ModuleNotFoundError, ImportError) as e:
    from cgen import *

try:
    from LanguageCPP import LanguageCPP
except  (ModuleNotFoundError, ImportError) as e:
    from .LanguageCPP import LanguageCPP

try:
    from plant import TTToDot
except  (ModuleNotFoundError, ImportError) as e:
    from .plant import TTToDot

import re

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
        tstate  = OrderedDict() # TODO : Since py 3.7 a regular dict is guaranteed to preserve order, and is more performat.
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
                transition[__TAG_STATENAME_IF_NEXTSTATE_SMALL_CAMEL__] = camel_case_small(tableline[self.START_STATE])
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


class CStateMachineGenerator(CGenerator):

    def __init__(self, inputfiledir, outputfiledir, events_interface=None, language=None, author='Anonymous', group='', brief=''):
        CGenerator.__init__(self,inputfiledir,outputfiledir,language, author, group, brief)
        self.events_interface = events_interface
        self.vpp_filename = ""

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

        if self.language and self.events_interface:
            enums = ""
            for e in self.events_interface.Enums():
                enums += self.language.DeclareEnum(e, '\t')
            dict_to_replace_lines[__TAG_ENUMERATIONS__] = enums


        dict_to_replace_filenames = {}
        dict_to_replace_filenames["TEMPLATE_"] = smmodel.statemachinename

        return CGenerator.loadtemplates_firstfiltering(self,dict_to_replace_lines,dict_to_replace_filenames)

    def get_event_signature(self,name, with_defaults):
        if self.events_interface is None or self.language is None:
            return ""
        for s in self.events_interface.Structs():
            if s.Name == name:
                return self.language.ParameterString(self.language.GetFactoryCreateParams(s, self.events_interface, with_defaults))

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

    def innerexpand_secondfiltering(self, snippet_to_expand, alllinesexpanded, items):
        alpha = reset_alphabet()
        cnt = 0
        for name in items:
            for line in snippet_to_expand:
                newline = line
                newline = newline.replace(__TAG_STATENAME_SMALL_CAMEL__, camel_case_small(name))
                newline = newline.replace(__TAG_STATENAME__, name)
                newline = newline.replace(__TAG_EVENTNAME_SMALL_CAMEL__, camel_case_small(name))
                newline = newline.replace(__TAG_EVENTNAME__, name)
                newline = newline.replace(__TAG_ACTIONNAME__, name)
                newline = newline.replace(__TAG_ACTIONNAME_SMALL_CAMEL__, camel_case_small(name))
                newline = newline.replace(__TAG_GUARDNAME__, name)
                newline = newline.replace(__TAG_GUARDNAME_SMALL_CAMEL__, camel_case_small(name))
                newline = newline.replace(__TAG_ABC__, alpha)
                newline = newline.replace(__TAG_123__, str(cnt))
                tabcnt = newline.count('    ')
                if hasSpecificTag(newline,__TAG_EVENT_SIGNATURE__):
                    has_signature_defaults = __TAG_EVENT_SIGNATURE_DEF__ in newline
                    if hasDefault(newline):
                        # Has user params
                        user_params = extractDefaultAndTag(newline)
                        signature = self.get_event_signature(name, False) + ", " + user_params[1]
                        signature = signature.strip(',').strip(' ')
                        newline = newline.replace(user_params[0], signature)
                    else:
                        newline = newline.replace(__TAG_EVENT_SIGNATURE_DEF__ if has_signature_defaults else __TAG_EVENT_SIGNATURE__, self.get_event_signature(name, has_signature_defaults))
                    # check for brackets...remove any spurious ',' and ' '
                    newline = re.sub("\([^)]*\)", lambda x:x.group(0).replace(' , )',')').replace(', )',')').replace(',)',')').replace('( , ','(').replace('( ,','(').replace('(,','('), newline)
                # __TAG_EVENT_MEMBERINST__ -> PTR
                if hasSpecificTag(newline,__TAG_EVENT_MEMBERINST__) and hasDefault(newline):
                    line_member = extractDefaultAndTag(newline)
                    newline = newline.replace(line_member[0],self.instantiate_event_struct_member(name, tabcnt, True, line_member[1]))
                else:
                    newline = newline.replace(__TAG_EVENT_MEMBERINST__, self.instantiate_event_struct_member(name, tabcnt, True))        # PTR
                # __TAG_LITE_EVENT_MEMBERINST__ -> NO PTR
                if hasSpecificTag(newline,__TAG_LITE_EVENT_MEMBERINST__) and hasDefault(newline):
                    line_member = extractDefaultAndTag(newline)
                    newline = newline.replace(line_member[0],self.instantiate_event_struct_member(name, tabcnt, False, line_member[1]))
                else:
                    newline = newline.replace(__TAG_LITE_EVENT_MEMBERINST__, self.instantiate_event_struct_member(name, tabcnt, False))  # NO PTR
                newline = newline.replace(__TAG_EVENT_MEMBERDECL__, self.declare_event_struct_members(name, tabcnt))
                if newline == '\n' or newline == '' or newline == '\r\n' or newline.replace(' ','') == "" or newline.replace(' ','').replace('\n','').replace('\r','') == "":
                    continue
                alllinesexpanded.append(newline)
            cnt = cnt + 1
            alpha = get_next_alphabet()

    def innerexpand_actionsignatures(self, snippet_to_expand, alllinesexpanded, states):
        alpha = reset_alphabet()
        cnt = 0
        for key, (actionname, eventname) in states.items():
            if eventname == "" or eventname.lower() == 'none':
                eventname = "NONE"
            elif eventname.lower() == 'any':
                eventname = "ANY"
            for line in snippet_to_expand:
                alllinesexpanded.append(line
                            .replace(__TAG_ACTIONNAME_SMALL_CAMEL__, camel_case_small(actionname))
                            .replace(__TAG_ACTIONNAME__, actionname)
                            .replace(__TAG_EVENTNAME_SMALL_CAMEL__, camel_case_small(eventname))
                            .replace(__TAG_EVENTNAME__, eventname)
                            .replace(__TAG_ABC__, alpha)
                            .replace(__TAG_123__, str(cnt)))
            cnt = cnt + 1
            alpha = get_next_alphabet()

    def innerexpand_msm(self, output, whitespace, smmodel):
        len_tt = len(smmodel.transition_table)
        tt_out = whitespace + "// " + len("msmf::Row < ") * ' ' + even_space("Start") + even_space("Event") + even_space("Next") + even_space("Action") + even_space("Guard") + '\n'
        for i, ttline in enumerate(smmodel.transition_table):
            tt_out += whitespace + 'msmf::Row < '
            tt_out += even_space(self.transitiontable_replace_NONE(ttline[smmodel.START_STATE])) + ','
            tt_out += even_space(self.transitiontable_replace_NONE(ttline[smmodel.EVENT])) + ','
            tt_out += even_space(self.transitiontable_replace_NONE(ttline[smmodel.NEXT_STATE])) + ','
            tt_out += even_space(self.transitiontable_replace_NONE(ttline[smmodel.ACTION])) + ','
            tt_out += even_space(self.transitiontable_replace_NONE(ttline[smmodel.GUARD])) + '>    '
            if i != len_tt - 1:
                tt_out += ","
            tt_out += "    // " + str(i) + '\n'
            output.append(tt_out)
            tt_out = ""

    def innerexpand_msmlite(self, output, whitespace, smmodel):
        tt_out = whitespace + "// " + even_space("Start + ") + even_space("Event") + even_space("[ Guard ] ") + even_space("/ Action") + even_space(" = Next") + '\n'
        startStateHasEntryExit = {}
        for i, ttline in enumerate(smmodel.transition_table):
            if i == 0:  # initial state
                tt_out += whitespace + " *"
            else:
                tt_out += whitespace + ", "
            tt_out += even_space(self.transitiontable_replace_NONE(ttline[smmodel.START_STATE])) + '+'
            tt_out += even_space('event<' + self.transitiontable_replace_NONE(ttline[smmodel.EVENT]) + ">") + ' '
            tt_out += even_space('[' + self.transitiontableLITE_guard_replace_NONE('__' + ttline[smmodel.GUARD]) + ']') + ' / '
            tt_out += even_space(self.transitiontableLITE_action_replace_NONE('__' + ttline[smmodel.ACTION]))
            if ttline[smmodel.NEXT_STATE].lower() != 'none':  # to not get transitions into/outof state on actions that dont change the state...
                tt_out += ' = ' + even_space(self.transitiontableLITE_nextstate_replace_NONE(ttline[smmodel.NEXT_STATE], ttline[smmodel.START_STATE]))
            tt_out = tt_out.rstrip()
            tt_out += '\n'
            output.append(tt_out)
            tt_out = ""
            # State entry/exit, once only
            if not (ttline[smmodel.START_STATE] in startStateHasEntryExit):
                startStateHasEntryExit[ttline[smmodel.START_STATE]] = True
                tt_out += whitespace + ", " + ttline[smmodel.START_STATE] + " + msm::on_entry / __" + ttline[smmodel.START_STATE] + 'OnEntry\n'
                tt_out += whitespace + ", " + ttline[smmodel.START_STATE] + " + msm::on_exit / __" + ttline[smmodel.START_STATE] + 'OnExit'
                tt_out = tt_out.rstrip()
                tt_out += '\n'
                output.append(tt_out)
                tt_out = ""

    def innerexpand_plant(self, output, whitespace, smmodel):
        lines = TTToDot(smmodel.transition_table)
        for l in lines:
            output.append(whitespace + l + "\n")

    def innerexpand_sml(self, output, whitespace, smmodel, sml_entry_exit):
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
            output.append(tt_out)
            tt_out = ""
            # State entry/exit, once only
            if not (ttline[smmodel.START_STATE] in startStateHasEntryExit) and sml_entry_exit:
                startStateHasEntryExit[ttline[smmodel.START_STATE]] = True
                tt_out += whitespace + ", state<" + ttline[smmodel.START_STATE] + "> + boost::sml::on_entry<_> / " + camel_case_small(ttline[smmodel.START_STATE]) + 'OnEntry\n'
                tt_out += whitespace + ", state<" + ttline[smmodel.START_STATE] + "> + boost::sml::on_exit<_> / " + camel_case_small(ttline[smmodel.START_STATE]) + 'OnExit'
                tt_out = tt_out.rstrip()
                tt_out += '\n'
                output.append(tt_out)
                tt_out = ""

    def filterInitialState(self, all_lines, smmodel):
        output = []
        for l in all_lines:
            output.append(l.replace(__TAG_INIT_STATE__, smmodel.getfirststate()).replace(__TAG_INIT_STATE_SMALL_CAMEL__, camel_case_small(smmodel.getfirststate())))
        return output


    def filterStateName(self, lines, stateName):
        result = []
        for l in lines:
            result.append(l.replace(__TAG_STATENAME__, stateName).replace(__TAG_STATENAME_SMALL_CAMEL__, camel_case_small(stateName)))
        return result


    def filterEventName(self, lines, eventName):
        result = []
        for l in lines:
            result.append(l.replace(__TAG_EVENTNAME__, eventName).replace(__TAG_EVENTNAME_SMALL_CAMEL__, camel_case_small(eventName)))
        return result


    def innerexpand_transitionsperstate(self, snippet_to_expand, all_lines_expanded, transitionperstate):

        def __expansion(to_expand, output, object, state, transition_dict):
            for ev, transitionList in transition_dict.items():
                # guard/action/next state repeats
                object.innerexpand_transitionsperguard(to_expand, output, ev, state, transitionList)

        for state, transition_dict in transitionperstate.items():
            all_lines_snippet = self.filterStateName(snippet_to_expand, state)
            all_lines_snippet = PairExpander(__TAG_PET_BEGIN__, __TAG_PET_END__).Expand(all_lines_snippet, __expansion, self, state, transition_dict)
            all_lines_expanded.extend(all_lines_snippet)


    def innerexpand_transitionsperguard(self, snippet_to_expand, all_lines_expanded, eventName, stateName, transitionList):

        def __expansion(to_expand, output, transitionList):
            for transitionDict in transitionList:
                for l in to_expand:
                    for k, v in transitionDict.items():
                        # for those that are present but who have alternate text when not present.
                        if hasSpecificTag(l, k):
                            l = removeDefault(l)
                        l = l.replace(k, v)
                    # l = l.replace(__TAG_EVENTNAME__, eventName)
                    # l = l.replace(__TAG_EVENTNAME_SMALL_CAMEL__, camel_case_small(eventName))
                    # If there is no guard, or no next state, or no action, just remove it (or replace it with the alternative text). Leave no hanging code.
                    if hasSpecificTag(l, __TAG_GUARDNAME_SMALL_CAMEL__) or hasSpecificTag(l, __TAG_GUARDNAME__) or hasSpecificTag(l, __TAG_NEXTSTATENAME__) or hasSpecificTag(l, __TAG_ACTIONNAME__) or hasSpecificTag(l, __TAG_STATENAME_IF_NEXTSTATE__) or hasSpecificTag(l, __TAG_STATENAME_IF_NEXTSTATE_SMALL_CAMEL__):
                        line_member = extractDefaultAndTag(l)
                        if line_member[1]:  # alternative text is embedded in the tag.
                            whitespace = len(l) - len(l.lstrip())
                            output.append(whitespace * ' ' + line_member[1] + '\n')
                    elif l.find(__TAG_GUARDNAME_SMALL_CAMEL__) == -1 and l.find(__TAG_GUARDNAME__) == -1 and l.find(__TAG_NEXTSTATENAME__) == -1 and l.find(__TAG_STATENAME_IF_NEXTSTATE__) == -1 and l.find(__TAG_STATENAME_IF_NEXTSTATE_SMALL_CAMEL__) == -1:
                        output.append(l)

        all_lines_snippet = self.filterEventName(snippet_to_expand, eventName)
        all_lines_snippet = PairExpander(__TAG_PGT_BEGIN__, __TAG_PGT_END__).Expand(all_lines_snippet, __expansion, transitionList)
        all_lines_expanded.extend(all_lines_snippet)

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
            all_lines_expanded = self.filterInitialState(cmmodel.filenames_to_lines[file], smmodel)
            all_lines_expanded = SingleExpander(__TAG_TTT_PLANT_UML__).Expand(all_lines_expanded, self.innerexpand_plant, smmodel)
            all_lines_expanded = SingleExpander(__TAG_TTT_BOOST_MSM__).Expand(all_lines_expanded, self.innerexpand_msm, smmodel)
            all_lines_expanded = SingleExpander(__TAG_TTT_BOOST_MSMLITE__).Expand(all_lines_expanded, self.innerexpand_msmlite, smmodel)
            all_lines_expanded = SingleExpander(__TAG_TTT_BOOST_SML_ENTRYEXIT__).Expand(all_lines_expanded, self.innerexpand_sml, smmodel, True)
            all_lines_expanded = SingleExpander(__TAG_TTT_BOOST_SML__).Expand(all_lines_expanded, self.innerexpand_sml, smmodel, False)
            all_lines_expanded = PairExpander(__TAG_PS_BEGIN__, __TAG_PS_END__).Expand(all_lines_expanded, self.innerexpand_secondfiltering, smmodel.states)
            all_lines_expanded = PairExpander(__TAG_PE_BEGIN__, __TAG_PE_END__).Expand(all_lines_expanded, self.innerexpand_secondfiltering, smmodel.events)
            all_lines_expanded = PairExpander(__TAG_PA_BEGIN__, __TAG_PA_END__).Expand(all_lines_expanded, self.innerexpand_secondfiltering, smmodel.actions)
            all_lines_expanded = PairExpander(__TAG_PASIG_BEGIN__, __TAG_PASIG_END__).Expand(all_lines_expanded, self.innerexpand_actionsignatures, smmodel.actionsignatures)
            all_lines_expanded = PairExpander(__TAG_PST_BEGIN__, __TAG_PST_END__).Expand(all_lines_expanded, self.innerexpand_transitionsperstate, smmodel.transitionsperstate)
            all_lines_expanded = PairExpander(__TAG_PG_BEGIN__, __TAG_PG_END__).Expand(all_lines_expanded, self.innerexpand_secondfiltering, smmodel.guards)
            cmmodel.filenames_to_lines[file] = all_lines_expanded

    ''' Used for State Machine Generation
    '''
    def Generate(self, transitiontable, namespacenname, statemachinename, dclspc="", copyotherfiles = True) -> list:

        print("*************************************")
        print("******* SMGen ***********************")
        print("*************************************")
        print(" Output Dir   : " + self.output_gen_file_dir)
        print(" State Machine: " + statemachinename)
        print(" Executing in : " + os.path.realpath(__file__))
        print("*************************************")

        sm = CTransitionTableModel(transitiontable, namespacenname, statemachinename, dclspc)

        for e in self.events_interface.Structs(): # only necessary for stateless (nonTT) events.
            if not e.Name in sm.events:
                sm.events.append(e.Name)

        cm = self.loadtemplates_firstfiltering(sm)
        self.expand_secondfiltering(sm, cm)

        # user tags.
        if self.events_interface != None:
            self.do_user_tags(cm, self.events_interface.UserTags())

        # For processing
        self.do_for(cm)

        # Preserve user code.
        self.preserve_usercode_in_files(cm)
        '''
        # Round-trip Code Preservation. Will load the code to preserve upon creation (if the output dir is not-empty/the same as the one in the compile path).
        preservation = Preservative(self.output_gen_file_dir)
        preservation.Emplace(cm.filenames_to_lines)
        '''
        # Write output to file.
        res = self.createoutput(cm.filenames_to_lines)

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

        return res


    ''' Used for Protocol Generation
    '''
    def GenerateProtocol(self, pythoninterfacegeneratorfilename, namespacenname, classname, dclspc="", preserve_dir="") -> list:
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

        return self.createoutput(cm.filenames_to_lines)

