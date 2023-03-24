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

from kojen.kojentypes import *
import kojen.Generate as Generate
import os

def generate():
    author = "yourname@yourdomain.com"
    group = "GROUP_EXAMPLE"
    brief = "An example demonstrating code-generation abilities."
    namespacename = "ExampleIO"
    classname = "CExampleIF"
    declspec = ""
    outputdir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "autogen")
    templatedir = ""  # defaults

    interface = Interface('IMyIntefaceIO')

    AnotherNestedPayloadStruct = Struct('AnotherNestedPayloadStruct')
    AnotherNestedPayloadStruct.AddType('member1', 'uint16', '6')
    AnotherNestedPayloadStruct.AddType('member2', 'uint16', '7')
    AnotherNestedPayloadStruct.AddType('member3', 'uint32', '8')

    NestedPayloadStruct = Struct('NestedPayloadStruct')
    NestedPayloadStruct.AddType('member1', 'uint16', '3')
    NestedPayloadStruct.AddType('member2', 'uint16', '4')
    NestedPayloadStruct.AddType('member3', 'uint32', '5')
    NestedPayloadStruct.AddStruct('member4', AnotherNestedPayloadStruct)

    PayloadStruct = Struct('PayloadStruct')
    PayloadStruct.AddType('member1', 'uint16', '1')
    PayloadStruct.AddType('member2', 'uint16', '2')
    PayloadStruct.AddType('member3', 'uint32', '3')
    PayloadStruct.AddStruct('member4', NestedPayloadStruct)

    MsgSomeCMD = Message('MsgSomeCMD', 0x01)
    MsgSomeCMD.AddType('member1', 'uint8', '2')

    MsgSomeCMDRSP = Message('MsgSomeCMDRSP', 0x02)
    MsgSomeCMDRSP.AddStruct('mStructMember1', PayloadStruct)
    MsgSomeCMDRSP.AddType('member2', 'uint8', '3')

    MsgSomeREQ = Message('MsgSomeREQ', 0x03)
    MsgSomeREQ.AddType('member1', 'uint8', '4')

    MsgSomeREQRSP = Message('MsgSomeREQRSP', 0x04)
    MsgSomeREQRSP.AddStruct('mStructMember1', PayloadStruct)
    MsgSomeREQRSP.AddType('member2', 'uint8', '5')

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

    interface.AddEnum(Type)
    interface.AddEnum(Revision)

    interface.AddHashDefine("THREE", 3)
    interface.AddHashDefine("PI", 3.14159265359)

    interface.AddStruct(AnotherNestedPayloadStruct)
    interface.AddStruct(NestedPayloadStruct)
    interface.AddStruct(PayloadStruct)

    interface.AddMessage(MsgSomeCMD)
    interface.AddMessage(MsgSomeCMDRSP)
    interface.AddMessage(MsgSomeREQ)
    interface.AddMessage(MsgSomeREQRSP)

    Generate.Protocol(outputdir, interface, namespacename, classname, declspec, author, group, brief, templatedir, __file__, True)

if __name__ == "__main__":
    generate()