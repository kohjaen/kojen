#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'eugene'

"""

FANTASTIC EXAMPLES OF UML -> C++ here :

http://icarus.cs.weber.edu/~dab/cs1410/textbook/chapters.html
->
http://icarus.cs.weber.edu/~dab/cs1410/textbook/uml.html

TODO : Parameterized constructors and inheritance!

"""
try:
    import vppfs
except (ModuleNotFoundError, ImportError) as e:
    from kojen import vppfs

import unittest

'''----------------------------------------------------------------------'''
''' These appear to be the values for the different types of visibility '''


class Visibility:
    Public = '71'
    Protected = '67'
    Private = '66'
    Package = '68'


def VisibilityToHumanReadableString(vis):
    if vis == Visibility.Public:
        return "public"
    if vis == Visibility.Protected:
        return "protected"
    if vis == Visibility.Private:
        return "private"
    if vis == Visibility.Package:
        return "package"
    return "public"  # It appears that "unspecified" can return '65'


'''----------------------------------------------------------------------'''
''' These appear to be the values for the different types of scope (static = classifier)'''
SCOPE_CLASSIFIER = '65'

'''----------------------------------------------------------------------'''
'''A parameter of a function, with direction 'in' means it can't be modified...thus const '''
DIRECTION_IN = '65'
DIRECTION_OUT = '66'

'''----------------------------------------------------------------------'''
'''An association has 3 types ... association, aggregation, composition '''

# Default is association...each know about the other...
AGGREGATION_KIND__AGGREGATE  =  '66'
AGGREGATION_KIND__COMPOSITE  =  '67'

'''----------------------------------------------------------------------'''


def CleanName(name):
    return name.replace('=', '_').replace('<', '_').replace('>', '_').replace(';', '_').replace(r'\n', '_').\
        replace(r'\r', '_').replace(r'\t', '_').replace('\n', '_').replace('\r', '_').replace('\t', '_').\
        replace('"', "_").replace('(', '_').replace(')', '_').replace("*", "_").replace("+", "_").replace("-", "_").\
        replace("^", "_").replace("%", "_").replace("~", "_").replace("!", "_").replace(" ", "").replace("|", "_").\
        replace(":", "_")


def GetNestedTypeNamesFromNestedTypeIDS(nestedTypeIDs, table_vppmodelelements):
    # If the type is a class in a package, type will be 'packageID:classID' etc etc  for levels of nesting...
    # For most OOP languages we need to nest the type...
    nested_types = nestedTypeIDs.split(':')
    result = ""
    for t in nested_types:
        modelelement = table_vppmodelelements.GetModelElement(t)
        result = result + modelelement.NAME + "::"
    # remove the last "::"
    return result.rstrip(':')

PRIMITIVES = {"char",
              "wchar_t",
              "string",
              "wstring",
              "std::string",
              "std::wstring",
              "signed char",
              "short int",
              "int",
              "long int",
              "unsigned char",
              "unsigned short int",
              "unsigned int",
              "unsigned long int",
              "wchar_t",
              "bool",
              "boolean",
              "float",
              "double",
              "long",
              "void",
              "size_t",
              "ptrdiff_t",
              "int8",
              "uint8",
              "int16",
              "uint16",
              "int32",
              "uint32",
              "int64",
              "uint64",
              "int8_t",
              "uint8_t",
              "int16_t",
              "uint16_t",
              "int32_t",
              "uint32_t",
              "int64_t",
              "uint64_t"}

def IsTypePrimitive(type):
    global PRIMITIVES
    type = CleanModifiersFromType(type)
    return type in PRIMITIVES

def IsTypePointerOrRef(type):
    return type.find("*") > -1 or type.find("&") > -1

def CleanModifiersFromType(type):
    # &, *, []
    return type.replace("*", "").replace("&", "").replace("]","").replace("[","").replace("boolean", "bool")

'''----------------------------------------------------------------------'''
''' class Inheritance -> from searching the web, it appears the UML 'Generalization' and 'Realization' are the same, for C++ at least.
    This, until I find a better source of info (or a language with different semantics), I will treat them both the same.
    
    class Generalization(vppfs.VPPModelElement):
    class Realization(vppfs.VPPModelElement):
    
    If we were to split these concepts, the same code would be used.
'''

class Inheritance(vppfs.VPPModelElement):
    """ This class represents a 'Association' VPPModelElement.
        In UML, this is just a namespace name.
        It will contain the IDs of the classes that are contained within.
    """

    def __init__(self, baseclass, table_vppmodelelements, is_realization):
        self.ID = baseclass.ID
        self.MODEL_TYPE = baseclass.MODEL_TYPE
        self.PARENT_ID = baseclass.PARENT_ID
        self.NAME = baseclass.NAME
        self.BLOB_STRING = baseclass.BLOB_STRING
        self.table_vppmodelelements = table_vppmodelelements
        self.dict_from_BLOB_STRING = {}
        self.IS_REALIZATION = is_realization

        self.CLASS_FROM = ""  # For some reason these are not fully qualified. So this is just for debug.
        self.CLASS_FROM_ID = ""  # Perhaps the class needs to be gotten when generating code that uses this...
        self.CLASS_TO = ""  # For some reason these are not fully qualified. So this is just for debug.
        self.CLASS_TO_ID = ""  # Perhaps the class needs to be gotten when generating code that uses this...

        self.Parse()

    def Parse(self):
        self.dict_from_BLOB_STRING = vppfs.ParseBLOB_Recursive(self.BLOB_STRING)
        #vppfs.Print_RecursiveParsed_BLOB(self.dict_from_BLOB_STRING)

        for k, v in self.dict_from_BLOB_STRING.items():
            if k.lower().find('child') > -1:
                self.CLASS_FROM = GetNestedTypeNamesFromNestedTypeIDS(v['fromModel_0'],self.table_vppmodelelements)
                self.CLASS_FROM_ID = v['fromModel_0'].split(':')[-1]  # -1 = last element...gotto love python
                self.CLASS_TO = GetNestedTypeNamesFromNestedTypeIDS(v['toModel_0'],self.table_vppmodelelements)
                self.CLASS_TO_ID = v['toModel_0'].split(':')[-1]  # -1 = last element...gotto love python

    def PostProjectParseFix(self, classDiagram):
        try:
            cl_fr = classDiagram.classes[self.CLASS_FROM_ID]
            self.CLASS_FROM = cl_fr.NAMESPACE + "::" + cl_fr.NAME
        except KeyError:
            print("Warning : class " + self.CLASS_FROM + " does not exist.")

        try:
            cl_to = classDiagram.classes[self.CLASS_TO_ID]
            self.CLASS_TO = cl_to.NAMESPACE + "::" + cl_to.NAME
        except KeyError:
            print("Warning : class " + self.CLASS_TO + " does not exist.")



'''----------------------------------------------------------------------'''


class Association(vppfs.VPPModelElement):
    """ This class represents a 'Association' VPPModelElement.
        In UML, this is just a namespace name.
        It will contain the IDs of the classes that are contained within.
    """

    '''
    <ASSOCIATION> 
    http://icarus.cs.weber.edu/~dab/cs1410/textbook/11.Relationships/association.html
    class B{
        A* a;
    };
    class A{
        B* b;
    };
    
    <AGGREGATION>
    http://icarus.cs.weber.edu/~dab/cs1410/textbook/11.Relationships/aggregation.html
    class B {};
    class A
    {
        B* b;
    };
    
    <COMPOSITION>
    class B {};
    class A
    {
        B b;
    };
    '''

    def __init__(self, baseclass, table_vppmodelelements):
        self.ID = baseclass.ID
        self.MODEL_TYPE = baseclass.MODEL_TYPE
        self.PARENT_ID = baseclass.PARENT_ID
        self.NAME = baseclass.NAME
        self.BLOB_STRING = baseclass.BLOB_STRING
        self.table_vppmodelelements = table_vppmodelelements
        self.dict_from_BLOB_STRING = {}
        self.TYPE = "Association"
        self.USER_COMMENTS = ""
        self.CLASS_FROM = ""
        self.CLASS_FROM_ID = ""  # Perhaps the class needs to be gotten when generating code that uses this...
        self.CLASS_FROM_VISIBILITY = "private"
        self.CLASS_FROM_IS_STATIC = False
        self.CLASS_FROM_IS_CONST = False
        self.CLASS_FROM_MULTIPLICITY = "0..1" # 'Class From' multiplicity of 0 does not make sense with composition.
        self.CLASS_FROM_HAS_GETTER = False
        self.CLASS_FROM_HAS_SETTER = False
        self.CLASS_TO = ""
        self.CLASS_TO_ID = ""  # Perhaps the class needs to be gotten when generating code that uses this...
        self.CLASS_TO_VISIBILITY = "private"
        self.CLASS_TO_IS_STATIC = False
        self.CLASS_TO_IS_CONST = False
        self.CLASS_TO_MULTIPLICITY = "0..1"  # This only makes sense in an association where both know about each other...
        self.CLASS_TO_HAS_GETTER = False
        self.CLASS_TO_HAS_SETTER = False
        self.Parse()

    def Parse(self):
        self.dict_from_BLOB_STRING = vppfs.ParseBLOB_Recursive(self.BLOB_STRING)
        #vppfs.Print_RecursiveParsed_BLOB(self.dict_from_BLOB_STRING)
        self.ParseAssociation()

    def ParseAssociation(self):
        for k, v in self.dict_from_BLOB_STRING.items():
            if 'documentation_plain' in v:
                self.USER_COMMENTS = v['documentation_plain']
            if k.lower().find('child') > -1:
                for kk, vv in v.items():
                    if kk.lower().find('child') > -1:
                        if vv:
                            if vv['type'].lower().find('associationend') != -1:
                                for kkk, vvv in vv.items():
                                    if kkk.lower().find('child') > -1:
                                        # Direction ...
                                        if vvv['Direction'] == '0':
                                            self.CLASS_FROM = GetNestedTypeNamesFromNestedTypeIDS(vvv['EndModelElement_0'], self.table_vppmodelelements)
                                            self.CLASS_FROM_ID = vvv['EndModelElement_0'].split(':')[-1]  # -1 = last element...gotto love python
                                        elif vvv['Direction'] == '1':
                                            self.CLASS_TO = GetNestedTypeNamesFromNestedTypeIDS(vvv['EndModelElement_0'], self.table_vppmodelelements)
                                            self.CLASS_TO_ID = vvv['EndModelElement_0'].split(':')[-1]  # -1 = last element...gotto love python
                                        # TYPE
                                        if 'aggregationKind' in vvv:
                                            if vvv['aggregationKind'] == AGGREGATION_KIND__AGGREGATE:
                                                self.TYPE = "Aggregation"
                                            elif vvv['aggregationKind'] == AGGREGATION_KIND__COMPOSITE:
                                                self.TYPE = "Composition"
                                        # Multiplicity ...
                                        if 'multiplicity' in vvv:
                                            m = vvv['multiplicity']
                                            if vvv['Direction'] == '0':
                                                self.CLASS_FROM_MULTIPLICITY = m
                                            elif vvv['Direction'] == '1':
                                                self.CLASS_TO_MULTIPLICITY = m
                                        else:
                                            # Set defaults depending on aggregation.
                                            if vvv['Direction'] == '0':
                                                if self.TYPE == "Composition":  # composition means, the class 'from' has an value (not a pointer) of the class 'to' ... thus can not be '0'
                                                    self.CLASS_FROM_MULTIPLICITY = "1"
                                            elif vvv['Direction'] == '1':
                                                if self.TYPE != "Association":  # If it is NOT association, then the class 'to' knows nothing about the class from (its a one way relationship).
                                                    self.CLASS_TO_MULTIPLICITY = '0'
                                        # Visibility
                                        # 'package' to me makes most sense as public, and static.
                                        # However, it appears that 'private' is the default...and thus signified by 'visibility' not being set here...
                                        if 'visibility' in vvv:
                                            vis = vvv['visibility']
                                            if vis == Visibility.Package:
                                                if vvv['Direction'] == '0':
                                                    self.CLASS_FROM_IS_STATIC = True
                                                elif vvv['Direction'] == '1':
                                                    self.CLASS_TO_IS_STATIC = True
                                            else:
                                                if vvv['Direction'] == '0':
                                                    self.CLASS_FROM_VISIBILITY = VisibilityToHumanReadableString(vis)
                                                elif vvv['Direction'] == '1':
                                                    self.CLASS_TO_VISIBILITY = VisibilityToHumanReadableString(vis)
                                        # Getter/Setter
                                        if 'providePropertyGetterMethod' in vvv:
                                            if vvv['Direction'] == '0':
                                                self.CLASS_FROM_HAS_GETTER = True
                                            elif vvv['Direction'] == '1':
                                                self.CLASS_TO_HAS_GETTER = True
                                        if 'providePropertySetterMethod' in vvv:
                                            if vvv['Direction'] == '0':
                                                self.CLASS_FROM_HAS_SETTER = True
                                            elif vvv['Direction'] == '1':
                                                self.CLASS_TO_HAS_SETTER = True
                                        # Readonly (const)
                                    if 'readOnly' in vvv:
                                        if vvv['Direction'] == '0':
                                            self.CLASS_FROM_IS_CONST = True
                                        elif vvv['Direction'] == '1':
                                            self.CLASS_TO_IS_CONST = True


'''----------------------------------------------------------------------'''


class Package(vppfs.VPPModelElement):
    """ This class represents a 'Package' VPPModelElement.
        In UML, this is just a namespace name.
        It will contain the IDs of the classes that are contained within.
    """
    def __init__(self, baseclass):
        self.ID = baseclass.ID
        self.MODEL_TYPE = baseclass.MODEL_TYPE
        self.PARENT_ID = baseclass.PARENT_ID
        self.NAME = baseclass.NAME
        self.BLOB_STRING = baseclass.BLOB_STRING
        # from UML Package (as a package can be nested within a package)...
        self.NAMESPACE = ""
        self.dict_from_BLOB_STRING = {}
        self.CLASSES_IN_PACKAGE = []
        self.Parse()

    def Parse(self):
        self.dict_from_BLOB_STRING = vppfs.ParseBLOB_Recursive(self.BLOB_STRING)
        self.ParseClassesInPackage()
        #Print_RecursiveParsed_BLOB(self.dict_from_BLOB_STRING)
        #print(self.BLOB_STRING)

    def ParseClassesInPackage(self):
        """ Returns the IDs of all the classes contained within (in a list)
        """
        for k, v in self.dict_from_BLOB_STRING.items():
            if k.lower().find('child') > -1:
                for kk, vv in v.items():
                    if kk.lower().find('child') > -1:
                        if isinstance(vv, str):  # there could be a child that is a dict
                            # Child_0 = pqLlew6GAqAA7wvG:4bxByw6GAqAA7wcw -> where THIS_ID:CLASS_ID
                            # Keep the fully qualified class here...it will be all nesting...so the namespace can be worked out at the end...
                            self.CLASSES_IN_PACKAGE.append(vv.strip())


'''----------------------------------------------------------------------'''


class ClassAttribute:
    def __init__(self, container, table_vppmodelelements):
        # Attribute Name
        self.NAME = ""
        if container:
            self.NAME = container['name']
        self.VISIBILITY = 'private'  # appears to be the default. So, when set to 'private' there is no attribute...
        self.TYPE_MODIFIER = ""
        self.USER_COMMENTS = ""
        self.TYPE = "void"
        self.MULTIPLICITY = ""
        self.UNIQUE = False
        self.HAS_SETTER = False
        self.HAS_GETTER = False
        self.IS_STATIC = False
        self.IS_CONST = False
        self.INITIAL_VALUE = None

        if not container or not table_vppmodelelements:
            return

        child_0 = container['child_0']
        # Attribute Visibility
        if 'visibility' in child_0:
            self.VISIBILITY = VisibilityToHumanReadableString(child_0['visibility'])
        # Attribute Type Modifier
        if 'typeModifier' in child_0:
            self.TYPE_MODIFIER = child_0['typeModifier']
        # Attribute Type ... dont allow users to put eg &,*,[] here...these should be in the modifier...force them
        if 'type_0' in child_0:
            self.TYPE = CleanModifiersFromType(GetNestedTypeNamesFromNestedTypeIDS(child_0['type_0'], table_vppmodelelements))
        # User documentation about this function
        if 'documentation_plain' in child_0:
            self.USER_COMMENTS = child_0['documentation_plain']
        # User requested setter
        if 'hasSetter' in child_0:
            self.HAS_SETTER = True
        # User requested getter
        if 'hasGetter' in child_0:
            self.HAS_GETTER = True
        # Static means the scope is 'classifier', meaning for all of the classifier of the class
        if 'scope' in child_0:
            if child_0['scope'] == SCOPE_CLASSIFIER:
                self.IS_STATIC = True
        if 'initialValue_string' in child_0:
            self.INITIAL_VALUE = child_0['initialValue_string']
        if 'readOnly' in child_0:
            self.IS_CONST = True
            # however, a const attribute MUST have an initial value...
            #if self.INITIAL_VALUE is None:
            #	raise Exception("'Read-only (const)' marked class attribute '" + self.NAME + "' requires an initial value to be set.")
            # Actually...rather create a special constructor for this...fuck.
        if 'multiplicity' in child_0:
            self.MULTIPLICITY = child_0['multiplicity']

    def From(self, NAME, TYPE, TYPE_ID, MODIFIER, MULTIPLICITY, IS_STATIC, IS_CONST, VISIBILITY, HAS_GETTER, HAS_SETTER, USER_COMMENTS):
        self.NAME = NAME
        self.ID = TYPE_ID
        self.TYPE_MODIFIER = MODIFIER
        self.USER_COMMENTS = ""
        self.TYPE = TYPE
        self.VISIBILITY = VISIBILITY
        self.MULTIPLICITY = MULTIPLICITY
        self.USER_COMMENTS = USER_COMMENTS
        self.UNIQUE = False
        self.HAS_SETTER = HAS_SETTER
        self.HAS_GETTER = HAS_GETTER
        self.IS_STATIC = IS_STATIC
        self.IS_CONST = IS_CONST
        self.INITIAL_VALUE = None


class ClassOperation:
    def __init__(self, container, table_vppmodelelements):
        # Operation Name
        self.NAME = container['name']
        self.VISIBILITY = 'public'
        self.RETURN_TYPE = "void"
        self.RETURN_TYPE_MODIFIER = ""
        self.PARAMETERS = []
        self.USER_COMMENTS = ""
        self.VIRTUAL = False
        self.IS_STATIC = False
        self.IS_CONST = False

        child_0 = container['child_0']
        # Operation Visibility
        if 'visibility' in child_0:
            self.VISIBILITY = VisibilityToHumanReadableString(child_0['visibility'])
            # Second static option? 'visibility' = package...make it public and static.
            if self.VISIBILITY.lower().strip() == "package":
                self.IS_STATIC = True
                self.VISIBILITY = "public"

        # Operation Return Type -> if someone does not set this...then assume it is void.
        if 'returnType_0' in child_0:  # ... dont allow users to put eg &,*,[] here...these should be in the modifier...force them
            self.RETURN_TYPE = CleanModifiersFromType(GetNestedTypeNamesFromNestedTypeIDS(child_0['returnType_0'], table_vppmodelelements))
        if 'typeModifier' in child_0:
            self.RETURN_TYPE_MODIFIER = child_0['typeModifier']
        # Parameters
        for k, v in child_0.items():
            if k.find("child") > -1:
                if v:  # test for empty dictionary (empty dictionaries evaluate to False)
                    if 'parameter' == v['type'].lower():
                        v_child_0 = v['child_0']
                        # Options here : a parameter is a either a basic type (int, double), or a model element (namespace::class)...
                        type_s = ""  # ... dont allow users to put eg &,*,[] here...these should be in the modifier...force them
                        if 'type_string' in v_child_0:  # basic type
                            type_s = CleanModifiersFromType(v_child_0['type_string'])
                        else:
                            type_s = CleanModifiersFromType(GetNestedTypeNamesFromNestedTypeIDS(v_child_0['type_0'], table_vppmodelelements))
                        # IN parameters cant be changed...const...
                        const = ""
                        direction = "inout"
                        if 'direction' in v_child_0:
                            if v_child_0['direction'] == DIRECTION_IN:  # An 'in' parameter, even if its a pointer, is CONST...for C++. For other languages...different! so pass the direction...
                                const = "const"
                                direction = "in"
                            if v_child_0['direction'] == DIRECTION_OUT:
                                direction = "out"
                        # undefined type modifier means nothing...
                        typemodifier = ""
                        if 'typeModifier' in v_child_0:
                            typemodifier = v_child_0['typeModifier']
                        # default value
                        defaultvalue = ""
                        if 'defaultValue_string' in v_child_0:
                            defaultvalue = v_child_0['defaultValue_string']
                        multiplicity = ""
                        if 'multiplicity' in v_child_0:
                            multiplicity = v_child_0["multiplicity"]
                        param = {'const': const, 'type': type_s, 'name': v['name'], 'modifier': typemodifier, 'defaultvalue': defaultvalue, 'multiplicity': multiplicity, 'direction':direction}
                        self.PARAMETERS.append(param)
        # User documentation about this function
        if 'documentation_plain' in child_0:
            self.USER_COMMENTS = child_0['documentation_plain']
        # Is this member abstract
        if 'abstract' in child_0:
            self.VIRTUAL = True
        ''' IS this member const? Declaring a member function with the const keyword specifies that the function is 
            a "read-only" function that does not modify the object for which it is called. 
            If func does not change anything on it ( it can change on Logger) It can be "labeled" as "query".
        '''
        if 'query' in child_0:
            self.IS_CONST = True
        # Static means the scope is 'classifier', meaning for all of the classifier of the class
        if 'scope' in child_0:
            if child_0['scope'] == SCOPE_CLASSIFIER:
                self.IS_STATIC = True


class Class(vppfs.VPPModelElement):
    """ This class represents a 'Class' VPPModelElement.
        All VPPModelElement comments hold true. This class is specialized
        with more fields : 'from state', 'to state', 'guard' and 'activity'.
        These added fields are the model element id's of the corresponding model elements.
        These are added via trickery in the 'Parse' function.
    """

    def __init__(self, baseclass, parent_classDiagram):
        self.parent_classDiagram = parent_classDiagram
        self.ID = baseclass.ID
        self.MODEL_TYPE = baseclass.MODEL_TYPE
        self.PARENT_ID = baseclass.PARENT_ID
        self.NAME = baseclass.NAME
        self.BLOB_STRING = baseclass.BLOB_STRING
        self.dict_from_BLOB_STRING = {}
        # From stereotypes/flags
        self.PURE_VIRTUAL_INTERFACE = False
        self.AUTOGEN = False
        self.USER_COMMENTS = ""
        # from UML Package
        self.NAMESPACE = ""
        # from blob
        self.OPERATIONS = []
        self.ATTRIBUTES = []
        # Enum support
        self.IS_ENUM = False
        self.ENUM_LITERALS = []
        # Struct support
        self.IS_STRUCT = False
        self.IS_STRUCT_PACKED = False

        self.Parse()

    def ParseStereotypesAbstractAndDocs(self):
        """ Parse stereotypes.
            For 'interface' : pure virtual...
            For 'autogen' : the class will already be generated (i.e. statemachine, or protocol)...so don't regenerate.

            If the user has marked the class as 'abstract' this does the same as having the 'interface' stereotype
        """
        for k, v in self.dict_from_BLOB_STRING.items():
            if k.lower().find('child') > -1:
                for kk, vv in v.items():
                    if kk.lower().find('stereotype') > -1:
                        stereotype = self.parent_classDiagram.table_vppmodelelements.GetModelElement(vv)
                        if stereotype.NAME.lower().find("interface") != -1:
                            self.PURE_VIRTUAL_INTERFACE = True
                        elif stereotype.NAME.lower().find("autogen") != -1:
                            self.AUTOGEN = True
                        elif stereotype.NAME.lower().find("enumeration") != -1:
                            self.IS_ENUM = True
                        elif stereotype.NAME.lower().find("struct") != -1:
                            self.IS_STRUCT = True
                            if stereotype.NAME.lower().find("packed") != -1:
                                self.IS_STRUCT_PACKED = True
                        else:
                            print("Class : unhandled stereotype : " + stereotype.NAME)
                    elif kk.lower().find('abstract') > -1:
                        self.PURE_VIRTUAL_INTERFACE = True
                    elif kk.lower().find('documentation_plain') > -1:
                        self.USER_COMMENTS = vv
                    elif kk.lower().find('child') > -1:
                        if self.IS_ENUM:
                            # Get enumeration literals...
                            if 'type' in vv:
                                if vv['type'].lower().strip() == 'enumerationliteral':
                                    self.ENUM_LITERALS.append(vv['name'].strip())

    def ParseAttributes(self):
        for k, v in self.dict_from_BLOB_STRING.items():
            if k.lower().find('child') > -1:
                for kk, vv in v.items():
                    if kk.lower().find('child') > -1:
                        if vv:  # An empty dictionary evaluates to False
                            if "attribute" == vv['type'].lower():
                                op = ClassAttribute(vv, self.parent_classDiagram.table_vppmodelelements)
                                self.ATTRIBUTES.append(op)

    def ParseOperations(self):
        for k, v in self.dict_from_BLOB_STRING.items():
            if k.lower().find('child') > -1:
                for kk, vv in v.items():
                    if kk.lower().find('child') > -1:
                        if vv:  # An empty dictionary evaluates to False
                            if "operation" == vv['type'].lower():
                                op = ClassOperation(vv, self.parent_classDiagram.table_vppmodelelements)
                                self.OPERATIONS.append(op)

    def Parse(self):
        self.dict_from_BLOB_STRING = vppfs.ParseBLOB_Recursive(self.BLOB_STRING)
        # To look at the structure
        # vppfs.Print_RecursiveParsed_BLOB(self.dict_from_BLOB_STRING)
        self.ParseStereotypesAbstractAndDocs()
        self.ParseOperations()
        self.ParseAttributes()
        #print(self.BLOB_STRING)

    # Helpers...
    def GetNotForwardDeclarableNonPrimitiveTypesLinkedToThis(self):
        """
        Get all classes (fully qualified i.e. "NS1::NS2::CClass") for non-primitive types,
        related to this class, that can not be forward declared.

        Need to inspect
            - inheritance
            - the attributes
            - the operation parameters
            - operation return type
            - associations

        @return: set
        """
        filterValue = set()
        # INHERITANCE
        for id, inheritance in self.parent_classDiagram.inheritence.items():
            if inheritance.CLASS_TO_ID.find(self.ID) > -1:
                if not IsTypePrimitive(inheritance.CLASS_FROM):  # -> YOU never know who may do such a thing.
                    filterValue.add(inheritance.CLASS_FROM)
        # ATTRIBUTES
        for attr in self.ATTRIBUTES:
            if not IsTypePrimitive(attr.TYPE):
                if not IsTypePointerOrRef(attr.TYPE_MODIFIER):
                    filterValue.add(attr.TYPE)
        # OPERATION PARAMS and RETURN TYPE
        for oper in self.OPERATIONS:
            # Operation params
            for params in oper.PARAMETERS:
                modifier = params['modifier']
                type = params['type']
                if not IsTypePrimitive(type):
                    if not IsTypePointerOrRef(modifier):
                        filterValue.add(type)
            # return type
            if not IsTypePrimitive(oper.RETURN_TYPE):
                if not IsTypePointerOrRef(oper.RETURN_TYPE_MODIFIER):
                    filterValue.add(oper.RETURN_TYPE)
        # Associations
        for id, assoc in self.parent_classDiagram.associations.items():
            # This is the only association where it will not be a pointer.
            if assoc.CLASS_FROM_ID == self.ID:
                if assoc.TYPE.lower().find("composition") > -1:
                    if not IsTypePrimitive(assoc.CLASS_TO):  # -> YOU never know who may do such a thing.
                        filterValue.add(assoc.CLASS_TO)
        return filterValue

    def GetForwardDeclarableNonPrimitiveTypesLinkedToThis(self):
        """
        Get all classes (full qualified i.e. "NS1::NS2::CClass") for non-primitive types,
        related to this class, that can be forward declared.

         Need to inspect
            - the attributes
            - the operation parameters
            - operation return type
            - associations

        NOTE: take into account the fact that a ref/ptr AND value can declared...

        @return: set
        """
        filterPtrOrRef = set()
        filterValue = set()
        # ATTRIBUTES
        for attr in self.ATTRIBUTES:
            if not IsTypePrimitive(attr.TYPE):
                if IsTypePointerOrRef(attr.TYPE_MODIFIER):
                    filterPtrOrRef.add(attr.TYPE)
                else:
                    filterValue.add(attr.TYPE)
        # OPERATION PARAMS and RETURN TYPE
        for oper in self.OPERATIONS:
            # Operation params
            for params in oper.PARAMETERS:
                modifier = params['modifier']
                type = params['type']
                if not IsTypePrimitive(type):
                    if IsTypePointerOrRef(modifier):
                        filterPtrOrRef.add(type)
                    else:
                        filterValue.add(type)
            # return type
            if not IsTypePrimitive(oper.RETURN_TYPE):
                if IsTypePointerOrRef(oper.RETURN_TYPE_MODIFIER):
                    filterPtrOrRef.add(oper.RETURN_TYPE)
                else:
                    filterValue.add(oper.RETURN_TYPE)
        # Associations
        for id, assoc in self.parent_classDiagram.associations.items():
            # These are the only association where it will be a pointer.
            if assoc.TYPE.lower().find("association") > -1:  # This is the only one where it is bidirectional
                if assoc.CLASS_FROM_ID == self.ID:
                    if not IsTypePrimitive(assoc.CLASS_TO):  # -> YOU never know who may do such a thing.
                        filterPtrOrRef.add(assoc.CLASS_TO)
                elif assoc.CLASS_TO_ID == self.ID:
                    if not IsTypePrimitive(assoc.CLASS_FROM):  # -> YOU never know who may do such a thing.
                        filterPtrOrRef.add(assoc.CLASS_FROM)
            if assoc.TYPE.lower().find("aggregation") > -1:  # This is the only one where it is bidirectional
                if assoc.CLASS_FROM_ID == self.ID:
                    if not IsTypePrimitive(assoc.CLASS_TO):  # -> YOU never know who may do such a thing.
                        filterPtrOrRef.add(assoc.CLASS_TO)

        # In this case, if the type is in both, the value makes it not-forward-declarable...so remove.
        for i in filterValue:
            if i in filterPtrOrRef:
                filterPtrOrRef.remove(i)

        return filterPtrOrRef

    def GetAssociationsAsListOfAttributesPerVisibility(self, visibility="all"):
        """
        Returns a [] of Associations for this class as ClassAttributes for the desired visibility
         - public
         - protected
         - private
         - all (public and protected and private)
        @param visibility: string
        """
        result = []
        for id, assoc in self.parent_classDiagram.associations.items():
            # This is the only association where it will not be a pointer.
            if assoc.TYPE.lower().find("composition") > -1:
                if assoc.CLASS_FROM_ID == self.ID:
                    if visibility.lower().strip() == assoc.CLASS_FROM_VISIBILITY.lower().strip() or visibility.lower().strip() == "all":
                        if not IsTypePrimitive(assoc.CLASS_TO):  # -> YOU never know who may do such a thing.
                            c = ClassAttribute(None, None)
                            name = CleanName(assoc.NAME)
                            if not name:
                                name = "m_" + assoc.CLASS_TO.replace(self.NAMESPACE + "::", "").replace("::", "_")
                            c.From(name, assoc.CLASS_TO, assoc.CLASS_TO_ID, "", assoc.CLASS_FROM_MULTIPLICITY, assoc.CLASS_FROM_IS_STATIC, assoc.CLASS_FROM_IS_CONST, assoc.CLASS_FROM_VISIBILITY, assoc.CLASS_FROM_HAS_GETTER, assoc.CLASS_FROM_HAS_SETTER, assoc.USER_COMMENTS)
                            c.VISIBILITY = assoc.CLASS_FROM_VISIBILITY
                            result.append(c)
            # These are the only association where it will be a pointer.
            if assoc.TYPE.lower().find("association") > -1:  # This is the only one where it is bidirectional
                # This is also the only type of association whereby a child can contain a parent, and be itself (i.e. composite).
                is_composite = assoc.CLASS_FROM_ID == self.ID and assoc.CLASS_TO_ID == self.ID
                if assoc.CLASS_FROM_ID == self.ID:
                    if visibility.lower().strip() == assoc.CLASS_FROM_VISIBILITY.lower().strip() or visibility.lower().strip() == "all":
                        if not IsTypePrimitive(assoc.CLASS_TO):  # -> YOU never know who may do such a thing.
                            c = ClassAttribute(None, None)
                            name = CleanName(assoc.NAME)
                            if not name or is_composite:
                                name = "m_" + ("child_" if is_composite else "") + assoc.CLASS_TO.replace(self.NAMESPACE + "::", "").replace("::", "_")
                            c.From(name, assoc.CLASS_TO, assoc.CLASS_TO_ID, "*", assoc.CLASS_FROM_MULTIPLICITY, assoc.CLASS_FROM_IS_STATIC, assoc.CLASS_FROM_IS_CONST, assoc.CLASS_FROM_VISIBILITY, assoc.CLASS_FROM_HAS_GETTER, assoc.CLASS_FROM_HAS_SETTER, assoc.USER_COMMENTS)
                            c.VISIBILITY = assoc.CLASS_FROM_VISIBILITY
                            result.append(c)
                if assoc.CLASS_TO_ID == self.ID:
                    if visibility.lower().strip() == assoc.CLASS_TO_VISIBILITY.lower().strip() or visibility.lower().strip() == "all":
                        if not IsTypePrimitive(assoc.CLASS_FROM):  # -> YOU never know who may do such a thing.
                            c = ClassAttribute(None, None)
                            name = CleanName(assoc.NAME)
                            if not name or is_composite:
                                name = "m_" + ("parent_" if is_composite else "") + assoc.CLASS_FROM.replace(self.NAMESPACE + "::", "").replace("::", "_")
                            c.From(name, assoc.CLASS_FROM, assoc.CLASS_FROM_ID, "*", assoc.CLASS_TO_MULTIPLICITY, assoc.CLASS_TO_IS_STATIC, assoc.CLASS_TO_IS_CONST, assoc.CLASS_TO_VISIBILITY, assoc.CLASS_TO_HAS_GETTER, assoc.CLASS_TO_HAS_SETTER, assoc.USER_COMMENTS)
                            c.VISIBILITY = assoc.CLASS_TO_VISIBILITY
                            result.append(c)
            if assoc.TYPE.lower().find("aggregation") > -1:  # This is the only one where it is bidirectional
                if assoc.CLASS_FROM_ID == self.ID:
                    if visibility.lower().strip() == assoc.CLASS_FROM_VISIBILITY.lower().strip() or visibility.lower().strip() == "all":
                        if not IsTypePrimitive(assoc.CLASS_TO):  # -> YOU never know who may do such a thing.
                            c = ClassAttribute(None, None)
                            name = CleanName(assoc.NAME)
                            if not name:
                                name = "m_" + assoc.CLASS_TO.replace(self.NAMESPACE + "::", "").replace("::", "_")
                            c.From(name, assoc.CLASS_TO, assoc.CLASS_TO_ID, "*", assoc.CLASS_FROM_MULTIPLICITY, assoc.CLASS_FROM_IS_STATIC, assoc.CLASS_FROM_IS_CONST, assoc.CLASS_FROM_VISIBILITY, assoc.CLASS_FROM_HAS_GETTER, assoc.CLASS_FROM_HAS_SETTER, assoc.USER_COMMENTS)
                            c.VISIBILITY = assoc.CLASS_FROM_VISIBILITY
                            result.append(c)
        return result

    def GetContainerMultiplicityType(self, MULTIPLICITY):
        """
        Will determine the container type based on multiplicity.

        @param MULTIPLICITY:
        @return: 'vector', 'array' or 'none'
        """
        if MULTIPLICITY.find("*") != -1:  # vector
            return 'vector'
        elif MULTIPLICITY.find("0..1") != -1:
            return 'none'
        elif MULTIPLICITY.find("0..*") != -1:  # vector
            return 'vector'
        elif MULTIPLICITY.find("1..*") != -1:  # vector
            return 'vector'
        elif MULTIPLICITY.find("..") > -1:
            numbers = MULTIPLICITY.split("..")
            try:  # Array
                i = int(numbers[-1])
                return 'array:' + str(i)
            except ValueError:  # vector
                return 'vector'
        elif MULTIPLICITY.find("0") != -1:
            return 'none'
        elif MULTIPLICITY.find("1") != -1:
            return 'none'
        else:  # lastly...perhaps someone put an actual value here...then its an array.
            try:  # Array
                i = int(MULTIPLICITY)
                return 'array:' + str(i)
            except ValueError:
                return 'none'
        return 'none'

    def DoAttributesAssociationsReturnTypesOrFunctionParametersRequireVector(self):
        """
        @return: True or False if any attributes, associations or operation-parameters use a vector (based on multiplicity)
        """
        has_Vector = False
        for attr in self.ATTRIBUTES:
            if not has_Vector and self.GetContainerMultiplicityType(attr.MULTIPLICITY).find("vector") > -1:
                has_Vector = True

        if not has_Vector:
            associations_as_attributes = self.GetAssociationsAsListOfAttributesPerVisibility("all")
            for attr in associations_as_attributes:
                if not has_Vector and self.GetContainerMultiplicityType(attr.MULTIPLICITY).find("vector") > -1:
                    has_Vector = True

        if not has_Vector:
            for oper in self.OPERATIONS:
                for param in oper.PARAMETERS:
                    if not has_Vector and self.GetContainerMultiplicityType(param['multiplicity']).find("vector") > -1:
                        has_Vector = True;
                # Search for <!#!>
                if oper.RETURN_TYPE_MODIFIER.strip().find("[]") > -1:
                    has_Vector = True

        # Also look at any members from interfaces !
        for id, inheritance in self.parent_classDiagram.inheritence.items():
            if inheritance.CLASS_TO_ID.find(self.ID) > -1:
                if inheritance.IS_REALIZATION:# or REALIZING_CLASS:  # or REALIZING_CLASS -> if a pure virtual interface inherits another pure virtual interface, and the top child class that inherits them all wants to realize, then all should be realized
                    # get the class we are realizing...
                    realizeObj = self.parent_classDiagram.classes[inheritance.CLASS_FROM_ID]
                    if realizeObj.PURE_VIRTUAL_INTERFACE:
                        has_Vector = has_Vector or realizeObj.DoAttributesAssociationsReturnTypesOrFunctionParametersRequireVector()

        return has_Vector


'''----------------------------------------------------------------------'''


class ClassDiagram:
    """ This class represents a class diagram for a particular diagram of 'name' and 'id'.
        The name and the id of the diagram are passed into the constructor.
        The diagram elements from the project are also passed into the constructor (from the diagram elements table)
        as well as the model elements table.

        This class will use the diagram elements to lookup all the necessary model elements from the model elements table
        and create a ??? table from that.
    """

    def __init__(self, diagramName, diagramID, diagramElements, table_vppmodelelements):
        self.name = diagramName
        self.id = diagramID
        self.elements = diagramElements
        self.table_vppmodelelements = table_vppmodelelements

        self.packages = {}
        self.classes = {}
        self.associations = {}
        self.inheritence = {}
        self.usages = {}
        self.LoadAndTest()

    ''' Will load the table and hope to catch any changes (for future proofing) if VP decide to change their database. '''

    def LoadAndTest(self):
        for i in self.elements:
            vppmodelelement = self.table_vppmodelelements.GetModelElement(i.MODEL_ELEMENT_ID)
            #print("|| ", vppmodelelement.MODEL_TYPE)
            if vppmodelelement.MODEL_TYPE == 'Class':
                self.classes[vppmodelelement.ID] = Class(vppmodelelement, self)
            elif vppmodelelement.MODEL_TYPE == 'Package':
                self.packages[vppmodelelement.ID] = Package(vppmodelelement)
            elif vppmodelelement.MODEL_TYPE == 'Association':
                self.associations[vppmodelelement.ID] = Association(vppmodelelement, self.table_vppmodelelements)
            elif vppmodelelement.MODEL_TYPE == 'Realization' or vppmodelelement.MODEL_TYPE == 'Generalization':
                self.inheritence[vppmodelelement.ID] = Inheritance(vppmodelelement, self.table_vppmodelelements, vppmodelelement.MODEL_TYPE == 'Realization')
            elif vppmodelelement.MODEL_TYPE == 'Usage':
                # self.usages[vppmodelelement.ID] = Usage(vppmodelelement)
                pass
            else:
                print("Class Diagram : unhandled model-element type : ", vppmodelelement.MODEL_TYPE)

        # UML Packages are namespaces. The can be nested. This supports nesting.
        # Iterate through all packages, see what classes are in them...these will be the fully qualified (nested) range of IDS,
        # and build the namespace for the class.
        # # # > A side note : the whole idea of de-serializing packages seems moot...as the PARENT_ID member of the class objects, when embedded in a package...will be the ID for the package...
        # # # > ...and I guess the same for a package...and so that could be all that is used, by looking up and looking up etc.
        # # # > HOWEVER, if someone used another shape as a package...then that should be the namespace name...and we might have to do this.
        for _id, package in self.packages.items():
            for pclassid in package.CLASSES_IN_PACKAGE:
                fullyQualifiedNestedNamespacesAndClass = pclassid.split(':')
                namespace = ""
                for i in range(len(fullyQualifiedNestedNamespacesAndClass) - 1):
                    namespace = namespace + self.packages[fullyQualifiedNestedNamespacesAndClass[i]].NAME + "::"
                namespace = namespace.rstrip(":")  # Remove the last '::'

                for classid, _class in self.classes.items():
                    if classid == fullyQualifiedNestedNamespacesAndClass[len(fullyQualifiedNestedNamespacesAndClass) - 1]:
                        _class.NAMESPACE = namespace
                        break

        # For some reason, nest typeid's for inheritance are not fully qualified...fix this AFTER fixing namespace names.
        for id, inh in self.inheritence.items():
            inh.PostProjectParseFix(self)

    ''' Returns a dictionary of 'namespace : set()' dependencies where the set is a set of namespaces the 'key' namespace depends on.
    '''

    def GetNamespaceDependencies(self):
        result = {}
        for class_uid, classobj in self.classes.items():
            namespace = classobj.NAMESPACE
            if not namespace in result:
                result[namespace] = set()
            # These are sets. Dont add a dependancy to oneself...
            set1 = classobj.GetNotForwardDeclarableNonPrimitiveTypesLinkedToThis()
            set2 = classobj.GetForwardDeclarableNonPrimitiveTypesLinkedToThis()
            for s in set1:
                if s.find(namespace) == -1:
                    result[namespace].add(s.rpartition("::")[0])
            for s in set2:
                if s.find(namespace) == -1:
                    result[namespace].add(s.rpartition("::")[0])
        return result

''' USE THIS FUNCTION to extract a named class diagram from a VPP file.
    input : class diagram name
    input : path to the file
'''
def ExtractClassDiagram(classdiagramname, path_to_vpp):
    vppdiagrams = vppfs.VPPDiagrams(path_to_vpp)
    vppdiagramelements = vppfs.VPPDiagramElements(path_to_vpp)
    vppmodelelements = vppfs.VPPModelElements(path_to_vpp)
    elements = vppdiagramelements.GetDiagramElements(vppdiagrams.GetIDFromClassDiagramName(classdiagramname))
    class_diagram = ClassDiagram(classdiagramname, vppdiagrams.GetIDFromClassDiagramName(classdiagramname), elements, vppmodelelements)
    return class_diagram

''' USE THIS FUNCTION to extract ALL class diagrams from a VPP file.
    input : path to the file
'''
def ExtractAllClassDiagrams(path_to_vpp):
    vppdiagrams = vppfs.VPPDiagrams(path_to_vpp)
    vppdiagramelements = vppfs.VPPDiagramElements(path_to_vpp)
    vppmodelelements = vppfs.VPPModelElements(path_to_vpp)
    class_diagrams = []
    for id, name in vppdiagrams.class_diagrams.items():
        elements = vppdiagramelements.GetDiagramElements(id)
        class_diagram = ClassDiagram(name, id, elements, vppmodelelements)
        class_diagrams.append(class_diagram)
    return class_diagrams