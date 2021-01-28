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

#include "minunit/minunit.h"

#ifdef __arm__
// Embedded platforms have other constraints (no new, use of fixed block allocators for example).
#include "allocator.h"

#ifdef __FREERTOS__
#include "threadsafe_queue_FreeRTOS.h"
#include "threaded_dispatcher_FreeRTOS.h"

namespace {
	struct Event
	{
	public:
		virtual ~Event() {}
		Event() {};

		/** Move-only
		*/
		Event(const Event& other) = delete;
		Event& operator=(Event& other) = delete;
		Event(Event&& other) = default;
		Event& operator=(Event&& other) = default;
	};
	struct EventPlay : public Event {
		/** Move-only
		*/
		EventPlay(const EventPlay& other) = delete;
		EventPlay& operator=(EventPlay& other) = delete;
		EventPlay(EventPlay&& other) = default;
		EventPlay& operator=(EventPlay&& other) = default;
		EventPlay() {};

		uint16_t m_track_no;
		DECLARE_ALLOCATOR
	};
	IMPLEMENT_ALLOCATOR(EventPlay, 0, 0)

	typedef std::unique_ptr<EventPlay> EventPlay_ptr;
}

MU_TEST(ThreadsafeQueue_move_ownership_and_API)
{
	size_t heap_start_run = xPortGetFreeHeapSize();
	XKoJen::threadsafe_queue<Event> a_queue;

	size_t heap_before = xPortGetFreeHeapSize();
	size_t heap_during2, heap_during1, heap_during3;

	// Get the current task hand...which should be from the named thread 'MainThrd' found in test_main.cpp
	xTaskHandle m_handle = xTaskGetHandle("MainThrd");

	UBaseType_t stack_before = uxTaskGetStackHighWaterMark(m_handle);
	UBaseType_t stack_during2, stack_during1, stack_during3;

	for (uint32_t i = 0; i < 1000; ++i)
	{
		heap_during1 = xPortGetFreeHeapSize();
		stack_during1 = uxTaskGetStackHighWaterMark(m_handle);
		for (uint32_t j = 0; j < 16; ++j)
		{
			std::unique_ptr<EventPlay> ev0 = std::make_unique<EventPlay>(EventPlay());
			ev0->m_track_no = (i + j) % 16000;
			a_queue.push(std::move(ev0));
			mu_assert(ev0 == nullptr, "ev0 still owns its data...");
		}
		// How to test a full queue? STL Queue is not really limited...but regular queue is configured to 16.
#ifdef _USE_STL_QUEUE
#else
		std::unique_ptr<EventPlay> evFull = std::make_unique<EventPlay>(EventPlay());
		evFull->m_track_no = 666;
		mu_assert(evFull != nullptr, "evFull does not own its data...");
#endif
		stack_during3 = uxTaskGetStackHighWaterMark(m_handle);
		heap_during3 = xPortGetFreeHeapSize();
		for (uint32_t j = 0; j < 16; ++j)
		{
			std::unique_ptr<Event> ev;
			ev = a_queue.wait_and_pop();
			mu_check(ev != nullptr);
			auto* evP = dynamic_cast<EventPlay*>(ev.get());
			mu_check(evP != nullptr);
			mu_check(evP->m_track_no == (i + j) % 16000);
		}
		heap_during2 = xPortGetFreeHeapSize();
		stack_during2 = uxTaskGetStackHighWaterMark(m_handle);
	}
	size_t sizeof_event = sizeof(Event);
	size_t heap_after = xPortGetFreeHeapSize();
	UBaseType_t stack_after = uxTaskGetStackHighWaterMark(m_handle);

	uint32 u1 = EventPlay::GetBlocksInUse();
	uint32 u2 = EventPlay::GetAllocations();
	uint32 u3 = EventPlay::GetDeallocations();
}

namespace {
#define DISPATCH_THREAD_PRIORITY 4
#define DISPATCH_THREAD_STACK 500
	class TestDispatch : public XKoJen::threaded_dispatcher<Event>
	{
	public:
		TestDispatch() : XKoJen::threaded_dispatcher<Event>("TestDispatch", DISPATCH_THREAD_PRIORITY, DISPATCH_THREAD_STACK) {};
		int m_DispatchCnt = 0;
		virtual void handle_dispatch(ptr_type item) override
		{
			m_DispatchCnt++;
		}
	};
}
MU_TEST(Threaded_dispatcher_API)
{
	TestDispatch ts;
	ts.Start();
	ts.dispatch(EventPlay{});
	ts.dispatch(EventPlay{});
	ts.dispatch(EventPlay{});
	mu_check(ts.m_DispatchCnt == 3);
}

MU_TEST_SUITE(Threads_Suite) {
	MU_RUN_TEST(ThreadsafeQueue_move_ownership_and_API);
	MU_RUN_TEST(Threaded_dispatcher_API);
}

#else
#pragma message "Threading test need to be added for your platform."
#endif

#else

#pragma warning( disable : 4127 )

#include "../threaded_dispatcher.h"
#include "../waitcondition.h"
#include <functional>

	/////////////////////////////////////////////////////////////////////////////////////////////////
	// Move-enabled complex class
	// Taken from here when brushing up on the subject :
	//    https://docs.microsoft.com/en-us/cpp/cpp/move-constructors-and-move-assignment-operators-cpp?view=vs-2019
	namespace {
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
	}
	/////////////////////////////////////////////////////////////////////////////////////////////////

	/////////////////////////////////////////////////////////////////////////////////////////////////
	/// Fixture 
	namespace {
		struct Group_threadsafe_queue
		{
			XKoJen::threadsafe_queue<MemoryBlock> m_testQ;
			MemoryBlock_ptr m_block_a;
			MemoryBlock_ptr m_block_b;
			MemoryBlock_ptr m_block_c;

			Group_threadsafe_queue()
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
					mu_assert(m_block_a != nullptr, "m_block_a does not own its data...");
					mu_assert(m_block_b != nullptr, "m_block_b does not own its data...");
					mu_assert(m_block_c != nullptr, "m_block_c does not own its data...");
				}
				else
				{
					mu_assert(m_block_a == nullptr, "m_block_a still owns its data...");
					mu_assert(m_block_b == nullptr, "m_block_b still owns its data...");
					mu_assert(m_block_c == nullptr, "m_block_c still owns its data...");
				}
			}

			void test_size_and_empty(size_t size)
			{
				if (size == 0)
				{
					mu_check(m_testQ.empty()); // usage : empty()
					mu_check(m_testQ.size() == 0); // usage : size()
				}
				else
				{
					mu_check(!m_testQ.empty()); // usage : empty()
					mu_check(m_testQ.size() == size); // usage : size()
				}
			}
		};
	}

	/////////////////////////////////////////////////////////////////////////////////////////////////
	/// Test
	MU_TEST(ThreadsafeQueue_move_ownership_and_API)
	{
		Group_threadsafe_queue fixture;
		// Try and pop without waiting when the queue is empty should be nullptr
		MemoryBlock_ptr empty;
		empty = fixture.m_testQ.try_pop(); // usage : try_pop (1)

		mu_check(empty == nullptr);
		mu_check(!fixture.m_testQ.try_pop(*empty)); // usage : try_pop (2)

		fixture.test_size_and_empty(0); // usage : empty(), size()
		// Local ptrs should be initialized and own data...
		fixture.test_local_ptrs_ownership(true);
		fixture.transfer_local_ptrs_to_Q(); // usage : push() (2)
		// Local ptrs should be empty and queue owns data...
		fixture.test_local_ptrs_ownership(false);
		fixture.test_size_and_empty(3); // usage : empty(), size()
		fixture.m_block_a = fixture.m_testQ.try_pop(); // usage : try_pop (1)
		fixture.m_block_b.reset(new MemoryBlock(0));
		auto popped = fixture.m_testQ.try_pop(*fixture.m_block_b); // usage : try_pop (2)
		fixture.m_block_c = fixture.m_testQ.try_pop(); // usage : try_pop (1)
		fixture.test_size_and_empty(0); // usage : empty(), size()

		mu_check(popped);

		// Local ptrs should be initialized and own data...
		fixture.test_local_ptrs_ownership(true);

		// Use by-value instead of shared_ptr
		fixture.transfer_values_to_Q(); // usage : push() (1)

		fixture.test_size_and_empty(3); // usage : empty(), size()
		// cache old values to make sure values are actually swapped...
		size_t len_a = fixture.m_block_a->Length();
		size_t len_b = fixture.m_block_b->Length();
		size_t len_c = fixture.m_block_c->Length();

		fixture.m_block_a = fixture.m_testQ.wait_and_pop(); // usage : wait_and_pop (2)
		popped = fixture.m_testQ.wait_and_pop(*fixture.m_block_b); // usage : wait_and_pop (1)
		fixture.m_block_c = fixture.m_testQ.wait_and_pop(); // usage : wait_and_pop (2)

		fixture.test_size_and_empty(0); // usage : empty(), size()

		mu_check(popped);

		mu_check(len_a != fixture.m_block_a->Length());
		mu_check(len_b != fixture.m_block_b->Length());
		mu_check(len_c != fixture.m_block_c->Length());
		// wake_up() is meant to be used in a threaded context.
 	}

	/////////////////////////////////////////////////////////////////////////////////////////////////
	// Function object dispatcher class
	namespace {
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
	}
	/////////////////////////////////////////////////////////////////////////////////////////////////
	/// Fixture 
	namespace {
		struct Group_dispatcher_queue
		{
			FunctionDispatcher_ptr m_dispatcher;
			Group_dispatcher_queue()
			{
				m_dispatcher.reset(new FunctionDispatcher());
			}
		};
	}
	/////////////////////////////////////////////////////////////////////////////////////////////////
	/// Test
	MU_TEST(Threaded_dispatcher_API)
	{
		Group_dispatcher_queue fixture;

		size_t expected_cnt = 0;
		for (int x = 0; x < 100; ++x) {
			fixture.m_dispatcher->dispatch([] {printf("My Dispatch 1!\n"); });
			expected_cnt++;
			fixture.m_dispatcher->dispatch([] {printf("My Dispatch 2!\n"); });
			expected_cnt++;
			fixture.m_dispatcher->dispatch([] {printf("My Dispatch 3!\n"); });
			expected_cnt++;
			fixture.m_dispatcher->dispatch([] {printf("My Dispatch 4!\n"); });
			expected_cnt++;
		}
		std::this_thread::sleep_for(std::chrono::milliseconds(2000));

		mu_check(fixture.m_dispatcher->m_CNT == expected_cnt);

		fixture.m_dispatcher.reset();
		// Above reset should not block. All threads should terminate.
	}

	MU_TEST_SUITE(Threads_Suite) {
		MU_RUN_TEST(ThreadsafeQueue_move_ownership_and_API);
		MU_RUN_TEST(Threaded_dispatcher_API);
	}

#endif // __arm__