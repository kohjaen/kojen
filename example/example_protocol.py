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

from kojen.interface_base import *

def CreateInterface():
    sCustomStruct = Struct('sCustomStruct')
    sCustomStruct.AddType('m_Member1','uint16')
    sCustomStruct.AddType('m_Member2','uint16')
    sCustomStruct.AddType('m_Member3','uint32')

    MsgSomeCMD = Message('MsgSomeCMD',0x01)
    MsgSomeCMD.AddType('m_Member1','uint8')

    MsgSomeCMDRSP = Message('MsgSomeCMDRSP',0x02)
    MsgSomeCMDRSP.AddStruct('mStructMember1',sCustomStruct)
    MsgSomeCMDRSP.AddType('m_Member2','uint8')
    
    MsgSomeREQ = Message('MsgSomeREQ',0x03)
    MsgSomeREQ.AddType('m_Member1','uint8')

    #Array of type : Not supported by ARM due to dynamic memory allocation requirements
    MsgSomeREQRSP = Message('MsgSomeREQRSP',0x04)
    MsgSomeREQRSP.AddStruct('mStructMember1',sCustomStruct)
    MsgSomeREQRSP.AddType('m_Member2','uint8')
    MsgSomeREQRSP.AddArrayOfType('mArrayMember3','double')


    MsgSomeUnsolicitedData = Message('MsgSomeUnsolicitedData',0x05)
    MsgSomeUnsolicitedData.AddArrayOfStruct('mStructArrayMember1',sCustomStruct)

    #
    # Includes : Enums and defines ...
    #
    Type = Enum("Type")
    Type.Add("kOne", 0)
    Type.Add("kTwo", 1)

    Revision = Enum("Revision")
    Revision.Add("kVersion1", 0)
    Revision.Add("kVersion2", 1)
    Revision.Add("kVersion3", 2)


    interface = Interface('IMyIntefaceIO')

    interface.AddEnum(Type)
    interface.AddEnum(Revision)

    interface.AddHashDefine("THREE", 3)
    interface.AddHashDefine("PI", 3.14159265359)

    interface.AddStruct(sCustomStruct)
    interface.AddMessage(MsgSomeCMD)
    interface.AddMessage(MsgSomeCMDRSP)
    interface.AddMessage(MsgSomeREQ)
    interface.AddMessage(MsgSomeREQRSP)
    interface.AddMessage(MsgSomeUnsolicitedData)


    return interface

if __name__ == "__main__":
    import kojen.protogen
    output_dir = ".\\autogen\\test_protocol"
    pythonfile = ".\\example_protocol.py"
    namespacename = "ITemplateIO"
    classname = "ITemplateIF"
    kojen.protogen.Generate(output_dir, pythonfile, namespacename, classname)