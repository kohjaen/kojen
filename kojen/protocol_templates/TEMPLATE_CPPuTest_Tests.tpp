/**
[[[cog
import cog
from <<<PYIFGENNAME>>> import *
from LanguageCPP import *
interface = CreateInterface()
language  = LanguageCPP()

for g in language.LicenseAgreement():
	cog.outl(g)

cog.outl("This generates unit tests for use with the CPPuTEST testing framework.")
cog.outl("")
cog.outl('It generates tests for "Packedness", "Payload Size" and "To/From Streams" for correct and efficient TX/RX, and generated payload sized, for stream reading/writing.')
cog.outl("")
]]]

[[[end]]]
*/

#ifdef __arm__
#define CPPUTEST_MEM_LEAK_DETECTION_DISABLED // Using the memory pool and not defining this causes problems...
#endif // __arm__
#include <CppUTest/TestHarness.h>
#include "<<<CLASSNAME>>>.h"
using namespace <<<NAMESPACE>>>;

		/**[[[cog
		cog.outl("")

		testgroupname = "<<<CLASSNAME>>>IF_Protocol_Suite"

		cog.outl("TEST_GROUP("+testgroupname+")")
		cog.outl("{")
		cog.outl("void setup(){")
		cog.outl("	// Memory pool should not leak. See inline tests...")
		cog.outl("	MemoryLeakWarningPlugin::turnOffNewDeleteOverloads();")
		cog.outl("}")
		cog.outl("void teardown(){")
		cog.outl("	MemoryLeakWarningPlugin::turnOnNewDeleteOverloads();")
		cog.outl("}")
		cog.outl("};\n")

		allstructs = interface.All()
		for s in allstructs:
			cog.outl("TEST("+testgroupname+", "+s.Name +"_PackedNess)")
			cog.outl("{")
			test = UnitTestWriter(interface,s,language,"ptr2"+s.Name)
			guts = test.WRITE_UNITTEST_PACKED_STRUCT_SIZE(language.WhiteSpace(0), UnitTestFramework.CPPuTEST)
			for g in guts:
				cog.outl(g)
			cog.outl("}\n")

		messages = interface.Messages()
		for s in messages:
			cog.outl("TEST("+testgroupname+", "+s.Name +"_FactoryPayloadSize)")
			cog.outl("{")
			test = UnitTestWriter(interface,s,language,"ptr2"+s.Name)
			guts = test.WRITE_UNITTEST_FACTORY_PAYLOAD_SIZE(language.WhiteSpace(0), UnitTestFramework.CPPuTEST)
			for g in guts:
				cog.outl(g)
			cog.outl("}\n")

		for s in messages:
			cog.outl("TEST("+testgroupname+", "+s.Name +"_SerializeDeserialize)")
			cog.outl("{")
			test = UnitTestWriter(interface,s,language,"ptr2"+s.Name)
			cog.outl("#ifdef __arm__")

			guts = test.WRITE_UNITTEST_TOFROM_BYTESTREAM(language.WhiteSpace(0), True, UnitTestFramework.CPPuTEST)
			for g in guts:
				cog.outl(g)

			cog.outl('#else')

			guts = test.WRITE_UNITTEST_TOFROM_BYTESTREAM(language.WhiteSpace(0),False, UnitTestFramework.CPPuTEST)
			for g in guts:
				cog.outl(g)

			cog.outl("#endif //__arm__")
			cog.outl("}\n")
			
		]]]*/

		//[[[end]]]