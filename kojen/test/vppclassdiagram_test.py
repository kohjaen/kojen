import unittest
from kojen import vppfs
from kojen.vppclassdiagram import Visibility, ClassDiagram


class TestDecipherVPPBlobs(unittest.TestCase):
    """
    This unit test tests the deciphering of a VPP blob into a dictionary of key:value pairs
    where the values can also be further nested child objects.

    The idea is to use the same VPP project, and run the tests through the different versions of VP
    as they come available
    """
    def setUp(self):
        self.blob_Class = b'4bxByw6GAqAA7wcw:"ILayer":Class {\n\tstereotypes=(\n\t\t<zpgByw6GAqAA7wbU>\n\t);\n\t_modelEditable=T;\n\t_masterViewId="YbxByw6GAqAA7wcv";\n\tpmAuthor="ooooige";\n\tFromSimpleRelationships=(\n\t\t<sXtlKqqFYEAQWAie:KROxyw6GAqAA7wiS:8WQxyw6GAqAA7wg.>\n\t);\n\tpmCreateDateTime="1584096492935";\n\t_modelViews=(\n\t\t{ibxByw6GAqAA7wcx:"View":ModelView {\n\t\t\tcontainer=<QcgxGqqFYEAQWAnB>;\n\t\t\tview="YbxByw6GAqAA7wcv";\n\t\t}}\n\t);\n\tToEndRelationships=(\n\t\t<sXtlKqqFYEAQWAie:CROxyw6GAqAA7wiR:YGARyw6GAqAA7weJ$aGARyw6GAqAA7weO>\n\t);\n\tChild=(\n\t\t{Ef1Byw6GAqAA7wdB:"Send":Operation {\n\t\t\tvisibility=71;\n\t\t\treturnType=<F5FFKqqFYEAQWAYP>;\n\t\t\tpmLastModified="1584096608451";\n\t\t\tpmAuthor="ooooige";\n\t\t\tChild=(\n\t\t\t\t{fcDByw6GAqAA7wdE:"packet":Parameter {\n\t\t\t\t\ttypeModifier="&";\n\t\t\t\t\ttype_string="CPacket";\n\t\t\t\t\tpmLastModified="1584096608451";\n\t\t\t\t\tpmAuthor="ooooige";\n\t\t\t\t\tpmCreateDateTime="1584096543678";\n\t\t\t\t\t_modelViews=NULL;\n\t\t\t\t\t_modelEditable=T;\n\t\t\t\t}}\n\t\t\t);\n\t\t\tpmCreateDateTime="1584096526216";\n\t\t\t_modelViews=NULL;\n\t\t\t_modelEditable=T;\n\t\t}}, \n\t\t{9A3Byw6GAqAA7wdG:"Recv":Operation {\n\t\t\tvisibility=71;\n\t\t\treturnType=<F5FFKqqFYEAQWAYP>;\n\t\t\tpmLastModified="1584097249458";\n\t\t\tpmAuthor="ooooige";\n\t\t\tChild=(\n\t\t\t\t{7A3Byw6GAqAA7wdH:"packet":Parameter {\n\t\t\t\t\ttypeModifier="&";\n\t\t\t\t\ttype_string="CPacket";\n\t\t\t\t\tpmLastModified="1584096608451";\n\t\t\t\t\tpmAuthor="ooooige";\n\t\t\t\t\tpmCreateDateTime="1584096587834";\n\t\t\t\t\t_modelViews=NULL;\n\t\t\t\t\t_modelEditable=T;\n\t\t\t\t}}\n\t\t\t);\n\t\t\tpmCreateDateTime="1584096587831";\n\t\t\t_modelViews=NULL;\n\t\t\t_modelEditable=T;\n\t\t}}, \n\t\t{IVPByw6GAqAA7wdI:"Process":Operation {\n\t\t\tvisibility=71;\n\t\t\treturnType=<F5FFKqqFYEAQWAYP>;\n\t\t\tpmLastModified="1584097249458";\n\t\t\tpmAuthor="ooooige";\n\t\t\tChild=(\n\t\t\t\t{GVPByw6GAqAA7wdJ:"packet":Parameter {\n\t\t\t\t\ttypeModifier="&";\n\t\t\t\t\ttype_string="CPacket";\n\t\t\t\t\tpmLastModified="1584096608451";\n\t\t\t\t\tpmAuthor="ooooige";\n\t\t\t\t\tpmCreateDateTime="1584096594591";\n\t\t\t\t\t_modelViews=NULL;\n\t\t\t\t\t_modelEditable=T;\n\t\t\t\t}}\n\t\t\t);\n\t\t\tpmCreateDateTime="1584096594584";\n\t\t\t_modelViews=NULL;\n\t\t\t_modelEditable=T;\n\t\t}}\n\t);\n\tpmLastModified="1584097249456";\n}'
        self.blob_Package = b'pqLlew6GAqAA7wvG:"XProtocol":Package {\n\t_masterViewId="hqLlew6GAqAA7wvF";\n\tpmLastModified="1584286807443";\n\tpmAuthor="ooooige";\n\tChild=(\n\t\t<pqLlew6GAqAA7wvG:4bxByw6GAqAA7wcw>, \n\t\t<pqLlew6GAqAA7wvG:oBChyw6GAqAA7wda>, \n\t\t<pqLlew6GAqAA7wvG:2pgByw6GAqAA7wbT>\n\t);\n\tpmCreateDateTime="1584283469157";\n\t_modelViews=(\n\t\t{paLlew6GAqAA7wvO:"View":ModelView {\n\t\t\tcontainer=<QcgxGqqFYEAQWAnB>;\n\t\t\tview="hqLlew6GAqAA7wvF";\n\t\t}}\n\t);\n\tlastModifiedTime=1584286791767;\n\t_modelEditable=T;\n}'

    def TopLevelContainerTest(self, container, val_ID, val_Name, val_Type):
        self.assertIn('id'  	, container, "No member named 'id'")
        self.assertIn('name'	, container, "No member named 'name'")
        self.assertIn('type'	, container, "No member named 'type'")
        self.assertEqual(container['id']	, val_ID	, "Mismatched member named 'id'")
        self.assertEqual(container['name']	, val_Name	, "Mismatched member named 'name'")
        self.assertEqual(container['type']	, val_Type	, "Mismatched member named 'type'")
        # There should be one child at the top layer...for all nested members.
        self.assertIn('child_0'	, container, "No member named 'child_0', but there should be")
        # And it should be a dict
        self.assertTrue(isinstance(container['child_0'	], dict))
        # There should be no more children at this level
        self.assertNotIn('child_1', container,	"Member named 'child_1', but there should not be")

    def OperationContainerTest(self, container, val_ID, val_Name, val_Type, val_Visibility, val_ReturnType):
        # Same structure as the highest level...
        self.TopLevelContainerTest(container, val_ID, val_Name, val_Type)
        # There should be one child at the top layer...for all nested operation parameters.
        self.assertIn('child_0', container, "No member named 'child_0', but there should be")
        # And it should be a dict
        self.assertTrue(isinstance(container['child_0'], dict))
        parameters = container['child_0']
        # Check the visibility
        self.assertIn('visibility', parameters, "No member named 'visibility'")
        self.assertEqual(parameters['visibility'], val_Visibility, "Mismatched member named 'visibility'")
        # Check the return type
        self.assertIn('returnType_0', parameters, "No member named 'returnType_0'")
        self.assertEqual(parameters['returnType_0'], val_ReturnType, "Mismatched member named 'returnType_0'")

    def ParameterContainerTest(self, container, val_ID, val_Name, val_Type, params):
        # Same structure as the highest level...
        self.TopLevelContainerTest(container['child_0'], val_ID, val_Name, val_Type)
        cnt = 0
        paramsContainer = container['child_0']
        for i in params:
            self.assertIn('child_'+str(cnt), paramsContainer, "No member named 'child_"+str(cnt)+"', but there should be")
            p = paramsContainer['child_'+str(cnt)]
            for k, v in i.items():
                self.assertEqual(p[k], v, "Mismatched member named '"+k+"'")
            cnt = cnt + 1

    def test_Deserialize_ClassBlob(self):
        class_info = vppfs.ParseBLOB_Recursive(self.blob_Class.decode())

        # To look at the structure...
        #Print_RecursiveParsed_BLOB(class_info)

        self.TopLevelContainerTest(class_info, "4bxByw6GAqAA7wcw", "ILayer", "Class")

        child_0 = class_info['child_0']
        ''' Test only the attributes that we care about for code-generation
        '''
        # This particular class has a stereotype...it should be 'Interface'.
        self.assertIn("stereotypes_0"			 , child_0				, "No member named 'stereotypes_0', but there should be")
        self.assertEqual(child_0['stereotypes_0'], "zpgByw6GAqAA7wbU"	, "Mismatched member named 'stereotypes_0'")
        # At this level, there should be 4 children...the first being a 'modelview', that we don't care about...
        # then the next three being operations.
        self.assertIn("child_0"			, child_0				, "No member named 'child_0', but there should be")
        self.assertIn("child_1"			, child_0				, "No member named 'child_1', but there should be")
        self.assertIn("child_2"			, child_0				, "No member named 'child_2', but there should be")
        self.assertIn("child_3"			, child_0				, "No member named 'child_3', but there should be")
        self.assertNotIn("child_4"		, child_0				, "Member named 'child_4', but there should not be")
        # Operation 1
        operation_1 = child_0['child_1']
        self.OperationContainerTest(operation_1, 'Ef1Byw6GAqAA7wdB', 'Send', 'Operation', Visibility.Public, 'F5FFKqqFYEAQWAYP')
        parameters = operation_1['child_0']
        params = []
        param1 = {'typeModifier': '&', 'type_string': 'CPacket'}
        params.append(param1)
        self.ParameterContainerTest(parameters, 'fcDByw6GAqAA7wdE', 'packet', 'Parameter', params)
        # Operation 2
        operation_2 = child_0['child_2']
        self.OperationContainerTest(operation_2, '9A3Byw6GAqAA7wdG', 'Recv', 'Operation', Visibility.Public, 'F5FFKqqFYEAQWAYP')
        parameters = operation_2['child_0']
        # should be same params
        self.ParameterContainerTest(parameters, '7A3Byw6GAqAA7wdH', 'packet', 'Parameter', params)
        # Operation 3
        operation_3 = child_0['child_3']
        self.OperationContainerTest(operation_3, 'IVPByw6GAqAA7wdI', 'Process', 'Operation', Visibility.Public, 'F5FFKqqFYEAQWAYP')
        parameters = operation_3['child_0']
        # should be same params
        self.ParameterContainerTest(parameters, 'GVPByw6GAqAA7wdJ', 'packet', 'Parameter', params)

    def test_Deserialize_PackageBlob(self):
        package_info = vppfs.ParseBLOB_Recursive(self.blob_Package.decode())
        # To look at the structure
        #Print_RecursiveParsed_BLOB(package_info)

        self.TopLevelContainerTest(package_info, "pqLlew6GAqAA7wvG", "XProtocol", "Package")

        child_0 = package_info['child_0']

        # This blob : namespace has only 3 class children in it...notice the capitalization...
        self.assertIn("Child_0"				, child_0				, "No member named 'Child_0', but there should be")
        self.assertIn("Child_1"				, child_0				, "No member named 'Child_1', but there should be")
        self.assertIn("Child_2"				, child_0				, "No member named 'Child_2', but there should be")
        self.assertNotIn("Child_3"			, child_0				, "Member named 'Child_3', but there should not be")
        self.assertEqual(child_0['Child_0'], "pqLlew6GAqAA7wvG:4bxByw6GAqAA7wcw"	, "Mismatched member named 'Child_0'")
        self.assertEqual(child_0['Child_1'], "pqLlew6GAqAA7wvG:oBChyw6GAqAA7wda"	, "Mismatched member named 'Child_0'")
        self.assertEqual(child_0['Child_2'], "pqLlew6GAqAA7wvG:2pgByw6GAqAA7wbT"	, "Mismatched member named 'Child_0'")


#########################################################
# Development Tests
#########################################################


def BlobShit():
    blob_Class  = b'4bxByw6GAqAA7wcw:"ILayer":Class {\n\tstereotypes=(\n\t\t<zpgByw6GAqAA7wbU>\n\t);\n\t_modelEditable=T;\n\t_masterViewId="YbxByw6GAqAA7wcv";\n\tpmAuthor="ooooige";\n\tFromSimpleRelationships=(\n\t\t<sXtlKqqFYEAQWAie:KROxyw6GAqAA7wiS:8WQxyw6GAqAA7wg.>\n\t);\n\tpmCreateDateTime="1584096492935";\n\t_modelViews=(\n\t\t{ibxByw6GAqAA7wcx:"View":ModelView {\n\t\t\tcontainer=<QcgxGqqFYEAQWAnB>;\n\t\t\tview="YbxByw6GAqAA7wcv";\n\t\t}}\n\t);\n\tToEndRelationships=(\n\t\t<sXtlKqqFYEAQWAie:CROxyw6GAqAA7wiR:YGARyw6GAqAA7weJ$aGARyw6GAqAA7weO>\n\t);\n\tChild=(\n\t\t{Ef1Byw6GAqAA7wdB:"Send":Operation {\n\t\t\tvisibility=71;\n\t\t\treturnType=<F5FFKqqFYEAQWAYP>;\n\t\t\tpmLastModified="1584096608451";\n\t\t\tpmAuthor="ooooige";\n\t\t\tChild=(\n\t\t\t\t{fcDByw6GAqAA7wdE:"packet":Parameter {\n\t\t\t\t\ttypeModifier="&";\n\t\t\t\t\ttype_string="CPacket";\n\t\t\t\t\tpmLastModified="1584096608451";\n\t\t\t\t\tpmAuthor="ooooige";\n\t\t\t\t\tpmCreateDateTime="1584096543678";\n\t\t\t\t\t_modelViews=NULL;\n\t\t\t\t\t_modelEditable=T;\n\t\t\t\t}}\n\t\t\t);\n\t\t\tpmCreateDateTime="1584096526216";\n\t\t\t_modelViews=NULL;\n\t\t\t_modelEditable=T;\n\t\t}}, \n\t\t{9A3Byw6GAqAA7wdG:"Recv":Operation {\n\t\t\tvisibility=71;\n\t\t\treturnType=<F5FFKqqFYEAQWAYP>;\n\t\t\tpmLastModified="1584097249458";\n\t\t\tpmAuthor="ooooige";\n\t\t\tChild=(\n\t\t\t\t{7A3Byw6GAqAA7wdH:"packet":Parameter {\n\t\t\t\t\ttypeModifier="&";\n\t\t\t\t\ttype_string="CPacket";\n\t\t\t\t\tpmLastModified="1584096608451";\n\t\t\t\t\tpmAuthor="ooooige";\n\t\t\t\t\tpmCreateDateTime="1584096587834";\n\t\t\t\t\t_modelViews=NULL;\n\t\t\t\t\t_modelEditable=T;\n\t\t\t\t}}\n\t\t\t);\n\t\t\tpmCreateDateTime="1584096587831";\n\t\t\t_modelViews=NULL;\n\t\t\t_modelEditable=T;\n\t\t}}, \n\t\t{IVPByw6GAqAA7wdI:"Process":Operation {\n\t\t\tvisibility=71;\n\t\t\treturnType=<F5FFKqqFYEAQWAYP>;\n\t\t\tpmLastModified="1584097249458";\n\t\t\tpmAuthor="ooooige";\n\t\t\tChild=(\n\t\t\t\t{GVPByw6GAqAA7wdJ:"packet":Parameter {\n\t\t\t\t\ttypeModifier="&";\n\t\t\t\t\ttype_string="CPacket";\n\t\t\t\t\tpmLastModified="1584096608451";\n\t\t\t\t\tpmAuthor="ooooige";\n\t\t\t\t\tpmCreateDateTime="1584096594591";\n\t\t\t\t\t_modelViews=NULL;\n\t\t\t\t\t_modelEditable=T;\n\t\t\t\t}}\n\t\t\t);\n\t\t\tpmCreateDateTime="1584096594584";\n\t\t\t_modelViews=NULL;\n\t\t\t_modelEditable=T;\n\t\t}}\n\t);\n\tpmLastModified="1584097249456";\n}'
    blob_Class2 = b'oBChyw6GAqAA7wda:"CProtocolStack":Class {\n\t_modelEditable=T;\n\t_masterViewId="oBChyw6GAqAA7wdZ";\n\tToSimpleRelationships=(\n\t\t<sXtlKqqFYEAQWAie:KROxyw6GAqAA7wiS:4_Axyw6GAqAA7wg4>\n\t);\n\tpmAuthor="ooooige";\n\tFromEndRelationships=(\n\t\t<sXtlKqqFYEAQWAie:CROxyw6GAqAA7wiR:YGARyw6GAqAA7weJ$yGARyw6GAqAA7weL>\n\t);\n\tFromSimpleRelationships=(\n\t\t<sXtlKqqFYEAQWAie:WROxyw6GAqAA7wiU:OS2xyw6GAqAA7wiH>\n\t);\n\tpmCreateDateTime="1584096675845";\n\t_modelViews=(\n\t\t{sBChyw6GAqAA7wdb:"View":ModelView {\n\t\t\tcontainer=<QcgxGqqFYEAQWAnB>;\n\t\t\tview="oBChyw6GAqAA7wdZ";\n\t\t}}\n\t);\n\tChild=(\n\t\t{4N2hyw6GAqAA7wdl:"Send":Operation {\n\t\t\tvisibility=71;\n\t\t\treturnType=<F5FFKqqFYEAQWAYP>;\n\t\t\tpmLastModified="1584097249461";\n\t\t\tpmAuthor="ooooige";\n\t\t\tChild=(\n\t\t\t\t{qkBhyw6GAqAA7wdn:"packet":Parameter {\n\t\t\t\t\ttypeModifier="&";\n\t\t\t\t\ttype_string="CPacket";\n\t\t\t\t\tpmLastModified="1584097249461";\n\t\t\t\t\tpmAuthor="ooooige";\n\t\t\t\t\tpmCreateDateTime="1584096739925";\n\t\t\t\t\t_modelViews=NULL;\n\t\t\t\t\t_modelEditable=T;\n\t\t\t\t}}\n\t\t\t);\n\t\t\tpmCreateDateTime="1584096721671";\n\t\t\t_modelViews=NULL;\n\t\t\t_modelEditable=T;\n\t\t}}, \n\t\t{gmVhyw6GAqAA7wdp:"Recv":Operation {\n\t\t\tvisibility=71;\n\t\t\treturnType=<F5FFKqqFYEAQWAYP>;\n\t\t\tpmLastModified="1584097249461";\n\t\t\tpmAuthor="ooooige";\n\t\t\tChild=(\n\t\t\t\t{UmVhyw6GAqAA7wdq:"packet":Parameter {\n\t\t\t\t\ttypeModifier="&";\n\t\t\t\t\ttype_string="CPacket";\n\t\t\t\t\tpmLastModified="1584097249461";\n\t\t\t\t\tpmAuthor="ooooige";\n\t\t\t\t\tpmCreateDateTime="1584096781900";\n\t\t\t\t\t_modelViews=NULL;\n\t\t\t\t\t_modelEditable=T;\n\t\t\t\t}}\n\t\t\t);\n\t\t\tpmCreateDateTime="1584096781898";\n\t\t\t_modelViews=NULL;\n\t\t\t_modelEditable=T;\n\t\t}}\n\t);\n\tpmLastModified="1584097249461";\n}'
    blob_Package = b'pqLlew6GAqAA7wvG:"XProtocol":Package {\n\t_masterViewId="hqLlew6GAqAA7wvF";\n\tpmLastModified="1584286807443";\n\tpmAuthor="ooooige";\n\tChild=(\n\t\t<pqLlew6GAqAA7wvG:4bxByw6GAqAA7wcw>, \n\t\t<pqLlew6GAqAA7wvG:oBChyw6GAqAA7wda>, \n\t\t<pqLlew6GAqAA7wvG:2pgByw6GAqAA7wbT>\n\t);\n\tpmCreateDateTime="1584283469157";\n\t_modelViews=(\n\t\t{paLlew6GAqAA7wvO:"View":ModelView {\n\t\t\tcontainer=<QcgxGqqFYEAQWAnB>;\n\t\t\tview="hqLlew6GAqAA7wvF";\n\t\t}}\n\t);\n\tlastModifiedTime=1584286791767;\n\t_modelEditable=T;\n}'
    #print(blob_Class2.decode())
    de = vppfs.ParseBLOB_Recursive(blob_Package.decode())
    vppfs.Print_RecursiveParsed_BLOB(de)


def Dev_ClassDiagram():
    class_diagram = ExtractClassDiagram("ProtocolStack",r"TestModels.vpp")
    print(class_diagram)


def Dev_TestClassDiagram():
    class_diagram = ExtractClassDiagram("TestClassDiagram", r"TestModels.vpp")
    print(class_diagram)


if __name__ == "__main__":
    unittest.main()
    #Dev_ClassDiagram()
    #Dev_TestClassDiagram()
    #BlobShit()