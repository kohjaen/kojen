/**

This file is part of 'KoJen'.

'KoJen' is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

'KoJen' is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with 'KoJen'.  If not, see <http://www.gnu.org/licenses/>.
For any feedback please contact the original author : koh.jaen@yahoo.de.

*/

#ifdef __arm__

#include <asf.h>
#ifdef FAIL
#undef FAIL
#endif // FAIL

// Present assumption : CppUTest is used on ARM

#else

#pragma warning( disable : 4127 )

#include "../threaded_dispatcher.h"
#include "../waitcondition.h"
#include <functional>

#if UNIT_TEST_FW == testfw_BOOST
#include <boost/test/unit_test.hpp>
#elif UNIT_TEST_FW == testfw_CPUuTEST
#include "CppUTest/TestHarness.h"
#endif

	/////////////////////////////////////////////////////////////////////////////////////////////////
	// Move-enabled complex class
	// Taken from here when brushing up on the subject :
	//    https://docs.microsoft.com/en-us/cpp/cpp/move-constructors-and-move-assignment-operators-cpp?view=vs-2019

	class MemoryBlock
	{
	public:
		// Simple constructor that initializes the resource.
		explicit MemoryBlock(size_t length)
			: _length(length)
			, _data(new int[length])
		{
			std::cout << "In MemoryBlock(size_t). length = " << _length << "." << std::endl;
			memset(_data, 0, length * sizeof(int));
		}
	
		// Destructor.
		~MemoryBlock()
		{
			std::cout << "In ~MemoryBlock(). length = " << _length << ".";
			if (_data != nullptr)
			{
				std::cout << " Deleting resource.";
				// Delete the resource.
				delete[] _data;
			}
			std::cout << std::endl;
		}
	
		// Copy constructor.
		MemoryBlock(const MemoryBlock& other)
			: _length(other._length)
			, _data(new int[other._length])
		{
			std::cout << "In MemoryBlock(const MemoryBlock&). length = " << other._length << ". Copying resource." << std::endl;
			std::copy(other._data, other._data + _length, _data);
		}
	
		// Copy assignment operator.
		MemoryBlock& operator=(const MemoryBlock& other)
		{
			std::cout << "In operator=(const MemoryBlock&). length = " << other._length << ". Copying resource." << std::endl;
			if (this != &other)
			{
				// Free the existing resource.
				delete[] _data;
				_length = other._length;
				_data = new int[_length];
				std::copy(other._data, other._data + _length, _data);
			}
			return *this;
		}
	
		// Move constructor.
		MemoryBlock(MemoryBlock&& other) noexcept
			: _data(nullptr)
			, _length(0)
		{
			std::cout << "In MemoryBlock(MemoryBlock&&). length = " << other._length << ". Moving resource." << std::endl;
			*this = std::move(other);
		}
	
		// Move assignment operator.
		MemoryBlock& operator=(MemoryBlock&& other) noexcept
		{
			std::cout << "In operator=(MemoryBlock&&). length = " << other._length << "." << std::endl;
			if (this != &other)
			{
				// Free the existing resource.
				delete[] _data;
				// Copy the data pointer and its length from the
				// source object.
				_data = other._data;
				_length = other._length;
				// Release the data pointer from the source object so that
				// the destructor does not free the memory multiple times.
				other._data = nullptr;
				other._length = 0;
			}
			return *this;
		}

		// Retrieves the length of the data resource.
		size_t Length() const
		{
			return _length;
		}
	
	private:
		size_t _length; // The length of the resource.
		int* _data; // The resource.
	};
	typedef XKoJen::threadsafe_queue<MemoryBlock>::ptr_type MemoryBlock_ptr;
	/////////////////////////////////////////////////////////////////////////////////////////////////

	/////////////////////////////////////////////////////////////////////////////////////////////////
	/// Fixture 
#if UNIT_TEST_FW == testfw_CPUuTEST
	TEST_GROUP(Group_threadsafe_queue)
#elif UNIT_TEST_FW == testfw_BOOST
	struct Group_threadsafe_queue
#endif // __arm__
	{
		XKoJen::threadsafe_queue<MemoryBlock> m_testQ;
		MemoryBlock_ptr m_block_a;
		MemoryBlock_ptr m_block_b;
		MemoryBlock_ptr m_block_c;

#if UNIT_TEST_FW == testfw_CPUuTEST
		void setup()
#elif UNIT_TEST_FW == testfw_BOOST
		Group_threadsafe_queue()
#endif
		{
			m_block_a.reset(new MemoryBlock(33));
			m_block_b.reset(new MemoryBlock(66));
			m_block_c.reset(new MemoryBlock(99));
		}

		void transfer_local_ptrs_to_Q()
		{
			// usage : push() (2)
			m_testQ.push(m_block_a);
			m_testQ.push(m_block_b);
			m_testQ.push(m_block_c);
		}
		void transfer_values_to_Q()
		{
			// usage : push() (1)
			m_testQ.push(MemoryBlock(25));
			m_testQ.push(MemoryBlock(75));
			m_testQ.push(MemoryBlock(50));
		}

		void test_local_ptrs_ownership(bool owns)
		{
			if (owns)
			{
#if UNIT_TEST_FW == testfw_CPUuTEST
				CHECK_TRUE_TEXT(m_block_a != nullptr, "m_block_a does not own its data...");
				CHECK_TRUE_TEXT(m_block_b != nullptr, "m_block_b does not own its data...");
				CHECK_TRUE_TEXT(m_block_c != nullptr, "m_block_c does not own its data...");
#elif UNIT_TEST_FW == testfw_BOOST
				BOOST_REQUIRE_MESSAGE(m_block_a != nullptr, "m_block_a does not own its data...");
				BOOST_REQUIRE_MESSAGE(m_block_b != nullptr, "m_block_b does not own its data...");
				BOOST_REQUIRE_MESSAGE(m_block_c != nullptr, "m_block_c does not own its data...");
#endif
			}
			else
			{
#if UNIT_TEST_FW == testfw_CPUuTEST
				CHECK_TRUE_TEXT(m_block_a == nullptr, "m_block_a still owns its data...");
				CHECK_TRUE_TEXT(m_block_b == nullptr, "m_block_b still owns its data...");
				CHECK_TRUE_TEXT(m_block_c == nullptr, "m_block_c still owns its data...");
#elif UNIT_TEST_FW == testfw_BOOST
				BOOST_REQUIRE_MESSAGE(m_block_a == nullptr, "m_block_a still owns its data...");
				BOOST_REQUIRE_MESSAGE(m_block_b == nullptr, "m_block_b still owns its data...");
				BOOST_REQUIRE_MESSAGE(m_block_c == nullptr, "m_block_c still owns its data...");
#endif
			}
		}

		void test_size_and_empty(size_t size)
		{
			if (size == 0)
			{
#if UNIT_TEST_FW == testfw_CPUuTEST
				CHECK_TRUE(m_testQ.empty()); // usage : empty()
				CHECK_EQUAL(m_testQ.size(), 0); // usage : size()
#elif UNIT_TEST_FW == testfw_BOOST
				BOOST_REQUIRE(m_testQ.empty()); // usage : empty()
				BOOST_REQUIRE(m_testQ.size() == 0); // usage : size()
#endif
			}
			else
			{
#if UNIT_TEST_FW == testfw_CPUuTEST
				CHECK_FALSE(m_testQ.empty()); // usage : empty()
				CHECK_EQUAL(m_testQ.size(), size); // usage : size()
#elif UNIT_TEST_FW == testfw_BOOST
				BOOST_REQUIRE(!m_testQ.empty()); // usage : empty()
				BOOST_REQUIRE(m_testQ.size() == size); // usage : size()
#endif
			}
		}

#if UNIT_TEST_FW == testfw_CPUuTEST
		void teardown() {
		}
#endif
	};

	/////////////////////////////////////////////////////////////////////////////////////////////////
	/// Test
#if UNIT_TEST_FW == testfw_CPUuTEST
	TEST(Group_threadsafe_queue, TEST_move_ownership_and_API)
#elif UNIT_TEST_FW == testfw_BOOST

	BOOST_AUTO_TEST_SUITE(XKoJen_suite);
	BOOST_AUTO_TEST_SUITE(threadsafe_queue_dispatcher_suite);

	BOOST_FIXTURE_TEST_CASE(TEST_move_ownership_and_API, Group_threadsafe_queue)
#endif
	{
		// Try and pop without waiting when the queue is empty should be nullptr
		MemoryBlock_ptr empty;
		empty = m_testQ.try_pop(); // usage : try_pop (1)
#if UNIT_TEST_FW == testfw_CPUuTEST
		CHECK_TRUE(empty == nullptr);
		// Because the queue is empty, this should not crash (moving into uninitialized ptr)
		CHECK_FALSE(m_testQ.try_pop(*empty)); // usage : try_pop (2)
#elif UNIT_TEST_FW == testfw_BOOST
		BOOST_REQUIRE(empty == nullptr);
		BOOST_REQUIRE(!m_testQ.try_pop(*empty)); // usage : try_pop (2)
#endif
		test_size_and_empty(0); // usage : empty(), size()
		// Local ptrs should be initialized and own data...
		test_local_ptrs_ownership(true);
		transfer_local_ptrs_to_Q(); // usage : push() (2)
		// Local ptrs should be empty and queue owns data...
		test_local_ptrs_ownership(false);
		test_size_and_empty(3); // usage : empty(), size()
		m_block_a = m_testQ.try_pop(); // usage : try_pop (1)
		m_block_b.reset(new MemoryBlock(0));
		auto popped = m_testQ.try_pop(*m_block_b); // usage : try_pop (2)
		m_block_c = m_testQ.try_pop(); // usage : try_pop (1)
		test_size_and_empty(0); // usage : empty(), size()
#if UNIT_TEST_FW == testfw_CPUuTEST
		CHECK_TRUE(popped);
#elif UNIT_TEST_FW == testfw_BOOST
		BOOST_REQUIRE(popped);
#endif
		// Local ptrs should be initialized and own data...
		test_local_ptrs_ownership(true);

		// Use by-value instead of shared_ptr
		transfer_values_to_Q(); // usage : push() (1)

		test_size_and_empty(3); // usage : empty(), size()
		// cache old values to make sure values are actually swapped...
		size_t len_a = m_block_a->Length();
		size_t len_b = m_block_b->Length();
		size_t len_c = m_block_c->Length();

		m_block_a = m_testQ.wait_and_pop(); // usage : wait_and_pop (2)
		popped = m_testQ.wait_and_pop(*m_block_b); // usage : wait_and_pop (1)
		m_block_c = m_testQ.wait_and_pop(); // usage : wait_and_pop (2)

		test_size_and_empty(0); // usage : empty(), size()
#if UNIT_TEST_FW == testfw_CPUuTEST
		CHECK_TRUE(popped);
#elif UNIT_TEST_FW == testfw_BOOST
		BOOST_REQUIRE(popped);
#endif
#if UNIT_TEST_FW == testfw_CPUuTEST
		CHECK_TRUE(len_a != m_block_a->Length());
		CHECK_TRUE(len_b != m_block_b->Length());
		CHECK_TRUE(len_c != m_block_c->Length());
#elif UNIT_TEST_FW == testfw_BOOST
		BOOST_REQUIRE(len_a != m_block_a->Length());
		BOOST_REQUIRE(len_b != m_block_b->Length());
		BOOST_REQUIRE(len_c != m_block_c->Length());
#endif
		// wake_up() is meant to be used in a threaded context.
 	}

	/////////////////////////////////////////////////////////////////////////////////////////////////
	// Function object dispatcher class
	typedef std::function<void(void)> function_t;
	class FunctionDispatcher : public XKoJen::threaded_dispatcher<function_t>
	{
	public:
		size_t m_CNT = 0;
		FunctionDispatcher() : XKoJen::threaded_dispatcher<function_t>(std::string("FunctionDispatcher"), 1) {}
	protected:
		virtual void handle_dispatch(FunctionDispatcher::ptr_type item) override
		{
			(*item)();
			m_CNT++;
		}
	};
	typedef std::shared_ptr<FunctionDispatcher> FunctionDispatcher_ptr;
	/////////////////////////////////////////////////////////////////////////////////////////////////
	/// Fixture 
#if UNIT_TEST_FW == testfw_CPUuTEST
	TEST_GROUP(Group_dispatcher_queue)
#elif UNIT_TEST_FW == testfw_BOOST
	struct Group_dispatcher_queue
#endif // __arm__
	{
		FunctionDispatcher_ptr m_dispatcher;

#if UNIT_TEST_FW == testfw_CPUuTEST
		void setup()
#elif UNIT_TEST_FW == testfw_BOOST
		Group_dispatcher_queue()
#endif
		{
			m_dispatcher.reset(new FunctionDispatcher());
		}

#if UNIT_TEST_FW == testfw_CPUuTEST
		void teardown() {
		}
#endif
	};

	/////////////////////////////////////////////////////////////////////////////////////////////////
	/// Test
#if UNIT_TEST_FW == testfw_CPUuTEST
	TEST(Group_dispatcher_queue, TEST_threaded_dispatcher_and_API)
#elif UNIT_TEST_FW == testfw_BOOST	
	BOOST_FIXTURE_TEST_CASE(TEST_threaded_dispatcher_and_API, Group_dispatcher_queue)
#endif
	{
		size_t expected_cnt = 0;
		for (int x = 0; x < 100; ++x) {
			m_dispatcher->dispatch([] {printf("My Dispatch 1!\n"); });
			expected_cnt++;
			m_dispatcher->dispatch([] {printf("My Dispatch 2!\n"); });
			expected_cnt++;
			m_dispatcher->dispatch([] {printf("My Dispatch 3!\n"); });
			expected_cnt++;
			m_dispatcher->dispatch([] {printf("My Dispatch 4!\n"); });
			expected_cnt++;
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(2000));

#if UNIT_TEST_FW == testfw_CPUuTEST
		CHECK_EQUAL(m_dispatcher->m_CNT, expected_cnt);
#elif UNIT_TEST_FW == testfw_BOOST
		BOOST_REQUIRE(m_dispatcher->m_CNT == expected_cnt);
#endif
		m_dispatcher.reset();
		// Above reset should not block. All threads should terminate.
	}

	///

#if UNIT_TEST_FW == testfw_CPUuTEST
#else

BOOST_AUTO_TEST_SUITE_END();
BOOST_AUTO_TEST_SUITE_END();
#endif

#endif // __arm__