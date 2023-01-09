#!/usr/bin/env python3
def TTToDot(TransitionTable):
    assert len(TransitionTable) >= 1
    assert len(TransitionTable[0]) == 5

    plantUml = []

    plantUml.append("@startuml")
    plantUml.append("hide empty description")
    plantUml.append("")
    # plantUml.append("top to bottom direction")
    # plantUml.append("left to right direction")
    # plantUml.append("top to bottom direction")
    # plantUml.append("skinparam nodesep 10")
    plantUml.append("skinparam ranksep 150")
    plantUml.append("")

    initialState = TransitionTable[0][0]
    plantUml.append("[*] --> " + initialState)

    for line in TransitionTable:
        assert len(line) == 5

        Start  = line[0].strip()
        Event  = line[1].strip()
        Guard  = line[4].replace("none", "").replace("None", "")
        Action = line[3].replace("none", "").replace("None", "")
        Next   = line[2].replace("none", "").replace("None", "")
        if not Next:
            Next = Start
        if Guard:
            Guard = "[" + Guard + "]"
        Guard_Action = Guard
        if Action:
            Guard_Action = Guard + "\\n/ " + Action

        plantUml.append(Start + " --> " + Next + " : " + Event + Guard_Action)

    plantUml.append("@enduml")
    return plantUml

def FromTransitionTable(TransitionTable, outputPath):
    plantUml = TTToDot(TransitionTable)
    with open(outputPath, mode='wt', encoding='utf-8') as myfile:
        myfile.write('\n'.join(plantUml))

def FromSML(fileWithSML, outputPath):
    import re
    lines = []
    with open(fileWithSML, 'r') as f:
        lines = f.readlines()
    assert len(lines) > 0
    has = False
    smltt = []
    tt = []
    ''' Extract only lines for SML TT ... and only the first transition table in case there are multiple'''
    for l in lines:
        s = l.strip()
        if not "//" in s:
            if "state<" in s:
                if not has:
                    has = True
                smltt.append(s)
            else: # Only first set of
                if has:
                    break
    assert len(smltt) > 0
    ''' Format to pythonic TT '''
    for s in smltt:
        # Split START/EVENT/GUARD and ACTION/NEXT
        SEG_AN = s.split("/")
        if len(SEG_AN) != 2:
            raise Exception('Unhandled error #1')
        # Extract Start/Event/Guard
        Start = re.search(r'state<(.*?)>', SEG_AN[0]).group(1)
        Event = re.search(r'event<(.*?)>', SEG_AN[0]).group(1)
        # escape [] chars with backslash as they have special meaning.
        Guard = re.search(r'\[(.*?)\]', SEG_AN[0]).group(1).replace("gnone", "None")
        # Extract Action/Next
        Action = ""
        Next = ""
        if "=" in SEG_AN[1]:
            A_N = SEG_AN[1].split("=")
            Action = A_N[0].strip().replace("none","None")
            Next   = re.search(r'state<(.*?)>', A_N[1]).group(1)
        else:
            Action = SEG_AN[1].strip().replace("none", "None")
        tt.append([Start, Event, Next, Action, Guard])
    assert len(smltt) == len(tt)
    FromTransitionTable(tt, outputPath)
