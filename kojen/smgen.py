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

# EMBEDDED SM SUPPORT.
Step 4) In each <<PER_XXX tag, there might be more expansion required. The following tags apply in this pass

<<<PER_EVENT_CURRENT_NEXT_STATE_BEGIN>>>
<<<PER_EVENT_NEXT_STATE_END>>>

and the following replacement tags will be correctly set
<<<EVENTSTATECURRENT>>>
<<<EVENTSTATENEXT>>>

Also, the original SM only allows a single state-based action to happen.
I want there to be several actions allowed in a State, based on several events valid in that state.
These tags provide for that.

<<<PER_STATE_ACTION_EVENT_BEGIN>>>
<<<PER_STATE_ACTION_EVENT_END>>>

and the following replacement tags will be correctly set
<<<PER_STATE_ACTION>>>
<<<PER_STATE_EVENT>>>

# END EMBEDDED SM SUPPORT.
'''
__TAG_AUTHOR__              = '<<<AUTHOR>>>'
__TAG_GROUP__               = '<<<GROUP>>>'
__TAG_BRIEF__               = '<<<BRIEF>>>'
__TAG_NAMESPACE__           = '<<<NAMESPACE>>>'
__TAG_SM_NAME__             = '<<<STATEMACHINENAME>>>'
__TAG_CLASS_NAME__          = '<<<CLASSNAME>>>'
__TAG_PyIFGen_NAME__        = '<<<PYIFGENNAME>>>'

__TAG_PS_BEGIN__            = "<<<PER_STATE_BEGIN>>>"
__TAG_PS_END__              = "<<<PER_STATE_END>>>"

__TAG_PE_BEGIN__            = "<<<PER_EVENT_BEGIN>>>"
__TAG_PE_END__              = "<<<PER_EVENT_END>>>"

__TAG_PA_BEGIN__            = "<<<PER_ACTION_BEGIN>>>"
__TAG_PA_END__              = "<<<PER_ACTION_END>>>"

__TAG_PASIG_BEGIN__         = "<<<PER_ACTION_SIGNATURE_BEGIN>>>"
__TAG_PASIG_END__           = "<<<PER_ACTION_SIGNATURE_END>>>"

__TAG_PG_BEGIN__            = "<<<PER_GUARD_BEGIN>>>"
__TAG_PG_END__              = "<<<PER_GUARD_END>>>"

__TAG_EVENT_SIGNATURE__     = "<<<EVENTSIGNATURE>>>"
__TAG_EVENT_MEMBERINST__    = "<<<EVENTMEMBERSINSTANTIATE>>>"
__TAG_LITE_EVENT_MEMBERINST__    = "<<<EVENTMEMBERSLITEINSTANTIATE>>>"
__TAG_EVENT_MEMBERDECL__    = "<<<EVENTMEMBERSDECLARE>>>"

__TAG_STATENAME__           = '<<<STATENAME>>>'
__TAG_EVENTNAME__           = '<<<EVENTNAME>>>'
__TAG_ACTIONNAME__          = '<<<ACTIONNAME>>>'
__TAG_GUARDNAME__           = '<<<GUARDNAME>>>'

__TAG_ABC__                 = '<<<ALPH>>>'
__TAG_123__                 = '<<<NUM>>>'
__TAG_INIT_STATE__          = '<<<STATE_0>>>'

__TAG_TTT_BEGIN__           = '<<<TTT_BEGIN>>>'
__TAG_TTT_END___            = '<<<TTT_END>>>'

__TAG_TTT_LITE_BEGIN__      = '<<<TTT_LITE_BEGIN>>>'
__TAG_TTT_LITE_END__        = '<<<TTT_LITE_END>>>'

__TAG_TTT_LITE_SML_BEGIN__      = '<<<TTT_LITE_SML_BEGIN>>>'
__TAG_TTT_LITE_SML_END__        = '<<<TTT_LITE_SML_END>>>'

__TAG_DECLSPEC_DLL_EXPORT__ = "<<<DLL_EXPORT>>>"

# EMBEDDED SM SUPPORT.
__TAG_EVENT_CURNEX_ST_BEG__ = "<<<PER_EVENT_CURRENT_NEXT_STATE_BEGIN>>>"
__TAG_EVENT_CURNEX_ST_END__ = "<<<PER_EVENT_NEXT_STATE_END>>>"
__TAG_EVENT_ST_CUR__        = "<<<EVENTSTATECURRENT>>>"
__TAG_EVENT_ST_NXT__        = "<<<EVENTSTATENEXT>>>"

__TAG_PSAE_BEGIN__          = "<<<PER_STATE_ACTION_EVENT_BEGIN>>>"
__TAG_PSAE_END__            = "<<<PER_STATE_ACTION_EVENT_END>>>"
__TAG_PSAE_ACTION__         = "<<<PER_STATE_ACTION>>>"
__TAG_PSAE_EVENT__          = "<<<PER_STATE_EVENT>>>"
# END EMBEDDED SM SUPPORT.

# Python2 -> 3 shennanigans...try support both
try:
	from interface_base import *		# py2
except (ModuleNotFoundError, ImportError) as e:
	from .interface_base import *		# py3

try:
	from .preservative import *
except (ModuleNotFoundError, ImportError) as e:
	from preservative import *

try:
	from .cgen import CBASEGenerator, CCodeModel, alpha, __getnextalphabet__, __resetalphabet__, even_space, FileCopyUtil
except (ModuleNotFoundError, ImportError) as e:
	from cgen import CBASEGenerator, CCodeModel, alpha, __getnextalphabet__, __resetalphabet__, even_space, FileCopyUtil

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
		# EMBEDDED SM SUPPORT.
		self.event_transitions_per_state = {}  # ['event', ['next state,current state' , ...]]
		self.actionevents_per_state = {}       # ['state', [['event', 'action'] , ...]
		# END EMBEDDED SM SUPPORT.
		self.actionsignatures = OrderedDict()

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
		# EMBEDDED SM SUPPORT. ['current state, event', 'next state']
		tevent_transitions_tmp = {}
		# END EMBEDDED SM SUPPORT.

		# Filter
		for tableline in self.transition_table:
			if tableline[self.START_STATE] != "" and tableline[self.START_STATE].lower() != "none":
				tstate[tableline[self.START_STATE]] = 0
			if tableline[self.NEXT_STATE] != "" and tableline[self.NEXT_STATE].lower() != "none":
				tstate[tableline[self.NEXT_STATE]] = 0
			if tableline[self.EVENT] != "" and tableline[self.EVENT].lower() != "none":
				tevent[tableline[self.EVENT]] = 0
				# EMBEDDED SM SUPPORT. ['current state, event', 'next state']
				'''
				if tableline[self.NEXT_STATE] == "" or tableline[self.NEXT_STATE].lower() == "none":
					raise Exception('Events that dont change state should re-enter the current state.\nPlease fix your transition table')
				tevent_transitions_tmp[tableline[self.START_STATE] + ',' + tableline[self.EVENT]] =  tableline[self.NEXT_STATE]

				TODO : For the case below, how to support a different 'action' on the in-state-event???? Ie that event might have gotten the machine
				to this state with a particular action, but perhaps the user has configured a different action for this event in-state???
				'''
				if tableline[self.NEXT_STATE] == "" or tableline[self.NEXT_STATE].lower() == "none":
					tevent_transitions_tmp[tableline[self.START_STATE] + ',' + tableline[self.EVENT]] = tableline[self.START_STATE]
				else:
					tevent_transitions_tmp[tableline[self.START_STATE] + ',' + tableline[self.EVENT]] = tableline[self.NEXT_STATE]
				# This is for in-state-actions based on events...
				if tableline[self.ACTION] != "" and tableline[self.ACTION].lower() != "none":
					if not (tableline[self.START_STATE] in self.actionevents_per_state):
						self.actionevents_per_state[tableline[self.START_STATE]] = []
					self.actionevents_per_state[tableline[self.START_STATE]].append([tableline[self.EVENT], tableline[self.ACTION]])
					# END EMBEDDED SM SUPPORT.
			if tableline[self.ACTION] != "" and tableline[self.ACTION].lower() != "none":
				taction[tableline[self.ACTION]] = 0
				if not ((tableline[self.ACTION] + tableline[self.EVENT]) in self.actionsignatures):
					self.actionsignatures[tableline[self.ACTION] + tableline[self.EVENT]] = (tableline[self.ACTION], tableline[self.EVENT])  #, tableline[self.START_STATE],tableline[self.NEXT_STATE]))
			if tableline[self.GUARD] != "" and tableline[self.GUARD].lower() != "none":
				tguard[tableline[self.GUARD]] = 0
		# Populate CStateMachineModel
		for s in tstate:
			self.states.append(s)
		for e in tevent:
			self.events.append(e)
		for a in taction:
			self.actions.append(a)
		for g in tguard:
			self.guards.append(g)

		# EMBEDDED SM SUPPORT.
		for e in tevent:
			self.event_transitions_per_state[e] = []
			for s in tstate:
				key = s+','+e
				if key in tevent_transitions_tmp:
					self.event_transitions_per_state[e].append([tevent_transitions_tmp[key], s])
				else:
					self.event_transitions_per_state[e].append(['EVENT_IGNORED', s])
		# END EMBEDDED SM SUPPORT.


	def __getfirststate__(self):
		if not self.transition_table:
			return "NO TT PRESENT!"
		return self.transition_table[0][0]


class CStateMachineGenerator(CBASEGenerator):

	def __init__(self, inputfiledir, outputfiledir, events_interface=None, language=None, author='Anonymous', group='', brief=''):
		CBASEGenerator.__init__(self,inputfiledir,outputfiledir,language, author, group, brief)
		self.events_interface = events_interface

	def __loadtemplates_firstfiltering__(self, smmodel):
		"""
		See baseclass implementation. This just prepares the dictionary of things to replace
		for this type of codegeneration.

		@param smmodel:
		@return: cgen.CCodeModel, a dictionary -> {filename,[lines]}
		"""

		dict_to_replace_lines = {}
		dict_to_replace_lines[__TAG_SM_NAME__] = smmodel.statemachinename
		dict_to_replace_lines[__TAG_CLASS_NAME__] =smmodel.statemachinename
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
		dict_to_replace_filenames['.ty'] = '.py'
		dict_to_replace_filenames['.t'] = '.h'
		dict_to_replace_filenames['.t#'] = '.cs'
		dict_to_replace_filenames['.hpp'] = '.cpp'     # there are no '.hpp' templates...but search and replace will apply '.t -> .h' first so '.tpp' becomes '.hpp'...grrr

		return CBASEGenerator.__loadtemplates_firstfiltering__(self,dict_to_replace_lines,dict_to_replace_filenames)

	def __get_event_signature__(self,name):
		if self.events_interface is None or self.language is None:
			return ""
		for s in self.events_interface.Structs():
			if s.Name == name:
				return self.language.ParameterString(self.language.GetFactoryCreateParams(s, self.events_interface))

		return ""

	def __instantiate_event_struct_member(self, name, whitespace_cnt, is_ptr=True):
		if self.events_interface is None or self.language is None:
			return ""
		for s in self.events_interface.Structs():
			if s.Name == name:
				guts = self.language.InstantiateStructMembers(s, self.events_interface, '', "data", self.language.Accessor(is_ptr))
				result = ''
				cnt = 0
				for g in guts:
					result = result + (whitespace_cnt*'    ' if cnt > 0 else '') + g + '\n'
					cnt = cnt + 1
				return result
		return ""

	def __declare_event_struct_members(self, name, whitespace_cnt):
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
				# remove last '\n'
				result = result[:-1]
				return result
		return ""


	def __innerexpand__secondfiltering__(self, names2x, lines2x, puthere):
		global alpha
		__resetalphabet__()
		cnt = 0
		for name in names2x:
			for line in lines2x:
				newline = line
				newline = newline.replace(__TAG_STATENAME__, name)
				newline = newline.replace(__TAG_EVENTNAME__, name)
				newline = newline.replace(__TAG_ACTIONNAME__, name)
				newline = newline.replace(__TAG_GUARDNAME__, name)
				newline = newline.replace(__TAG_ABC__, chr(alpha))
				newline = newline.replace(__TAG_123__, str(cnt))
				# EMBEDDED SM SUPPORT.
				newline = newline.replace(__TAG_EVENT_CURNEX_ST_BEG__, __TAG_EVENT_CURNEX_ST_BEG__ + '<<<' + name + '>>>')  # put a marker (event name) for mapping
				newline = newline.replace(__TAG_PSAE_BEGIN__, __TAG_PSAE_BEGIN__ + '<<<' + name + '>>>')  # put a marker (state name) for mapping
				# END EMBEDDED SM SUPPORT.
				tabcnt = newline.count('    ')
				newline = newline.replace(__TAG_EVENT_SIGNATURE__, self.__get_event_signature__(name))
				newline = newline.replace(__TAG_EVENT_MEMBERINST__, self.__instantiate_event_struct_member(name, tabcnt, True))        # PTR
				newline = newline.replace(__TAG_LITE_EVENT_MEMBERINST__, self.__instantiate_event_struct_member(name, tabcnt, False))  # NO PTR
				newline = newline.replace(__TAG_EVENT_MEMBERDECL__, self.__declare_event_struct_members(name, tabcnt))
				puthere.append(newline)
			cnt = cnt + 1
			__getnextalphabet__()

	def __innerexpand_actionsignatures__(self, states2x, lines2x, puthere):
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
							.replace(__TAG_ACTIONNAME__, actionname)
							.replace(__TAG_EVENTNAME__, eventname)
							.replace(__TAG_ABC__, chr(alpha))
							.replace(__TAG_123__, str(cnt)))
			cnt = cnt + 1
			__getnextalphabet__()

	def __transitiontable_replace_NONE__(self, val):
		if val == "" or val.lower() == 'none':
			val = "msmf::none"
		return val

	def __transitiontableLITE_guard_replace_NONE__(self, val):
		tmp_val = val.replace('__', '')
		if tmp_val == "" or tmp_val.lower() == 'none':
			val = "boost::msm::gnone"
		return val

	def __transitiontableLITE_action_replace_NONE__(self, val):
		tmp_val = val.replace('__', '')
		if tmp_val == "" or tmp_val.lower() == 'none' or tmp_val.lower().find('::none<') > -1:
			val = "boost::msm::none"
		return val

	''' This SM doesnt seem to allow 'none' transitions -> make it transition to the source state'''
	def __transitiontableLITE_nextstate_replace_NONE__(self, val, source_state):
		tmp_val = val.replace('__', '')
		tmp_val = tmp_val.replace('msmf::', '')
		if tmp_val == "" or tmp_val.lower() == 'none':
			val = source_state
		return val


	def __expand_secondfiltering__(self, smmodel, cmmodel):
		for file in cmmodel.filenames_to_lines:

			ex_state     = False
			ex_event     = False
			ex_action    = False
			ex_actionsig = False
			ex_guard     = False
			ex_tt        = False
			ex_tt_lite   = False
			ex_tt_lite_sml = False

			snipped_to_expand = []
			alllinesexpanded = []
			for line in cmmodel.filenames_to_lines[file]:
				begin		= line.find(__TAG_PS_BEGIN__) > -1 or \
								line.find(__TAG_PE_BEGIN__) > -1 or \
								line.find(__TAG_PA_BEGIN__) > -1 or \
								line.find(__TAG_PASIG_BEGIN__) > -1 or \
								line.find(__TAG_PG_BEGIN__) > -1 or \
								line.find(__TAG_TTT_BEGIN__) > -1 or \
								line.find(__TAG_TTT_LITE_BEGIN__) > -1 or \
								line.find(__TAG_TTT_LITE_SML_BEGIN__) > -1

				ex_state     = line.find(__TAG_PS_BEGIN__) > -1 or ex_state
				ex_event     = line.find(__TAG_PE_BEGIN__) > -1 or ex_event
				ex_action    = line.find(__TAG_PA_BEGIN__) > -1 or ex_action
				ex_actionsig = line.find(__TAG_PASIG_BEGIN__) > -1 or ex_actionsig
				ex_guard     = line.find(__TAG_PG_BEGIN__) > -1 or ex_guard
				ex_tt        = line.find(__TAG_TTT_BEGIN__) > -1 or ex_tt
				ex_tt_lite   = line.find(__TAG_TTT_LITE_BEGIN__) > -1 or ex_tt_lite
				ex_tt_lite_sml = line.find(__TAG_TTT_LITE_SML_BEGIN__) > -1 or ex_tt_lite_sml
				if not ex_state and not ex_event and not ex_action and not ex_actionsig and not ex_guard and not ex_tt and not ex_tt_lite and not ex_tt_lite_sml:
					alllinesexpanded.append(line.replace(__TAG_INIT_STATE__, smmodel.__getfirststate__()))

				if ex_state and line.find(__TAG_PS_END__) > -1:
					self.__innerexpand__secondfiltering__(smmodel.states, snipped_to_expand, alllinesexpanded)
					snipped_to_expand = []
					ex_state = False
				if ex_event and line.find(__TAG_PE_END__) > -1:
					self.__innerexpand__secondfiltering__(smmodel.events, snipped_to_expand, alllinesexpanded)
					snipped_to_expand = []
					ex_event = False
				if ex_action and line.find(__TAG_PA_END__) > -1:
					self.__innerexpand__secondfiltering__(smmodel.actions, snipped_to_expand, alllinesexpanded)
					snipped_to_expand = []
					ex_action = False
				if ex_actionsig and line.find(__TAG_PASIG_END__) > -1:
					self.__innerexpand_actionsignatures__(smmodel.actionsignatures, snipped_to_expand, alllinesexpanded)
					snipped_to_expand = []
					ex_actionsig = False
				if ex_guard and line.find(__TAG_PG_END__) > -1:
					self.__innerexpand__secondfiltering__(smmodel.guards, snipped_to_expand, alllinesexpanded)
					snipped_to_expand = []
					ex_guard = False
				if ex_tt and line.find(__TAG_TTT_END___) > -1:
					len_tt = len(smmodel.transition_table)
					tt_out = "        // " + len("msmf::Row < ") * ' ' + even_space("Start") + even_space("Event") + even_space("Next") + even_space("Action") + even_space("Guard") + '\n'
					for i, ttline in enumerate(smmodel.transition_table):
						tt_out += '        msmf::Row < '
						tt_out += even_space(self.__transitiontable_replace_NONE__(ttline[smmodel.START_STATE])) + ','
						tt_out += even_space(self.__transitiontable_replace_NONE__(ttline[smmodel.EVENT]      )) + ','
						tt_out += even_space(self.__transitiontable_replace_NONE__(ttline[smmodel.NEXT_STATE] )) + ','
						tt_out += even_space(self.__transitiontable_replace_NONE__(ttline[smmodel.ACTION]     )) + ','
						tt_out += even_space(self.__transitiontable_replace_NONE__(ttline[smmodel.GUARD]      )) + '>    '
						if i != len_tt-1:
							tt_out += ","
						tt_out += "    // " + str(i) + '\n'
						alllinesexpanded.append(tt_out)
						tt_out = ""
					ex_tt = False

				if ex_tt_lite and line.find(__TAG_TTT_LITE_END__) > -1:
					tt_out = "                // " + even_space("Start + ") + even_space("Event") + even_space("[ Guard ] ") + even_space("/ Action") + even_space(" = Next") + '\n'
					startStateHasEntryExit = {}
					for i, ttline in enumerate(smmodel.transition_table):
						if i == 0:  # initial state
							tt_out += "                 *"
						else:
							tt_out += "                , "
						tt_out += even_space(self.__transitiontable_replace_NONE__(ttline[smmodel.START_STATE])) + '+'
						tt_out += even_space('event<' + self.__transitiontable_replace_NONE__(ttline[smmodel.EVENT]) + ">") + ' '
						tt_out += even_space('['+self.__transitiontableLITE_guard_replace_NONE__('__'+ttline[smmodel.GUARD])+']') + ' / '
						tt_out += even_space(self.__transitiontableLITE_action_replace_NONE__('__'+ttline[smmodel.ACTION]))
						if ttline[smmodel.NEXT_STATE].lower() != 'none':  # to not get transitions into/outof state on actions that dont change the state...
							tt_out += ' = ' + even_space(self.__transitiontableLITE_nextstate_replace_NONE__(ttline[smmodel.NEXT_STATE], ttline[smmodel.START_STATE]))
						tt_out += '\n'
						alllinesexpanded.append(tt_out)
						tt_out = ""
						# State entry/exit, once only
						if not (ttline[smmodel.START_STATE] in startStateHasEntryExit):
							startStateHasEntryExit[ttline[smmodel.START_STATE]] = True
							tt_out += "                , "+ttline[smmodel.START_STATE]+" + msm::on_entry / __" + ttline[smmodel.START_STATE] + 'OnEntry\n'
							tt_out += "                , "+ttline[smmodel.START_STATE]+" + msm::on_exit / __" + ttline[smmodel.START_STATE] + 'OnExit'
							tt_out += '\n'
							alllinesexpanded.append(tt_out)
							tt_out = ""
					ex_tt_lite = False

				if ex_tt_lite_sml and line.find(__TAG_TTT_LITE_SML_END__) > -1:
					tt_out = "                // " + even_space("Start + ") + even_space("Event") + even_space("[ Guard ] ") + even_space("/ Action", 100) + even_space(" = Next") + '\n'
					startStateHasEntryExit = {}
					for i, ttline in enumerate(smmodel.transition_table):
						if i == 0:  # initial state
							tt_out += "                 *"
						else:
							tt_out += "                , "
						tt_out += even_space(self.__transitiontable_replace_NONE__(ttline[smmodel.START_STATE])) + '+'
						tt_out += even_space('event<' + self.__transitiontable_replace_NONE__(ttline[smmodel.EVENT]) + ">") + ' '
						tt_out += even_space('['+self.__transitiontableLITE_guard_replace_NONE__('__'+ttline[smmodel.GUARD])+']') + ' / '
						tt_out += even_space(self.__transitiontableLITE_action_replace_NONE__('call(this,&CONCRETE::' + ttline[smmodel.ACTION] + '<' + ttline[smmodel.EVENT] + ">)"), 100)
						if ttline[smmodel.NEXT_STATE].lower() != 'none':  # to not get transitions into/outof state on actions that dont change the state...
							tt_out += ' = ' + even_space(self.__transitiontableLITE_nextstate_replace_NONE__(ttline[smmodel.NEXT_STATE], ttline[smmodel.START_STATE]))
						tt_out += '\n'
						alllinesexpanded.append(tt_out)
						tt_out = ""
						# State entry/exit, once only
						if not (ttline[smmodel.START_STATE] in startStateHasEntryExit):
							startStateHasEntryExit[ttline[smmodel.START_STATE]] = True
							tt_out += "                , "+ttline[smmodel.START_STATE]+" + msm::on_entry<_> / __" + ttline[smmodel.START_STATE] + 'OnEntry\n'
							tt_out += "                , "+ttline[smmodel.START_STATE]+" + msm::on_exit<_> / __" + ttline[smmodel.START_STATE] + 'OnExit'
							tt_out += '\n'
							alllinesexpanded.append(tt_out)
							tt_out = ""
					ex_tt_lite_sml = False

				if (ex_state or ex_event or ex_action or ex_actionsig or ex_guard or ex_tt or ex_tt_lite or ex_tt_lite_sml) and not begin:
					snipped_to_expand.append(line)

			cmmodel.filenames_to_lines[file] = alllinesexpanded

	# EMBEDDED SM SUPPORT.
	def __innerexpand__thirdfiltering__eventtransitionsperstate(self, namesmap3x, lines3x, puthere):
		global alpha
		__resetalphabet__()
		cnt = 0
		# First find the mapping marker
		for _map in namesmap3x:
			currentstate = _map[1]
			nextstate = _map[0]
			for line in lines3x:
				#puthere.append(line.replace(__TAG_ABC__, chr(alpha)).replace(__TAG_123__, str(cnt)))
				puthere.append(line.replace(__TAG_EVENT_ST_CUR__, currentstate).replace(__TAG_EVENT_ST_NXT__, nextstate).replace(__TAG_ABC__, chr(alpha)).replace(__TAG_123__, str(cnt)))
			cnt = cnt + 1
			__getnextalphabet__()

	# this function is pretty much the same as the one above...

	def __innerexpand__thirdfiltering__eventactionsperstate(self, namesmap3x, lines3x, puthere):
		global alpha
		__resetalphabet__()
		cnt = 0
		# First find the mapping marker
		for _map in namesmap3x:
			action = _map[1]
			event = _map[0]
			for line in lines3x:
				# puthere.append(line.replace(__TAG_ABC__, chr(alpha)).replace(__TAG_123__, str(cnt)))
				puthere.append(line.replace(__TAG_PSAE_ACTION__, action).replace(__TAG_PSAE_EVENT__, event).replace(__TAG_ABC__, chr(alpha)).replace(__TAG_123__, str(cnt)))
			cnt = cnt + 1
			__getnextalphabet__()

	def __expand_thirdfiltering__(self, smmodel, cmmodel):
		for file in cmmodel.filenames_to_lines:

			ex_state = False
			ex_event = False
			#ex_action = False
			#ex_guard = False

			snippet_to_expand = []
			alllinesexpanded = []
			state_action_map = ''
			event_map = ''
			for line in cmmodel.filenames_to_lines[file]:
				begin = line.find(__TAG_EVENT_CURNEX_ST_BEG__) > -1 or line.find(__TAG_PSAE_BEGIN__) > -1  #or line.find(__TAG_PA_BEGIN__) > -1 or line.find(__TAG_PG_BEGIN__) > -1
				if begin:
					event_map        = line.replace(__TAG_EVENT_CURNEX_ST_BEG__, '').replace('<<<', '').replace('>>>', '').replace('\t', '').replace('\n', '').replace("    ","")
					state_action_map = line.replace(__TAG_PSAE_BEGIN__, '').replace('<<<', '').replace('>>>', '').replace('\t', '').replace('\n', '').replace("    ","")

				end_event = (line.find(__TAG_EVENT_CURNEX_ST_END__) > -1)
				end_state = (line.find(__TAG_PSAE_END__) > -1)
				ex_state = line.find(__TAG_PSAE_BEGIN__) > -1 or ex_state
				ex_event = line.find(__TAG_EVENT_CURNEX_ST_BEG__) > -1 or ex_event
				#ex_action = line.find(__TAG_PA_BEGIN__) > -1 or ex_action
				#ex_guard = line.find(__TAG_PG_BEGIN__) > -1 or ex_guard
				#if not ex_state and not ex_event and not ex_action and not ex_guard:
				#    alllinesexpanded.append(line.replace(__TAG_INIT_STATE__, smmodel.__getfirststate__()))

				if ex_state and line.find(__TAG_PSAE_END__) > -1:
					if state_action_map in smmodel.actionevents_per_state:
						self.__innerexpand__thirdfiltering__eventactionsperstate(smmodel.actionevents_per_state[state_action_map], snippet_to_expand, alllinesexpanded)
					snippet_to_expand = []
					ex_state = False
				if ex_event and line.find(__TAG_EVENT_CURNEX_ST_END__) > -1:
					self.__innerexpand__thirdfiltering__eventtransitionsperstate(smmodel.event_transitions_per_state[event_map], snippet_to_expand, alllinesexpanded)
					snippet_to_expand = []
					ex_event = False
				#if ex_action and line.find(__TAG_PA_END__) > -1:
				#	self.__innerexpand__thirdfiltering__(smmodel.actions, snippet_to_expand, alllinesexpanded)
				#	snippet_to_expand = []
				#	ex_action = False
				#if ex_guard and line.find(__TAG_PG_END__) > -1:
				#	self.__innerexpand__thirdfiltering__(smmodel.guards, snippet_to_expand, alllinesexpanded)
				#	snippet_to_expand = []
				#	ex_guard = False

				#if (ex_state or ex_event or ex_action or ex_guard) and not begin:
				if (ex_event or ex_state) and not begin:
					snippet_to_expand.append(line)
				elif not begin and not end_event and not end_state:  # Unlike the second pass, this needs to preserve what was done there...
					alllinesexpanded.append(line)

			cmmodel.filenames_to_lines[file] = alllinesexpanded
	# END EMBEDDED SM SUPPORT.

	''' Used for State Machine Generation
	'''
	def Generate(self, transitiontable, namespacenname, statemachinename, dclspc=""):
		
		print("*************************************")
		print("******* SMGen ***********************")
		print("*************************************")
		print(" Output Dir   : " + self.output_gen_file_dir)
		print(" State Machine: " + statemachinename)
		print(" Executing in : " + os.path.realpath(__file__))
		print("*************************************")

		sm = CTransitionTableModel(transitiontable, namespacenname, statemachinename, dclspc)
		cm = self.__loadtemplates_firstfiltering__(sm)
		self.__expand_secondfiltering__(sm, cm)
		# EMBEDDED SM SUPPORT.
		self.__expand_thirdfiltering__(sm, cm)
		# END EMBEDDED SM SUPPORT.

		# Preserve user tags.
		self.__preserve_usertags_in_files__(cm)
		'''
		# Round-trip Code Preservation. Will load the code to preserve upon creation (if the output dir is not-empty/the same as the one in the compile path).
		preservation = Preservative(self.output_gen_file_dir)
		preservation.Emplace(cm.filenames_to_lines)
		'''
		# Write output to file.
		self.__createoutput__(cm.filenames_to_lines)

		# Copy non-autogenerated required files to output.
		if isinstance(self.language, LanguageCPP) :

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
		cm = self.__loadtemplates_firstfiltering__(sm)
		self.__expand_secondfiltering__(sm, cm)

		# Round-trip Code Preservation. Will load the code to preserve upon creation (if the output dir is not-empty/the same as the one in the compile path).
		# TCP gen might have a different output directory (typically COG will put files into an intermediate dir, and them copy them elsewhere
		preservation = None
		if preserve_dir == "":
			preservation = Preservative(self.output_gen_file_dir)
		else:
			preservation = Preservative(preserve_dir)

		preservation.Emplace(cm.filenames_to_lines)
		# Write output to file.
		self.__createoutput__(cm.filenames_to_lines)

		# return the filenames
		filenames = []
		for filename in cm.filenames_to_lines.keys():
			filenames.append(filename)
		return filenames
