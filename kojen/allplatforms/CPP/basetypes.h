/**

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

*/
#pragma once

// https://sourceforge.net/p/predef/wiki/Architectures/
#if ( defined(_MSC_VER) || defined(__GNUC__) || defined(__clang__) ) && !defined(__arm__)

#include <iostream>
#include <assert.h>
#include <vector>
#include <memory>

//-->> Supported Test frameworks
#define testfw_CPUuTEST 0
#define testfw_BOOST 1

#define UNIT_TEST_FW testfw_CPUuTEST
#ifdef USING_BOOST
#define UNIT_TEST_FWtestfw_BOOST
#endif
//-->> End

//-->> Warning support
#if defined(_MSC_VER)
// No GCC '#warning' in Visual Studio
#define STRINGIZE_HELPER(x) #x
#define STRINGIZE(x) STRINGIZE_HELPER(x)
#define WARNING(desc) message(__FILE__ "(" STRINGIZE(__LINE__) ") : Warning: " #desc)
//// usage:
//#pragma WARNING(FIXME: Code removed because...)
#elif defined(__GNUC__)
#define WARNING(desc) #pragma message #desc
#endif
//-->> End


#ifdef USING_BOOST
	// If boost is defined, it should be dynamically linked, and this should be defined in the project settings.
	// Use boost pointers.
	#include <boost/smart_ptr.hpp>
	#include <boost/thread.hpp>
	#include <boost/thread/mutex.hpp>
	#include <boost/thread/condition_variable.hpp>
	#include <boost/cstdint.hpp>
	#include <boost/signals2.hpp>

	// Just a plain shared_ptr...use alias template
	template<typename T>
	using justaplain_shared_ptr = boost::shared_ptr<T>;

	#define CGEN_DECL_CLASS_PTR(classT) \
		class classT;\
		typedef boost::shared_ptr<classT > classT##_ptr; \
		typedef boost::shared_ptr<classT const > classT##_cptr; \
		typedef boost::weak_ptr<classT > classT##_wptr; \
		typedef boost::weak_ptr<classT const > classT##_cwptr; \

	#define CGEN_DECL_STRUCT_PTR(classT) \
		struct classT;\
		typedef boost::shared_ptr<classT > classT##_ptr; \
		typedef boost::shared_ptr<classT const > classT##_cptr; \
		typedef boost::weak_ptr<classT > classT##_wptr; \
		typedef boost::weak_ptr<classT const > classT##_cwptr; \

	using namespace boost;

	typedef boost::uint64_t	uint64;
	typedef boost::uint32_t	uint32;
	typedef boost::uint16_t	uint16;
	typedef boost::uint8_t	uint8;

	typedef boost::int64_t	int64;
	typedef boost::int32_t	int32;
	typedef boost::int16_t	int16;
	typedef boost::int8_t	int8;

#else
	// If boost is not defined, use C++011 equivalent types.
	#include <memory.h>
	#include <thread>
	#include <mutex>
	#include <condition_variable>

	// Just a plain shared_ptr...use alias template
	template<typename T>
	using justaplain_shared_ptr = std::shared_ptr<T>;

	// Idea would be to use equivalent types here. Problem is, std::thread is not interruptable like boost::thread.
	// Not sure how to fix this kludge...would be great if we were not limited to boost here...

	#define CGEN_DECL_CLASS_PTR(classT) \
	class classT;\
		typedef std::shared_ptr<classT > classT##_ptr; \
		typedef std::shared_ptr<classT const > classT##_cptr; \
		typedef std::weak_ptr<classT > classT##_wptr; \
		typedef std::weak_ptr<classT const > classT##_cwptr; \

	#define CGEN_DECL_STRUCT_PTR(classT) \
		struct classT;\
		typedef std::shared_ptr<classT > classT##_ptr; \
		typedef std::shared_ptr<classT const > classT##_cptr; \
		typedef std::weak_ptr<classT > classT##_wptr; \
		typedef std::weak_ptr<classT const > classT##_cwptr; \


	using namespace std;

	// 1 through N represent the number of bytes.
	// U represents unsigned.

	#if defined(_MSC_VER)

		//
		// Windows/Visual C++
		//
		typedef signed char				int8;
		typedef unsigned char			uint8;
		typedef signed short			int16;
		typedef unsigned short			uint16;
		typedef signed int				int32;
		typedef unsigned int			uint32;
		typedef signed __int64			int64;
		typedef unsigned __int64		uint64;

	#elif defined(__GNUC__) || defined(__clang__)

		//
		// Unix/GCC
		//
		typedef signed char				int8;
		typedef unsigned char			uint8;
		typedef signed short			int16;
		typedef unsigned short			uint16;
		typedef signed int				int32;
		typedef unsigned int			uint32;
		#if defined(__LP64__)
		typedef signed long				int64;
		typedef unsigned long			uint64;
		#else
		typedef signed long long		int64;
		typedef unsigned long long		uint64;
		#endif // defined(__LP64__)

	#endif // defined(_MSC_VER)

#endif // USING_BOOST */

#elif  defined(__arm__)

	//
	// Arm types
	//

	typedef signed char				int8;
	typedef unsigned char			uint8;
	typedef signed short			int16;
	typedef unsigned short			uint16;
	typedef signed int				int32;
	typedef unsigned int			uint32;
	#if defined(__LP64__)
	typedef signed long				int64;
	typedef unsigned long			uint64;
	#else
	typedef signed long long		int64;
	typedef unsigned long long		uint64;
	#endif // defined(__LP64__)

#endif // ( defined(_MSC_VER) || defined(__GNUC__) || defined(__clang__) ) && !defined(__arm__)

#if defined WIN32 || defined __CYGWIN__
	#ifdef KOJEN_EXPORTS
		#ifdef __GNUC__
			#define KOJEN_API __attribute__ ((dllexport))
		#else
			#define KOJEN_API __declspec(dllexport) // Note: actually gcc seems to also supports this syntax.
			// Disable needs to have dll-interface to be used by clients warning
			#pragma warning( disable : 4251 )
			#pragma warning( disable : 4267 )
		#endif
	#else
		#ifdef __GNUC__
			#define KOJEN_API __attribute__ ((dllimport))
		#else
			#define KOJEN_API __declspec(dllimport) // Note: actually gcc seems to also supports this syntax.
		#endif
	#endif
#else
	#if __GNUC__ >= 4
		#define KOJEN_API __attribute__ ((visibility ("default")))		
	#else
		#define KOJEN_API		
	#endif
#endif
