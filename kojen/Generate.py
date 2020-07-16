from . import protogen, smgen, umlgen, vppfs, LanguageCPP, LanguageCsharp
import os

''' Generate Entry function for Protocols. 

    The python-interface-generator file used to define the structs etc, is passed in, and called by COG in the second stage.
'''
def Protocol(output_dir, pythoninterfacegeneratorfilename, namespacename, classname, declspec="", template_dir=""):
    protogen.Generate(output_dir, pythoninterfacegeneratorfilename, namespacename, classname,declspec,template_dir)

''' Generate Entry function for State Machines

	COG is not used here...so even though a python-interface-generator file is used by the event structs/parameterization, it needs
	to be called by the callee, and the events interface passed in.
'''


def StateMachine(transition_table, eventsinterface, outputdir, namespacenname, statemachinenameprefix, dclspc="", user_email_address="", templatedir=""):
	if not templatedir.strip():
		templatedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "statemachine_templates_embedded_arm")

	language = LanguageCPP.LanguageCPP()
	smgenerator = smgen.CStateMachineGenerator(templatedir, outputdir, eventsinterface, language, user_email_address)
	smgenerator.Generate(transition_table, namespacenname, statemachinenameprefix, dclspc)

def StateMachineFromModel(vp_project_path, vp_statemachinename, eventsinterface, outputdir, namespacenname, statemachinenameprefix, dclspc="", user_email_address = "", templatedir = ""):
	transition_table = vppfs.ExtractTransitionTable(vp_statemachinename, vp_project_path)
	StateMachine(transition_table, eventsinterface, outputdir, namespacenname, statemachinenameprefix, dclspc, user_email_address, templatedir)
	

''' Generate Entry function for Class Diagrams
'''
def UML(vp_project_path, vp_classdiagramname, outputdir, dclspc="", user_email_address = "", namespace_to_folders = False, templatefiledir=""):
	language = LanguageCPP.LanguageCPP()
	umlgen.Generate(vp_project_path, vp_classdiagramname, outputdir, language, user_email_address, namespace_to_folders, dclspc, templatefiledir)
	
def UML2(vp_project_path, vp_classdiagramname, outputdir, dclspc="", user_email_address = "", namespace_to_folders = False, templatefiledir=""):
	language = LanguageCsharp.LanguageCsharp()
	umlgen.Generate(vp_project_path, vp_classdiagramname, outputdir, language, user_email_address, namespace_to_folders, dclspc, templatefiledir)