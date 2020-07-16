__author__ = 'eugene'

'''

	This file is part of 'KoJen'.

	'KoJen' is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	'KoJen' is distributed in the hope that it will be useful
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with 'KoJen'.  If not, see <http://www.gnu.org/licenses/>.
	For any requests please contact : koh.jaen@yahoo.de.

'''
from collections import OrderedDict
import xml.etree.ElementTree as ET


class VisualParadigmStateMachineXMLParser:

	def __init__(self, xmlfile):
		self.xmlfile = xmlfile
		self.tree = ET.parse(self.xmlfile)
		self.root = self.tree.getroot()

	# This will parse the whole tree
	def PrintTree(self):
		for neighbour in self.root.iter():
			print(neighbour)

	def GetTransitionTable(self):

		tmp_TT = OrderedDict()
		# States
		states = {}
		for state in self.root.findall('Models/State2'):
			states[state.get('Id')] = state.get('Name')

		# Guards
		guards = {}
		for guard in self.root.findall('Models/ConstraintElement'):
			guards[guard.get('Id')] = guard.find("Specification/CompositeValueSpecification").get('Value')

		# Activities
		activities = {}
		for activity in self.root.findall('Models/ModelRelationshipContainer/ModelChildren/ModelRelationshipContainer/ModelChildren/Transition2/ModelChildren/Activity'):
			activities[activity.get('Id')] = activity.get('Name')

		# Transition Events
		for transition in self.root.findall('Models/ModelRelationshipContainer/ModelChildren/ModelRelationshipContainer/ModelChildren/Transition2'):
			# Get action
			action = None
			if transition.get('Effect') is not None:
				action = activities[transition.get('Effect')]
			if transition.get('Name') is not None:
				# print(' From ', states[transition.get('From')], ' on event ',transition.get('Name'),' To ',states[transition.get('To')],' if ', 'None' if transition.get('Guard') is None else guards[transition.get('Guard')], ' do ', 'None' if action is None else action)

				if not states[transition.get('From')] in tmp_TT:
					tmp_TT[states[transition.get('From')]] = []
				#		FROM									EVENT						NEXT						ACTION
				state_from = states[transition.get('From')]
				state_to = states[transition.get('To')]
				tmp_TT[state_from].append([transition.get('Name'), 'None' if state_from == state_to else state_to, 'None' if action is None else action, 'None' if transition.get('Guard') is None else guards[transition.get('Guard')]])

		# Build the usual format
		transition_table = []
		for start, val in tmp_TT.items():
			for event, _next, action, guard in val:
				transition_table.append([start, event, _next, action, guard])
				# print(start,event,next,action,guard)

		return transition_table

if __name__ == "__main__":
	parser = VisualParadigmStateMachineXMLParser(r"C:\Work\ICEy\trunk\ICESY\Documentation\Architecture\XML\project.xml")
	tt = parser.GetTransitionTable()
