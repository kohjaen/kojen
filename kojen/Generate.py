#!/usr/bin/env python3
try:
    from . import protogen, smgen, umlgen, coggen, vppfs, LanguageCPP, LanguageCsharp, LanguagePython, cgen
except:
    import protogen, smgen, umlgen, coggen, vppfs, LanguageCPP, LanguageCsharp, LanguagePython, cgen

import os

''' Generate Entry function for Protocols. 

    The python-interface-generator file used to define the structs etc, is passed in, and called by COG in the second stage.
'''


def Protocol(output_dir, pythoninterfacegeneratorfilename, namespacename, classname, declspec="", author = "", group="", brief="", template_dir="") -> list:
    return protogen.Generate(output_dir, pythoninterfacegeneratorfilename, namespacename, classname, declspec, author, group, brief, template_dir)


''' Generate Entry function for State Machines

    COG is not used here...so even though a python-interface-generator file is used by the event structs/parameterization, it needs
    to be called by the callee, and the events interface passed in.
'''


def StateMachine(outputdir, transition_table, eventsinterface, namespacenname, statemachinenameprefix, dclspc="", author="", group="", brief="", templatedir="", __internal="", __copy_other_files=True) -> list:
    if not templatedir.strip():
        templatedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "statemachine_templates_embedded_arm")

    if not os.path.isdir(templatedir):
        print("Error : dir '" + templatedir + "' does not exist. Aborting.")
        return

    language = LanguageCPP.LanguageCPP()
    smgenerator = smgen.CStateMachineGenerator(templatedir, outputdir, eventsinterface, language, author, group, brief)
    if not __internal:
        smgenerator.vpp_filename = "Transition Table"
    else:
        smgenerator.vpp_filename = __internal
    return smgenerator.Generate(transition_table, namespacenname, statemachinenameprefix, dclspc, __copy_other_files)


def StateMachine_CSHARP(outputdir, transition_table, eventsinterface, namespacenname, statemachinenameprefix, dclspc="", author="", group="", brief="", templatedir="", __internal="", __copy_other_files=True) -> list:
    if not templatedir.strip():
        templatedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "statemachine_templates_cs_winlinmac")

    if not os.path.isdir(templatedir):
        print("Error : dir '" + templatedir + "' does not exist. Aborting.")
        return []

    language = LanguageCsharp.LanguageCsharp()
    smgenerator = smgen.CStateMachineGenerator(templatedir, outputdir, eventsinterface, language, author, group, brief)
    if not __internal:
        smgenerator.vpp_filename = "Transition Table"
    else:
        smgenerator.vpp_filename = __internal
    return smgenerator.Generate(transition_table, namespacenname, statemachinenameprefix, dclspc, __copy_other_files)


def StateMachine_PYTHON(outputdir, transition_table, eventsinterface, namespacenname, statemachinenameprefix, dclspc="", author="", group="", brief="", templatedir="", __internal="", __copy_other_files=True) -> list:
    if not templatedir.strip():
        templatedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "statemachine_templates_py")

    if not os.path.isdir(templatedir):
        print("Error : dir '" + templatedir + "' does not exist. Aborting.")
        return []

    language = LanguagePython.LanguagePython()
    smgenerator = smgen.CStateMachineGenerator(templatedir, outputdir, eventsinterface, language, author, group, brief)
    if not __internal:
        smgenerator.vpp_filename = "Transition Table"
    else:
        smgenerator.vpp_filename = __internal
    return smgenerator.Generate(transition_table, namespacenname, statemachinenameprefix, dclspc, __copy_other_files)


def StateMachineFromModel(outputdir, vp_project_path, vp_statemachinename, eventsinterface, namespacenname, statemachinenameprefix, dclspc="", author="", group="", brief="", templatedir="", __copy_other_files=True) -> list:
    transition_table = vppfs.ExtractTransitionTable(vp_statemachinename, vp_project_path)
    return StateMachine(outputdir, transition_table, eventsinterface, namespacenname, statemachinenameprefix, dclspc, author, group, brief, templatedir, os.path.basename(vp_project_path),__copy_other_files)


''' Generate Entry function for Class Diagrams
'''


def UML(outputdir, vp_project_path, vp_classdiagramname, dclspc="", author="", group="", brief="", namespace_to_folders=False, templatefiledir="") -> list:
    language = LanguageCPP.LanguageCPP()
    return umlgen.Generate(vp_project_path, vp_classdiagramname, outputdir, language, author, group, brief, namespace_to_folders, dclspc, templatefiledir)

def UML_CSHARP(outputdir, vp_project_path, vp_classdiagramname, dclspc="", author="", group="", brief="", namespace_to_folders=False, templatefiledir="") -> list:
    language = LanguageCsharp.LanguageCsharp()
    return umlgen.Generate(vp_project_path, vp_classdiagramname, outputdir, language, author, group, brief, namespace_to_folders, dclspc, templatefiledir)


''' Generate Entry function for template files using COG
'''


def Cogify(output_dir, pythonfile, cog_template_FILEorDIRECTORY, namespacename, classname, author="", group="", brief="", dclspec="") -> list:
    if os.path.isfile(cog_template_FILEorDIRECTORY):
        return coggen.GenerateFile(output_dir, pythonfile, cog_template_FILEorDIRECTORY, author, namespacename, classname, group, brief, dclspec)
    else:
        return coggen.GenerateDirectory(output_dir, pythonfile, cog_template_FILEorDIRECTORY, author, namespacename, classname, group, brief, dclspec)


''' File preservation sync utility
'''
def FileSync(from_file, to_file) -> None:
    cgen.FilePreservationSyncUtil(from_file, to_file)