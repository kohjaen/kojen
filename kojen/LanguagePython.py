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
try:
    from kojentypes import *
except (ModuleNotFoundError, ImportError) as e:
    from .kojentypes import *

try:
    from vppclassdiagram import *
except (ModuleNotFoundError, ImportError) as e:
    from .vppclassdiagram import *

try:
    from Language import *
except (ModuleNotFoundError, ImportError) as e:
from .Language import *


class LanguagePython(Language):

    ## Language Specifics
    # Braces
    def OpenBrace(self):
        return ''

    def CloseBrace(self):
        return ''

    # Connection type
    def ConnectionType(self):
        return 'IConnection'

    def ConnectionTypePtr(self):
        return 'IConnection'

    # Member access / dereference
    def Accessor(self, is_ptr):
        return '.'

    # Bytestream access / dereference
    def BytestreamAccessor(self):
        return '.'

    # Byte Stream
    def ByteStreamType(self):
        return 'bytearray'

    def ByteStreamTypeSharedPtr(self):
        return self.SharedPtrToType(self.ByteStreamType())

    def ByteStreamTypeRawPtr(self):
        return self.RawPtrToType(self.ByteStreamType())

    # Convenience
    def SharedPtrToType(self, typename):
        return typename

    def RawPtrToType(self, typename):
        return typename

    def TypedefSharedPtrToType(self, typename, newtypename):
        return ''

    def TypedefRawPtrToType(self, typename, newtypename):
        return ''

    def GetFactoryCreateParams(self, struct, interface, with_defaults=False) -> list:
        structmembers = struct.Decompose()
        factoryparams = []
        for mem in structmembers:
            #isMessage = interface.IsMessageStruct(mem[0])
            #isStruct = struct.IsStruct(mem[1])
            if not interface.IsProtocolStruct(mem[0]):
                if with_defaults and HasDefault(mem):
                    factoryparams.append(("", mem[1] + "=" + mem[2]))
                else:
                    factoryparams.append(("", mem[1]))
        return factoryparams

    '''Declares the guts of a struct declaration
    '''
    def DeclareStructMembers(self, struct, interface, whitespace, attr_packed=True) -> list:
        structmembers = struct.Decompose()
        result = []
        for mem in structmembers:
            result.append(whitespace + self.InstantiateType(mem[0], mem[1], mem[2] if HasDefault(mem) else 'None') + ' # ' + mem[0])
        return result

    # Packedness
    def AddAttributePackedToDecl(self, declaration):
        # http://stackoverflow.com/questions/14771150/python-ctypes-pragma-pack-for-byte-aligned-read
        return '_pack_ = 1'

    def InstantiatePtrToType(self, typename, instancename):
        return instancename + ' = ' + typename + '()'

    def InstantiateArray(self, instancename, typename, noelements):
        return instancename + ' = ' + typename + '('+noelements+')\n'

    def DeleteArray(self, instancename):
        return 'del ' + instancename + '\n'

    def DeletePtrToType(self, instancename):
        return 'del ' + instancename + '\n'

    ''' Instantiate/declare a basic type, with optional initializer. Only declarations can use 'attribute packed' directives.
        use typename = '' to make it a known variable initialization
    '''
    def InstantiateType(self, typename, instancename, initialevalue=None, is_attr_packed=False, is_static=False, is_const=False):
        # declaration...i.e. in class or struct. no initial value, can be packed
        # if initialevalue.replace(' ','') == '':
        #    decl =  "('" + instancename + "'," + typename + ")"
        #    return decl + ',\n'

        # local variable decl/instantiation or known variable instantiation
        #return instancename + ' = ' + initialevalue
        if IsTypePrimitive(typename) or not typename.strip():
            if initialevalue:
        return instancename + ' = ' + initialevalue
            else:
                return instancename + (' = 0' if not 'string' in typename else ' = ""')
        else:
            if typename != "[]":
                if initialevalue:
                    return instancename + ' = ' + initialevalue
                else:
                    return instancename + ' = ' + typename + "()"
            else:
                if initialevalue:
                    return instancename + ' = [' + initialevalue + ']'
                else:
                    return instancename + ' = ' + typename

    def InstantiateStructMembers(self, struct, interface, whitespace, instancename, accessor) -> list:
        structmembers = struct.Decompose()
        result = []
        for mem in structmembers:
            isStruct = interface.IsStruct(mem[1])
            isProtocol = interface.IsProtocolStruct(mem[0])
            instance_accessor = whitespace + instancename + accessor

            if not isProtocol or isStruct:
                result.append(instance_accessor + self.InstantiateType('', mem[1], mem[1]))
            elif isProtocol and not isStruct:
                raise RuntimeError("C++ Copy Paste -> Language Feature Not Implemented")
            else:
                print("WTF : InstantiateStructMembers")

        return result

    def ParameterString(self,  parameters=None) -> str:
        if parameters is None:
            parameters = []

        if str(type(parameters)) == "<type 'list'>" or str(type(parameters)) == "<class 'list'>":  # Python2 gives the first, python3 the second!
            parameter_string = ''
            size = len(parameters)
            cnt = 0
            for param in parameters:
                parameter_string += param[1]
                if cnt != (size - 1):
                    parameter_string += ', '
                cnt += 1
            return parameter_string

        raise Exception("Please use OrderedDict when passing parameters into 'ParameterString'")

    # parameters need to be a list of (type, name).
    def DeclareFunction(self, returntype, classname, functionname, is_impl, parameters=None, virtual=False, is_static=False, is_const=False):
        # def DeclareFunction(self, returntype, classname, functionname, is_impl, parameters=[], virtual=False):
        # https://florimond.dev/blog/articles/2018/08/python-mutable-defaults-are-the-source-of-all-evil/
        if parameters is None:
            parameters = []
        if not is_impl:
            return ''

        if str(type(parameters)) == "<type 'list'>" or str(type(parameters)) == "<class 'list'>":  # Python2 gives the first, python3 the second!
            parameter_string = ''

            size = len(parameters)
            cnt = 0
            for param in parameters:
                parameter_string += param[1]
                if cnt != (size - 1):
                    parameter_string += ', '
                cnt += 1

            return 'def ' + functionname + '(' + parameter_string + ')' + ':'

        raise Exception("Please use list when passing parameters into 'DeclareFunction'")

    def DeclareClass(self, classname, declspec=''):
        return 'class ' + classname + ':\n'

    def ForwareDeclareClass(self, classname):
        return ''

    def DeclareStruct(self, structname, declspec=''):
        """c-type structs here
        # http://stackoverflow.com/questions/14771150/python-ctypes-pragma-pack-for-byte-aligned-read
        """
        result = 'class ' + structname + '(Structure):\n'
        result += self.AddAttributePackedToDecl('') + '\n'
        result += '_fields_ = [\n'
        return result

    def DeclareEnum(self, enum, whitespace) -> str:
        result = self.FormatComment(enum.documentation) + "\n"
        result += whitespace + "@unique\n"
        result += whitespace + "class " + enum.Name + "(Enum):\n"
        for descriptionName, val in enum.items():
            result += whitespace*2 + str(descriptionName) + " = " + str(val) + "\n"
        return result

    def DeclareNamespace(self, namespacename):
        return '\n'

    def UsingNamespace(self, namespacename):
        return '\n'

    #def DeclareClassConstructor(self, classname, is_impl, parameters = OrderedDict()):

    def FormatComment(self, commenttext):
        return '# ' + commenttext

    def FormatLongComment(self, commenttext):
        return "'''\n" + commenttext + "\n'''\n"

    # The includes that each generated file needs to have from the provided mini framework
    def LanguageSpecificFrameWorkIncludes(self):
        return ['ctypes']

    def AddInclude(self, filename):  # for python we can simply replace .h with''
        return 'from ' + filename.replace('.py', '').replace('"', '').replace('<', '').replace('>', '').replace('\n', '') + ' import *\n'

    def PrintError(self, message):  # python should split the strings by '<<', as there are more arguments passed this way
        return self.PrintMessage("ERROR : " + message)

    def PrintMessage(self, message):
        result = 'print ('
        for i in message.split("<<"):
            result += "+ str(" + i + ")"
        result += ')\n'
        return result

    def BooleanTrue(self):
        return 'True'

    def BooleanFalse(self):
        return 'False'

    def NullPtr(self):  # should be NULL for C, and None for pooota
        return 'None'

    def PublicAccessSpecifier(self):
        return ''

    def ProtectedAccessSpecifier(self):
        return ''

    def PrivateAccessSpecifier(self):
        return ''

    def If(self, statement):
        return 'if '+statement+' :\n'

    def ElseIf(self, statement):
        return 'elif '+statement+' :\n'

    def Else(self):
        return 'else:\n'

    def This(self):
        return 'self.'

    ''' Additions that were added for class diagram
        '''
    def GetFormatNestedNamespaceBegin(self, classObj) -> str:
        return ""

    def GetFormatNestedNamespaceEnd(self, classObj) -> str:
        return ""

    def GetFormatClassInheritence(self, classObj, dictOfInheritance) -> str:
        """
        Returns the Python format string for class inheritence based on objects
        returned by parsing the class diagram in e.g. our favourite UML tool.

        @param classObj: class information from vppclassdiagram.Class
        @param dictOfInheritance: a dictionary of inheritence info : {'id': vppclassdiagram.Inheritance}
        @return: string with the Python inheritance for this class, e.g. "(Parent1, Parent2):"
        for "class Child(Parent1, Parent2):"
        """
        result = ""
        if isinstance(classObj, Class) and isinstance(dictOfInheritance, dict):
            for id, inheritance in dictOfInheritance.items():
                if isinstance(inheritance, Inheritance):
                    if inheritance.CLASS_TO_ID.find(classObj.ID) > -1:
                        #result = result + inheritance.CLASS_FROM.replace(classObj.NAMESPACE + "::", "").replace("::",".") + ", "
                        result = result + inheritance.CLASS_FROM[inheritance.CLASS_FROM.rfind("::")+2:] + ", "
                else:
                    raise RuntimeError("dictOfInheritance contains item not of type 'Inheritance'")
            # Python ABCs
            if classObj.PURE_VIRTUAL_INTERFACE:
                result = result + "ABC, "
        else:
            raise RuntimeError("classObj not of type 'Class' OR dictOfInheritance not of type 'dict'")

        if len(result) > 0:
            # remove last ','
            result = result.strip().rstrip(',')
            # add " : "
            result = "(" + result + "):"
        else:
            result = ":"
        return result


    # Typically what goes into a H file, when the items can NOT be forward declared in H file.
    def GetNotForwardDeclarableHeaderIncludes(self, classObj, namespace_to_folders=False, filter_out_type_not_in_model=False, include_vector_if_needed=False) -> str:
            """
                For Header files. Given a class object, and class diagram, will return a multi-line string containing all header includes
                for types that can not be forward declared (ie. to reduce include dependencies) in a header file.

                If 'namespace_to_folders' is set, then that assumes the code is output into a separate folder per namespace.

                @param classObj: the 'vppclassdiagram.Class' object that we are working out the not-forward-declarable-type header includes.
                @param namespace_to_folders: This option implies that code is generated nested, in folders, named after namespace. This affects how header files are addressed.
                @param filter_out_type_not_in_model:  Will filter out includes of classes that do not exist in the class diagram.
                @return:
            """
            if isinstance(classObj, Class):
                filter = classObj.GetNotForwardDeclarableNonPrimitiveTypesLinkedToThis()
                namespace_to_classes = _getNamespaceToClassesFromFullyQualifiedNames(classObj, filter, True)
                if filter_out_type_not_in_model:
                    namespace_to_classes = _filterOutTypesNotInModel(namespace_to_classes, classObj.parent_classDiagram)
                # remove the composite (item that includes/uses itself)
                namespace_to_classes = {key: val for key, val in namespace_to_classes.items() if not classObj.NAME in val}
                result = _getIncludeStringFromNamespaceToClassMap(namespace_to_classes, namespace_to_folders)

                # Check multiplicity of attributes / operation parameters / associations for 'array'...and include that if it needs.
                if include_vector_if_needed:
                    if classObj.DoAttributesAssociationsReturnTypesOrFunctionParametersRequireVector():
                        #result = result + '#include <vector>\n'
                        pass

                return result
            else:
                raise RuntimeError("classObj not of type 'Class'")

            # Typically what goes into a CPP file, when the items can be forward declared in H file.

    def GetForwardDeclarableHeaderIncludes(self, classObj, namespace_to_folders=False, filter_out_type_not_in_model=False) -> str:
        """
            For SOURCE files. Given a class object, and class diagram, will return a multi-line string containing all header includes
            for types that can be forward declared (ie. to reduce include dependencies) in a header file.

            If 'namespace_to_folders' is set, then that assumes the code is output into a separate folder per namespace.

            @param classObj: the 'vppclassdiagram.Class' object that we are working out the forward-declarable-type header includes.
            @param namespace_to_folders: This option implies that code is generated nested, in folders, named after namespace. This affects how header files are addressed.
        """
        if isinstance(classObj, Class):
            filter = classObj.GetForwardDeclarableNonPrimitiveTypesLinkedToThis()
            namespace_to_classes = _getNamespaceToClassesFromFullyQualifiedNames(classObj, filter, True)
            if filter_out_type_not_in_model:
                namespace_to_classes = _filterOutTypesNotInModel(namespace_to_classes, classObj.parent_classDiagram)
            result = _getIncludeStringFromNamespaceToClassMap(namespace_to_classes, namespace_to_folders)
            return result
        else:
            raise RuntimeError("classObj not of type 'Class' OR classDiagram not of type 'ClassDiagram'")

    def GetForwardDeclarations(self, classObj) -> str:
        # raise RuntimeError("Python Forward Declaration Kludge - TODO 2 - no forward decls in Python")
        return ""

    def GetTypeAndNameFromMultiplicityAndModifier(self, classObj, TYPE, TYPE_MODIFIER, MULTIPLICITY, NAME) -> list:
        """
        https://www.researchgate.net/figure/Mappings-from-C-declarations-to-UML-multiplicity-ranges-depend-on-pointer-reference_tbl1_4207986
        http://www.cs.kent.edu/~jmaletic/papers/JIST07.pdf

        @param TYPE:
        @param TYPE_MODIFIER:
        @param MULTIPLICITY:
        @param NAME:
        @return:
        """
        # Python-ify -> imports should be fully qualified...so no need for fully qualified here.
        #TYPE = TYPE.replace("::",".")
        print("***** ", TYPE, " ", NAME)
        if "::" in TYPE:
            TYPE = TYPE[TYPE.rfind("::")+2:]
        if TYPE_MODIFIER.find("*") > -1 or TYPE_MODIFIER.find("&") > -1:
            TYPE_MODIFIER = ""
        # Python-ify

        if TYPE_MODIFIER.strip() == "[]":
            if not MULTIPLICITY:  # vector
                return ["[]", NAME] # -> use a list
            #else:
            #    TYPE_MODIFIER = ""

        containerType = classObj.GetContainerMultiplicityType(MULTIPLICITY)
        if containerType.find('vector') > -1:
            return ["[]", NAME]
        elif containerType.find('array') > -1:
            #return [TYPE + TYPE_MODIFIER, NAME + "[" + containerType.split(":")[-1] + "]"]
            return ["[]", NAME ]
        return [TYPE + TYPE_MODIFIER, NAME]

    def GetProjectIncludes(self, setOfProjectDependencies) -> str:
        return ""

    def GetEnumLiterals(self, classObj) -> str:
        if not classObj.IS_ENUM:
            raise RuntimeError("Can't get enum literals from a non-Enum")
        result = ""
        for literal in classObj.ENUM_LITERALS:
            result = result + literal + " = auto()\n"
        return result

    def GetAttributeDeclarationsPerVisibility(self, classObj, visibility="all", attributes=None) -> str:
        """
        Get the declaration string for all attributes of the desired visibility
         - public
         - protected
         - private
         - all (public and protected and private)

        @param classObj: vppclassdiagram.Class
        @param visibility: string
        """
        result = ""
        no_attr_passed_in = attributes is None
        if no_attr_passed_in:
            attributes = classObj.ATTRIBUTES

        for attr in attributes:
            if visibility.lower().strip() == attr.VISIBILITY.lower().strip() or visibility.lower().strip() == 'all':
                result = result + ( "" if not attr.USER_COMMENTS else self.FormatLongComment(attr.USER_COMMENTS) )
                type_name = self.GetTypeAndNameFromMultiplicityAndModifier(classObj, attr.TYPE, attr.TYPE_MODIFIER, attr.MULTIPLICITY, attr.NAME)
                #result = result + self.InstantiateType(type_name[0], type_name[1], '', False, attr.IS_STATIC, attr.IS_CONST)
                result = result + self.InstantiateType(type_name[0], type_name[1], attr.INITIAL_VALUE, False, attr.IS_STATIC, attr.IS_CONST)
                result = result + "\n"
        if result and no_attr_passed_in:
            result = "## " + visibility.capitalize() + " attributes\n" + result + "#"
        return result.rstrip("\n")

    # ------------------------------ End

def _getNamespaceToClassesFromFullyQualifiedNames(classObj, setOfClasses, is_file_include):
    """
    In the ClassDiagramModel, all Types are full qualified, ie 'XFullStack.XProtocol.CProtocolStack'
    It is thus safe to assume that should one split on ::, if the result is one, there is no namespace.

    @param setOfClasses: Set of all classes extracted for classObj
    @param classObj:
    @return: dictionary {'NS1.NS2':'CClass'}
    """
    namespace_to_class = OrderedDict()
    # Get a dictionary of namespace names, with all classes within.
    for f in setOfClasses:
        if is_file_include:
            # If a class is in the same namespace...then it is in the same folder...so clean this first.
            f = f.replace(classObj.NAMESPACE + "::", "")
        full = f.split("::")
        ns = f.replace(full[-1], "")
        if is_file_include:  # when using this for include files, switch :: with .
            ns = ns.replace("::", ".")
        else:  # when using this for forward declarations, the extra '::' creates an empty namespace.
            #ns = ns.rstrip("::")
            raise RuntimeError("Python Forward Declaration Kludge - TODO - no forward decls in Python")
        if ns not in namespace_to_class:
            namespace_to_class[ns] = []
        namespace_to_class[ns].append(full[-1])
    return namespace_to_class

def _filterOutTypesNotInModel(namespace_to_classes, classDiagram):
    """
    Will filter out class names in the 'namespace_to_classes' structure that do not exist in the class diagram.

    @param namespace_to_classes: a dictionary of lists - {"XNameSpace1::XNameSpace2":[Class1, Class2, Class3]}
    @param classDiagram: vppclassdiagram.ClassDiagram

    """
    namespace_to_classes_only_in_model = {}
    for ns, classes in namespace_to_classes.items():
        new_classes = []
        for c in classes:
            for id, pc in classDiagram.classes.items():
                if pc.NAME == c:
                    new_classes.append(c)
        if len(new_classes) > 0:
            namespace_to_classes_only_in_model[ns] = new_classes
    return namespace_to_classes_only_in_model

def _getIncludeStringFromNamespaceToClassMap(namespace_to_class, namespace_to_folders):
    result = ""
    for path, classnames in namespace_to_class.items():
        for classname in classnames:
            if not namespace_to_folders:  # clear the path
                path = ""
            #result = result + 'from ' + path + classname + ' import *\n'
            result = result + 'from ' + (('..' + path) if path else "") + classname + ' import *\n'
    return result