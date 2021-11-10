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
    parser = VisualParadigmStateMachineXMLParser(r"C:\Work\Documentation\Architecture\XML\project.xml")
    tt = parser.GetTransitionTable()
