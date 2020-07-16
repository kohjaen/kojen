/**
[[[cog
import cog
from LanguageCPP import *
language = LanguageCPP()
for g in language.LicenseAgreement():
	cog.outl(g)
]]]

[[[end]]]
*/
#pragma once
namespace <<<NAMESPACE>>>
{
	/**
	Unit tests should be run after creating an interface before integration.
	*/
	bool RunTests();
}
