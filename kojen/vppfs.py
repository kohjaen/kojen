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
Good tutorial:
http://zetcode.com/db/sqlitepythontutorial/
'''

import sqlite3 as lite
from collections import OrderedDict
import unittest

#########################################################


class VPPSQLiteParser:
    ''' This class is a wrapper around common
        functionality for extracting UML diagram
        information from our favourite UML tool SQLite
        project file.
    '''
    con = None

    def __init__(self, pathtoDB):
        self.path = pathtoDB

    def SQLVersion(self):
        self.con = lite.connect(self.path)
        with self.con:
            ''' 'with' does the same as try/except/finally apparently '''
            cur = self.con.cursor()
            cur.execute('SELECT SQLITE_VERSION()')
            data = cur.fetchone()
            print ("SQLite version: %s" % data)

    ''' Will Fetch all tables in the DB	'''
    def FetchAllTables(self):
        self.con = lite.connect(self.path)
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return cur.fetchall()

    ''' Will List all tables in the DB'''
    def ListAllTables(self):
        rows = self.FetchAllTables()
        for row in rows:
            print (row)

    ''' Will fetch the meta-data in table(tablename). Metadata is a tuple(index, name, type)'''
    def FetchMetaDataTable(self, tablename):
        self.con = lite.connect(self.path)
        with self.con:
            cur = self.con.cursor()
            cur.execute('PRAGMA table_info('+str(tablename)+')')
            return cur.fetchall()

    ''' Will list the meta-data in table(tablename) '''
    def ListMetadataTable(self, tablename):
        data = self.FetchMetaDataTable(tablename)
        print ("********* ", tablename, " (index, name, type)*********")
        for d in data:
            print (d[0], d[1], d[2])

    ''' Will fetch the data in table(tablename) '''
    def FetchDataTable(self, tablename):
        self.con = lite.connect(self.path)
        with self.con:
            cur = self.con.cursor()
            cur.execute('SELECT * FROM ' + str(tablename))
            return cur.fetchall()

    ''' Will list the data in table(tablename) '''
    def ListDataTable(self, tablename):
        rows = self.FetchDataTable(tablename)
        for row in rows:
            print (row)

    def ListMetadataAllTables(self):
        tables = self.FetchAllTables()
        for t in tables:
            self.ListMetadataTable(t[0])

    def ListDataAllTables(self):
        tables = self.FetchAllTables()
        for t in tables:
            self.ListDataTable(t[0])

    def GetTransitionBlobs(self, tablename):
        return self.GetBlobs(tablename, 'Transition2')

    def GetStateBlobs(self, tablename):
        return self.GetBlobs(tablename, 'State2')

    def GetBlobs(self, tablename, shapetype):
        self.con = lite.connect(self.path)
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT DEFINITION FROM " + tablename + ' WHERE SHAPE_TYPE="'+shapetype+'"')
            data = cur.fetchall()
            return str(data)

    def GetSpecificBlob_DiagramElements(self, tablename, id, model_element_id):
        self.con = lite.connect(self.path)
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT DEFINITION FROM " + tablename + ' WHERE ID="'+id+'" AND MODEL_ELEMENT_ID="'+model_element_id+'"')
            data = cur.fetchone()[0]
            return str(data)

    def GetSpecificBlob_ModelElements(self, tablename, id):
        self.con = lite.connect(self.path)
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT DEFINITION FROM " + tablename + ' WHERE ID="'+id+'"')
            data = cur.fetchone()[0]
            return str(data)


#########################################################


class VPPDiagrams:
    ''' This class extracts all class and state diagram names
        and uuids from our favourite UML tool SQLite
        project file. It uses VPPSQLiteParser.
    '''
    vpp = None
    # identifiers for the tables used to extract UML diagram info
    tableid = u"DIAGRAM"
    tableid_DIAGRAM_ELEMENT = u"DIAGRAM_ELEMENT"
    # metadata indexes for DIAGRAM table data
    index_ID = -1
    index_DIAGRAM_TYPE = -1
    index_NAME = -1
    # Diagram types {'ID':'Name' , ...}
    state_diagrams = {}
    class_diagrams = {}

    def __init__(self, pathtoDB):
        self.has_diagrams = False
        self.tables = None
        self.vpp = VPPSQLiteParser(pathtoDB)
        self.LoadAndTest()

    ''' Returns a dictionary of 'ID:Name' pairs for all class diagrams found in the project. '''
    def GetClassDiagrams(self):
        return self.class_diagrams
    ''' Returns a dictionary of 'ID:Name' pairs for all state diagrams found in the project. '''
    def GetStateDiagrams(self):
        return self.state_diagrams
    ''' Returns the ID of the state diagram of 'name'. Raised an exception if it does not exist'''
    def GetIDFromStateDiagramName(self, name):
        for key, val in self.state_diagrams.items():
            if val == name:
                return key
        raise KeyError(name + " not found")
    ''' Returns the ID of the class diagram of 'name'. Raised an exception if it does not exist'''
    def GetIDFromClassDiagramName(self, name):
        for key, val in self.class_diagrams.items():
            if val == name:
                return key
        raise KeyError(name + " not found")
    ''' Will load the table and hope to catch any changes (for future proofing) if VP decide to change their database. '''
    def LoadAndTest(self):

        ## Check the existence of 'diagrams' and 'diagram elements' tables in the database.

        self.tables = self.vpp.FetchAllTables()

        for table in self.tables:
            # Appears to be a tuple of tuples.
            if table[0] == self.tableid and table[0] != self.tableid_DIAGRAM_ELEMENT:
                self.has_diagrams = True

        # raise exceptions to fail
        if not self.has_diagrams:
            raise Exception(u"Table '"+self.tableid+u"' could not be found in VPP")

        ## Check the 'diagram' table metadata. It should contain the following metadata.

        metadata = self.vpp.FetchMetaDataTable(self.tableid)

        has_ID = False
        has_DIAGRAM_TYPE = False
        has_NAME = False
        for d in metadata:
            if len(d) != 3+3:
                # Last 3 items are I-don't-know
                raise Exception(u"Metadata in table '"+self.tableid+u"' unexpected size")
            index = d[0]
            name = d[1]
            type = d[2]
            if name == 'ID':
                if type != 'char(16)':
                    print (u"WARNING : Metadata 'ID' in table '"+self.tableid+u"' type changed from 'char(16)' to " , type)
                has_ID = True
                self.index_ID = int(index)
            if name == 'DIAGRAM_TYPE':
                if type != 'varchar(64)':
                    print (u"WARNING : Metadata 'DIAGRAM_TYPE' in table '"+self.tableid+u"' type changed from 'varchar(64)' to " , type)
                has_DIAGRAM_TYPE = True
                self.index_DIAGRAM_TYPE = int(index)
            if name == 'NAME':
                if type != 'text':
                    print (u"WARNING : Metadata 'NAME' in table '"+self.tableid_DIAGRAM+u"' type changed from 'text' to " , type)
                has_NAME = True
                self.index_NAME = int(index)
        if not has_ID:
            raise Exception(u"Table '"+self.tableid+u"' no longer has metadata 'ID'")
        if not has_DIAGRAM_TYPE:
            raise Exception(u"Table '"+self.tableid+u"' no longer has metadata 'DIAGRAM_TYPE'")
        if not has_NAME:
            raise Exception(u"Table '"+self.tableid+u"' no longer has metadata 'NAME'")

        ## Check the 'diagram' table. It should contain 1 state diagram. Also extract the ID and the name.

        self.tabledata = self.vpp.FetchDataTable(self.tableid)
        if len(self.tabledata) == 0:
            raise Exception(u"Table '"+self.tableid+u"' expected at least 1 diagram")

        for entry in self.tabledata:
            if entry[self.index_DIAGRAM_TYPE] == u'StateDiagram':
                table_ID = entry[self.index_ID]
                table_NAME = entry[self.index_NAME]
                self.state_diagrams[table_ID] = table_NAME

            if entry[self.index_DIAGRAM_TYPE] == u'ClassDiagram':
                table_ID = entry[self.index_ID]
                table_NAME = entry[self.index_NAME]
                self.class_diagrams[table_ID] = table_NAME


#########################################################


class VPPDiagramElement:
    ''' This class represents a diagram element.
        Most important information is the model element ID.
        Further information on this model element can be
        extracted with this.
    '''
    ID = ""
    SHAPE_TYPE = ""
    MODEL_ELEMENT_ID = ""
    BLOB_STRING = ""


#########################################################


class VPPDiagramElements:
    ''' This class extracts all diagram model elements
        for all diagrams in our favourite UML tool SQLite
        project file. It uses VPPSQLiteParser.
    '''
    vpp = None
    # identifiers for the tables used to extract UML data
    tableid = u"DIAGRAM_ELEMENT"
    # metadata indexes for DIAGRAM_ELEMENT table data
    index_ID = -1
    index_SHAPE_TYPE = -1
    index_DIAGRAM_ID = -1
    index_MODEL_ELEMENT_ID = -1
    index_DEFINITION = -1

    def __init__(self, pathtoDB):
        self.has_diagram_elements = False
        self.tabledata = None
        self.vpp = VPPSQLiteParser(pathtoDB)
        self.LoadAndTest()

    ''' Returns a list of all VPPDiagramElement that are in the diagram with ID	'''
    def GetDiagramElements(self, DiagramID):
        result = []
        for entry in self.tabledata:
            if entry[self.index_DIAGRAM_ID] == DiagramID:
                element = VPPDiagramElement()
                element.ID = entry[self.index_ID]
                element.SHAPE_TYPE = entry[self.index_SHAPE_TYPE]
                element.MODEL_ELEMENT_ID = entry[self.index_MODEL_ELEMENT_ID]
                element.BLOB_STRING = self.vpp.GetSpecificBlob_DiagramElements(self.tableid, element.ID, element.MODEL_ELEMENT_ID)
                # remove 'b'
                result.append(element)
        return result
    ''' Will load the table and hope to catch any changes (for future proofing) if VP decide to change their database. '''
    def LoadAndTest(self):
        tables = self.vpp.FetchAllTables()

        for table in tables:
            # Appears to be a tuple of tuples.
            if table[0] == self.tableid:
                self.has_diagram_elements = True

        # raise exceptions to fail
        if not self.has_diagram_elements:
            raise Exception(u"Table '"+self.tableid+u"' could not be found in VPP")

        ## Check the 'diagram_element' table...

        metadata = self.vpp.FetchMetaDataTable(self.tableid)

        has_ID = False
        has_SHAPE_TYPE = False
        has_DIAGRAM_ID = False
        has_MODEL_ELEMENT_ID = False
        has_DEFINITION = False

        for d in metadata:
            if len(d) != 3+3:
                # Last 3 items are I-dont-know
                raise Exception("Metadata in table '"+self.tableid+"' unexpected size")
            index = d[0]
            name = d[1]
            type = d[2]
            if name == 'ID':
                if type != 'char(16)':
                    print ("WARNING : Metadata 'ID' in table '"+self.tableid+"' type changed from 'char(16)' to " , type)
                has_ID = True
                self.index_ID = int(index)
            if name == 'SHAPE_TYPE':
                if type != 'varchar(64)':
                    print ("WARNING : Metadata 'SHAPE_TYPE' in table '"+self.tableid+"' type changed from 'varchar(64)' to " , type)
                has_SHAPE_TYPE = True
                self.index_SHAPE_TYPE = int(index)
            if name == 'DIAGRAM_ID':
                if type != 'char(16)':
                    print ("WARNING : Metadata 'DIAGRAM_ID' in table '"+self.tableid+"' type changed from 'char(16)' to " , type)
                has_DIAGRAM_ID = True
                self.index_DIAGRAM_ID = int(index)
            if name == 'MODEL_ELEMENT_ID':
                if type != 'char(16)':
                    print ("WARNING : Metadata 'MODEL_ELEMENT_ID' in table '"+self.tableid+"' type changed from 'char(16)' to " , type)
                has_MODEL_ELEMENT_ID = True
                self.index_MODEL_ELEMENT_ID = int(index)
            if name == 'DEFINITION':
                if type != 'blob':
                    print ("WARNING : Metadata 'DEFINITION' in table '"+self.tableid+"' type changed from 'blob' to " , type)
                has_DEFINITION = True
                self.index_DEFINITION = int(index)
        if not has_ID:
            raise Exception("Table '"+self.tableid+"' no longer has metadata 'ID'")
        if not has_SHAPE_TYPE:
            raise Exception("Table '"+self.tableid+"' no longer has metadata 'SHAPE_TYPE'")
        if not has_DIAGRAM_ID:
            raise Exception("Table '"+self.tableid+"' no longer has metadata 'DIAGRAM_ID'")
        if not has_MODEL_ELEMENT_ID:
            raise Exception("Table '"+self.tableid+"' no longer has metadata 'MODEL_ELEMENT_ID'")
        if not has_DEFINITION:
            raise Exception("Table '"+self.tableid+"' no longer has metadata 'DEFINITION'")

        self.tabledata = self.vpp.FetchDataTable(self.tableid)
        if len(self.tabledata) == 0:
            raise Exception(u"Table '"+self.tableid+u"' expected at least 1 diagram")


#########################################################


class VPPModelElement:
    ''' This class represents a model element.
        Most important information is the model element ID.
        Further information of this model element is extracted with this ID
        from the VPPModelElements Table.
    '''
    ID = ""
    MODEL_TYPE = ""
    PARENT_ID = ""
    NAME = ""
    BLOB_STRING = ""


class VPPModelElements:
    ''' This class extracts all model elements in our favourite UML tool SQLite
        project file. It uses VPPSQLiteParser.
    '''
    vpp = None
    # identifiers for the tables used to extract UML data
    tableid = u"MODEL_ELEMENT"
    # metadata indexes for DIAGRAM_ELEMENT table data
    index_ID = -1
    index_MODEL_TYPE = -1
    index_PARENT_ID = -1
    index_NAME = -1
    index_DEFINITION = -1

    def __init__(self, pathtoDB):
        self.has_model_elements = False
        self.tabledata = None
        self.vpp = VPPSQLiteParser(pathtoDB)
        self.LoadAndTest()

    ''' Returns the model element given the model element id'''
    def GetModelElement(self, model_element_id):
        for entry in self.tabledata:
            if entry[self.index_ID] == model_element_id:
                element = VPPModelElement()
                element.ID = "" if entry[self.index_ID] is None else entry[self.index_ID]
                element.MODEL_TYPE = "" if entry[self.index_MODEL_TYPE] is None else entry[self.index_MODEL_TYPE]
                element.PARENT_ID =  "" if entry[self.index_PARENT_ID] is None else entry[self.index_PARENT_ID]
                element.NAME =  "" if entry[self.index_NAME] is None else entry[self.index_NAME]
                element.BLOB_STRING =  self.vpp.GetSpecificBlob_ModelElements(self.tableid, entry[self.index_ID])
                return element
        raise Exception("Model Element '" + model_element_id + '" not found')

    ''' Will load the table and hope to catch any changes (for future proofing) if VP decide to change their database. '''
    def LoadAndTest(self):
        tables = self.vpp.FetchAllTables()

        for table in tables:
            # Appears to be a tuple of tuples.
            if table[0] == self.tableid:
                self.has_model_elements = True

        # raise exceptions to fail
        if not self.has_model_elements:
            raise Exception(u"Table '"+self.tableid+u"' could not be found in VPP")

        ## Check the 'diagram_element' table...

        metadata = self.vpp.FetchMetaDataTable(self.tableid)

        has_ID = False
        has_MODEL_TYPE = False
        has_PARENT_ID = False
        has_NAME = False
        has_DEFINITION = False

        for d in metadata:
            if len(d) != 3+3:
                # Last 3 items are I-dont-know
                raise Exception("Metadata in table '"+self.tableid+"' unexpected size")
            index = d[0]
            name = d[1]
            type = d[2]
            if name == 'ID':
                if type != 'char(16)':
                    print ("WARNING : Metadata 'ID' in table '"+self.tableid+"' type changed from 'char(16)' to " , type)
                has_ID = True
                self.index_ID = int(index)
            if name == 'MODEL_TYPE':
                if type != 'varchar(64)':
                    print ("WARNING : Metadata 'MODEL_TYPE' in table '"+self.tableid+"' type changed from 'varchar(64)' to " , type)
                has_MODEL_TYPE = True
                self.index_MODEL_TYPE = int(index)
            if name == 'PARENT_ID':
                if type != 'char(16)':
                    print ("WARNING : Metadata 'PARENT_ID' in table '"+self.tableid+"' type changed from 'char(16)' to " , type)
                has_PARENT_ID = True
                self.index_PARENT_ID = int(index)
            if name == 'NAME':
                if type != 'text':
                    print ("WARNING : Metadata 'NAME' in table '"+self.tableid+"' type changed from 'text' to " , type)
                has_NAME = True
                self.index_NAME = int(index)
            if name == 'DEFINITION':
                if type != 'blob':
                    print ("WARNING : Metadata 'DEFINITION' in table '"+self.tableid+"' type changed from 'blob' to " , type)
                has_DEFINITION = True
                self.index_DEFINITION = int(index)
        if not has_ID:
            raise Exception("Table '"+self.tableid+"' no longer has metadata 'ID'")
        if not has_MODEL_TYPE:
            raise Exception("Table '"+self.tableid+"' no longer has metadata 'MODEL_TYPE'")
        if not has_PARENT_ID:
            raise Exception("Table '"+self.tableid+"' no longer has metadata 'PARENT_ID'")
        if not has_NAME:
            raise Exception("Table '"+self.tableid+"' no longer has metadata 'MODEL_ELEMENT_ID'")
        if not has_DEFINITION:
            raise Exception("Table '"+self.tableid+"' no longer has metadata 'DEFINITION'")

        self.tabledata = self.vpp.FetchDataTable(self.tableid)


def mass_replace(string):																  # python 3                                           # python 2                                #
    return string.replace('=', '').replace('<', '').replace('>', '').replace(';', '').replace(r'\n', '').replace(r'\r', '').replace(r'\t', '').replace('\n', '').replace('\r', '').replace('\t', '').replace('"', "").replace('(', '').replace(')', '')


#########################################################
# Class Diagram  -> to go to own file
#########################################################


def Get_KeyNameType(text):
    if text.find(":") == -1:
        return None
    text = mass_replace(text)
    return text.split(":")


def Get_ValuesFromOutside(outside, verbose=False):
    '''
    During recursion of 'ParseBLOB_Recursive', a outside and a inside ({}) (another Blob) is built up.
    The outside contains pairs/tuples, depending. This function deciphers that.

    :param outside: the text 'outside' the 'this{notthistext}text'
    :return: dictionary of key/values.
    '''
    res = {}
    if outside.find(";") == -1 and outside.find(":") != -1:
        # its a key:name:type
        all = outside.split(":")
        res["id"] = mass_replace(all[0]).strip()
        res["name"] = mass_replace(all[1]).strip()
        res["type"] = mass_replace(all[2]).strip()
    else:
        all = outside.split(";")
        for a in all:
            if a.find("=") > -1:
                b = a.split("=")
                # Ignore the following as their children will already be children by parsing '{' and '}'
                if len(mass_replace(b[1]).replace(',', '').strip()) > 0 :
                    # special processing on these (looks to me like a list of a vector i.e. <e1><e2><e3>),
                    # that may be needed for other code generation
                    if b[1].find('<') != -1 and b[1].find('>') != -1:
                        vect = b[1].replace(">", "").replace('\n', '').replace('\t', '').replace('(', '').replace(')', '')
                        all_sterotypes = vect.split("<")
                        cnt = 0
                        for i in all_sterotypes:
                            i = mass_replace(i).replace(',', '').strip()
                            if len(i) > 0:
                                res[mass_replace(b[0]) + "_" + str(cnt)] = i
                                cnt = cnt + 1
                    else:
                        res[mass_replace(b[0]).strip()] = mass_replace(b[1]).strip()
            else:
                if verbose:
                    if len(mass_replace(a)) > 0:
                        print("Oops >> ", a)
    return res


index_PBR = 0


def ParseBLOB_Recursive(string, index = 0):
    '''
    Returns a dictionary of key:value paris, from a VPP blob.

    Will recursively split strings found between the first "{" and last "}" characters.
    - 	first string (outside) will be what is outside the parenthesis, meaning all items that are owned by the object
        at that level of nesting, and these will be further split into key:value pairs
    - 	Second string (children) will be what is within the parenthesis, which could be more blobs.
    -   The 'key' itself will be split into key-value pairs.
    '''
    global index_PBR
    index_PBR = index
    outside = ""
    children = {}
    result = {}

    while index_PBR < len(string):
        c = string[index_PBR]
        index_PBR = index_PBR+1
        if c == '{':
            child = ParseBLOB_Recursive(string, index_PBR)
            children["child_" + str(len(children))] = child
        elif c == '}':
            res = Get_ValuesFromOutside(outside)
            result.update(res)
            result.update(children)
            return result
        else:
            outside += c

    res = Get_ValuesFromOutside(outside)
    result.update(res)
    result.update(children)
    return result


def level_str(level):
    return "|" + level*"- - "


def Print_RecursiveParsed_BLOB(de):
    for k, v in de.items():
        if isinstance(v, dict):
            print(level_str(1) + k)
            for k2, v2 in v.items():
                if isinstance(v2, dict):
                    print(level_str(2) + k2)
                    for k3, v3 in v2.items():
                        if isinstance(v3, dict):
                            print(level_str(3) + k3)
                            for k4, v4 in v3.items():
                                if isinstance(v4, dict):
                                    print(level_str(4) + k4)
                                    for k5, v5 in v4.items():
                                        if isinstance(v5, dict):
                                            print(level_str(5) + k5)
                                            for k6, v6 in v5.items():
                                                if isinstance(v6, dict):
                                                    print(level_str(6) + k6)
                                                    for k7, v7 in v6.items():
                                                        if isinstance(v7, dict):
                                                            print(level_str(7) + k7)
                                                            for k8, v8 in v7.items():
                                                                print(level_str(8) + k8, ' = ', v8)
                                                        else:
                                                            print(level_str(7) + k7, ' = ', v7)
                                                else:
                                                    print(level_str(6) + k6, ' = ', v6)
                                        else:
                                            print(level_str(5) + k5, ' = ', v5)
                                else:
                                    print(level_str(4) + k4, ' = ', v4)
                        else:
                            print(level_str(3) + k3, ' = ' , v3)
                else:
                    print(level_str(2) + k2, " = ", v2)
        else:
            print(level_str(1) + k, " = ", v)
    print('\r\n')


#########################################################
# State Diagram  -> to go to own file
#########################################################


def GetLastIDFromColonList(item):
    ''' For items that have parent child relationship ids concatenate like "idparent:idchild:idchild2..." '''
    itemlist = item.split(':')
    return itemlist[len(itemlist)-1]

class Transition(VPPModelElement):
    ''' This class represents a 'Transition' VPPModelElement.
        All VPPModelElement comments hold true. This class is specialized
        with more fields : 'from state', 'to state', 'guard' and 'activity'.
        These added fields are the model element id's of the corresponding model elements.
        These are added via trickery in the 'Parse' function.
    '''
    def __init__(self, baseclass):
        self.ID = baseclass.ID
        self.MODEL_TYPE = baseclass.MODEL_TYPE
        self.PARENT_ID = baseclass.PARENT_ID
        self.NAME = baseclass.NAME
        self.BLOB_STRING = baseclass.BLOB_STRING
        self.STATE_TO_ID = None
        self.STATE_FROM_ID = None
        self.GUARD = None
        self.ACTIVITY = None
        self.Parse()

    def Parse(self):
        for i in self.BLOB_STRING.split(';'):
            if i.find('toModel') > -1:
                state_to_id = mass_replace(i.replace('toModel', ''))
                # This yields multiple IDs. Ownership parent child relationships. It seems we can get the name from the last one
                self.STATE_TO_ID = GetLastIDFromColonList(state_to_id)
            if i.find('fromModel') > -1:
                state_from_id = mass_replace(i.replace('fromModel', ''))
                # This yields multiple IDs. Ownership parent child relationships. It seems we can get the name from the last one
                self.STATE_FROM_ID = GetLastIDFromColonList(state_from_id)
            if i.find('guard') > -1:
                guard = mass_replace(i.replace('guard', ''))
                # This yields multiple IDs. Ownership parent child relationships. It seems we can get the name from the last one
                self.GUARD = GetLastIDFromColonList(guard)
            if i.find('effect') > -1:
                activity = mass_replace(i.replace('effect', ''))
                # This yields multiple IDs. Ownership parent child relationships. It seems we can get the name from the last one
                self.ACTIVITY = GetLastIDFromColonList(activity)


class Guard(VPPModelElement):
    ''' This class represents a 'Guard' VPPModelElement.
        All VPPModelElement comments hold true. This class is specialized
        to extract the 'value_string' from the model element blob, as the NAME.
        As of writing, this appears to be the text we want.
        See trickery in the 'Parse' function.
    '''
    def __init__(self, baseclass):
        self.ID = baseclass.ID
        self.MODEL_TYPE = baseclass.MODEL_TYPE
        self.PARENT_ID = baseclass.PARENT_ID
        self.NAME = baseclass.NAME
        self.BLOB_STRING = baseclass.BLOB_STRING
        self.Parse()

    def Parse(self):
        for i in self.BLOB_STRING.split(';'):
            if i.find('value_string') > -1:
                self.NAME = mass_replace(i.replace('value_string', ''))
                return
        raise Exception("'value_string' not found when parsing 'guard' model element blob. Could it be that this has changed?'")


class StateDiagram:
    ''' This class represents a state diagram for a particular diagram of 'name' and 'id'.
        The name and the id of the diagram are passed into the constructor.
        The diagram elements from the project are also passed into the constructor (from the diagram elements table)
        as well as the model elements table.

        This class will use the diagram elements to lookup all the necessary model elements from the model elements table
        and create a transition table from that.
    '''
    states = {}
    transitions = {}
    guards = {}
    actions = {}
    initialpseudostate = None

    def __init__(self, diagramName, diagramID, diagramElements, table_vppmodelelements):
        self.name = diagramName
        self.id = diagramID
        self.elements = diagramElements
        self.table_vppmodelelements = table_vppmodelelements
        self.LoadAndTest()

    ''' Will load the table and hope to catch any changes (for future proofing) if VP decide to change their database. '''
    def LoadAndTest(self):
        for i in self.elements:
            vppmodelelement = self.table_vppmodelelements.GetModelElement(i.MODEL_ELEMENT_ID)
            if vppmodelelement.MODEL_TYPE == 'InitialPseudoState':
                self.initialpseudostate = vppmodelelement
            elif vppmodelelement.MODEL_TYPE == 'Transition2':
                self.transitions[vppmodelelement.ID] = Transition(vppmodelelement)
            elif vppmodelelement.MODEL_TYPE == 'State2':
                self.states[vppmodelelement.ID] = vppmodelelement
            elif vppmodelelement.MODEL_TYPE == 'NOTE':
                pass
            elif vppmodelelement.MODEL_TYPE == 'Anchor':
                pass
            else:
                raise Exception("Unhandled model type found in State Diagram : " + vppmodelelement.MODEL_TYPE)
        # Now missing, GUARDS and ACTIONS...
        for key, t in self.transitions.items():
            if t.GUARD is not None:
                guard = self.table_vppmodelelements.GetModelElement(t.GUARD)
                self.guards[t.GUARD] = Guard(guard)
            if t.ACTIVITY is not None:
                action = self.table_vppmodelelements.GetModelElement(t.ACTIVITY)
                self.actions[t.ACTIVITY] = action

    def GetTransitionTable(self):
        # Model Types
        # 'InitialPseudoState' -> any transition with 'fromModel' of this ID should be ignored...
        transition_table = []
        # Use an ordered dictionary on start state to group all transitions together from states...
        ordered_TT = OrderedDict()

        # For boost sm generation, the initial state should always be the first 'from state' in the TT.
        # Find that via the initialpseudostate, and add it as the first item to the ordered_TT
        for key, val in self.transitions.items():
            if val.STATE_FROM_ID == self.initialpseudostate.ID:
                ordered_TT[self.states[val.STATE_TO_ID].NAME] = []
        # 		FROM									EVENT						NEXT						ACTION				GUARD

        for key, val in self.transitions.items():
            if val.STATE_FROM_ID != self.initialpseudostate.ID:
                _from = self.states[val.STATE_FROM_ID].NAME
                if not (_from in ordered_TT):
                    ordered_TT[_from] = []

                _event = val.NAME
                _next = self.states[val.STATE_TO_ID].NAME
                if _next == _from:
                    _next = 'None'
                _action = 'None' if val.ACTIVITY is None else self.actions[val.ACTIVITY].NAME
                _guard = 'None' if val.GUARD is None else self.guards[val.GUARD].NAME
                ordered_TT[_from].append([_from, _event, _next, _action, _guard])

        for key, val in ordered_TT.items():
            for start, event, next, action, guard in val:
                transition_table.append([start, event, next, action, guard])

        return transition_table


''' USE THIS FUNCTION to extract the transition table from a VPP file.
    input : state machine diagram name
    input : path to the file
'''
def ExtractTransitionTable(statemachinediagramname, path_to_vpp):
    vppdiagrams = VPPDiagrams(path_to_vpp)
    vppdiagramelements = VPPDiagramElements(path_to_vpp)
    vppmodelelements = VPPModelElements(path_to_vpp)
    elements = vppdiagramelements.GetDiagramElements(vppdiagrams.GetIDFromStateDiagramName(statemachinediagramname))
    statediagram = StateDiagram(statemachinediagramname ,vppdiagrams.GetIDFromStateDiagramName(statemachinediagramname), elements, vppmodelelements)
    return statediagram.GetTransitionTable()


def equal_space(str):
    return str + (35 - len(str))*" "

#########################################################
# Unit Tests -> to go to own file
#########################################################


class TestDBFormat(unittest.TestCase):
    ''' Unit test. These guys might change the format of their DB.
        This hopes to make it easier to catch those changes and adapt to them quickly.
        This also is coded for the fixed number of diagrams in the model I do the dev with...if that changes, this code must change.
    '''
    def setUp(self):
        self.unit_test_model = r"TestModels.vpp"
        self.vppdiagrams = VPPDiagrams(self.unit_test_model)
        self.classdiagrams = self.vppdiagrams.GetClassDiagrams()
        self.statediagrams = self.vppdiagrams.GetStateDiagrams()

    def test_classDiagrams(self):
        expectedIDToName = {u'QcgxGqqFYEAQWAnB': u'ProtocolStack', u'sb74Kw6GAqAA7wjN': u'TestClassDiagram'}

        self.assertEqual(len(self.classdiagrams), 2									, "Expected 2 class diagrams in TestModels.vpp test project")

        for key,val in expectedIDToName.items():
            self.assertTrue((key in self.classdiagrams)								, "Class diagram '" + val + "' in TestModels.vpp test project ID changed.")
            self.assertEqual(self.classdiagrams[key], val						 	, "Class diagram '" + val + "' in TestModels.vpp test project NAME changed.")
            self.assertEqual(key, self.vppdiagrams.GetIDFromClassDiagramName(val)	, "Error in lookup class diagram " + val)

    def test_stateDiagrams(self):
        expectedIDToName = {u'4C0lKqqFYEAQWAg_': u'TestStateMachine'}

        self.assertEqual(len(self.statediagrams), 1									, "Expected 1 state diagram in TestModels.vpp test project")

        for key, val in expectedIDToName.items():
            self.assertTrue((key in self.statediagrams)								, "State diagram '" + val + "' in TestModels.vpp test project ID changed.")
            self.assertEqual(self.statediagrams[key], val							, "State diagram '" + val + "' in TestModels.vpp test project NAME changed.")
            self.assertEqual(key, self.vppdiagrams.GetIDFromStateDiagramName(val)	, "Error in lookup state diagram " + val)

    def test_stateDiagramTransitionTable(self):
        vppdiagramelements = VPPDiagramElements(self.unit_test_model)
        vppmodelelements = VPPModelElements(self.unit_test_model)
        elements = vppdiagramelements.GetDiagramElements(self.vppdiagrams.GetIDFromStateDiagramName('TestStateMachine'))

        self.assertEqual(len(elements),  8, "Expected 8 state diagram in elements in TestStateMachine in TestModels.vpp")

        # Create a state diagram with NAME, ID and CHILDREN ELEMENTs
        statediagram = StateDiagram('TestStateMachine', self.vppdiagrams.GetIDFromStateDiagramName('TestStateMachine'), elements, vppmodelelements)
        tt = statediagram.GetTransitionTable()

        self.assertEqual(len(tt), 3,		"Expected 3 rows in transition table from TestStateMachine in TestModels.vpp")

        self.assertTrue(tt[0][0] == 'StateRed' 		and tt[0][1] == 'EventButtonPressed' and tt[0][2] == 'StateOrange' 	and tt[0][3] == 'OnOrange' 	and tt[0][4] == 'GuardCanChangeToOrange', "Error with row 1 of transition table from TestStateMachine in TestModels.vpp")
        self.assertTrue(tt[1][0] == 'StateOrange' 	and tt[1][1] == 'EventButtonPressed' and tt[1][2] == 'StateGreen' 	and tt[1][3] == 'OnGreen' 	and tt[1][4] == 'GuardCanChangeToGreen', "Error with row 2 of transition table from TestStateMachine in TestModels.vpp")
        self.assertTrue(tt[2][0] == 'StateGreen' 	and tt[2][1] == 'EventButtonPressed' and tt[2][2] == 'StateRed' 	and tt[2][3] == 'OnRed' 	and tt[2][4] == 'GuardCanChangeToRed', "Error with row 3 of transition table from TestStateMachine in TestModels.vpp")

#########################################################
# Development Tests
#########################################################


def Test_MS():
    tt = ExtractTransitionTable("MotionSystemStateMachine", r"/Users/eugenegrobbelaar/HomeProjects/Z43/Z43/ICEy/ICEMotionSystem/vpproject/ICEMotionSystem.vpp")
    for row in tt:
        print(equal_space(row[0])+',', equal_space(row[1])+',', equal_space(row[2])+',', equal_space(row[3])+',', equal_space(row[4]))


def Test_VSAScan():
    tt = ExtractTransitionTable("VSAScanStateMachine", r"/Users/eugenegrobbelaar/HomeProjects/Z43/Z43/ICEy/ICESY/vpproject/XIcesy.vpp")
    for row in tt:
        print(equal_space(row[0])+',', equal_space(row[1])+',', equal_space(row[2])+',', equal_space(row[3])+',', equal_space(row[4]))


def Test_VSAScanDispatcher():
    tt = ExtractTransitionTable("VSAScanDispatcherStateMachine", r"/Users/eugenegrobbelaar/HomeProjects/Z43/Z43/ICEy/XIcesy/vpproject/XIcesy.vpp")
    for row in tt:
        print(equal_space(row[0])+',', equal_space(row[1])+',', equal_space(row[2])+',', equal_space(row[3])+',', equal_space(row[4]))


if __name__ == "__main__":
    unittest.main()
    #Test_MS()
    #Test_VSAScan()
    #Test_VSAScanDispatcher()