/**
[[[cog
import cog
from <<<PYIFGENNAME>>> import *
from LanguageCPP import *
interface = CreateInterface()
language  = LanguageCPP()

for g in language.LicenseAgreement():
	cog.outl(g)

cog.outl("This generates unit tests for use with the BOOST testing framework.")
cog.outl("")
cog.outl('It generates tests for "Packedness", "Payload Size" and "To/From Streams" for correct and efficient TX/RX, and generated payload sized, for stream reading/writing.')
cog.outl("")
]]]

[[[end]]]
*/

#include "allplatforms/testsuite/minunit/minunit.h"
#pragma warning( disable : 4244 )

#include "<<<CLASSNAME>>>.h"
using namespace <<<NAMESPACE>>>;

		/**[[[cog
		cog.outl("")

		alltests = []
		allstructs = interface.All()
		for s in allstructs:
			testname = s.Name +"_PackedNess"
			alltests.append(testname)
			cog.outl("MU_TEST("+ testname + ")")
			cog.outl("{")
			test = UnitTestWriter(interface,s,language,"ptr2"+s.Name)
			guts = test.WRITE_UNITTEST_PACKED_STRUCT_SIZE(language.WhiteSpace(0), UnitTestFramework.MINUNIT)
			for g in guts:
				cog.outl(g)
			cog.outl("}\n")

		messages = interface.Messages()
		for s in messages:
			testname = s.Name +"_FactoryPayloadSize"
			alltests.append(testname)
			cog.outl("MU_TEST("+ testname + ")")
			cog.outl("{")
			test = UnitTestWriter(interface,s,language,"ptr2"+s.Name)
			guts = test.WRITE_UNITTEST_FACTORY_PAYLOAD_SIZE(language.WhiteSpace(0), UnitTestFramework.MINUNIT)
			for g in guts:
				cog.outl(g)
			cog.outl("}\n")

		for s in messages:
			testname = s.Name +"_SerializeDeserialize"
			alltests.append(testname)
			cog.outl("MU_TEST("+ testname + ")")
			cog.outl("{")
			test = UnitTestWriter(interface,s,language,"ptr2"+s.Name)
			cog.outl("#ifdef __arm__")

			guts = test.WRITE_UNITTEST_TOFROM_BYTESTREAM(language.WhiteSpace(0), True, UnitTestFramework.MINUNIT)
			for g in guts:
				cog.outl(g)

			cog.outl('#else')

			guts = test.WRITE_UNITTEST_TOFROM_BYTESTREAM(language.WhiteSpace(0),False, UnitTestFramework.MINUNIT)
			for g in guts:
				cog.outl(g)

			cog.outl("#endif //__arm__")
			cog.outl("}\n")

		testgroupname = "<<<CLASSNAME>>>IF_Protocol_Suite"
		cog.outl("MU_TEST_SUITE("+testgroupname+")")
		cog.outl("{")
		for testname in alltests:
			cog.outl("\tMU_RUN_TEST(" + testname + ");")
		cog.outl("}")
		]]]*/

		//[[[end]]]