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

#ifdef __FREERTOS__

#include "FreeRTOS.h"
#include <semphr.h> // Freertos
#include <event_groups.h>

#include <memory>
#include <algorithm>

//#define _USE_STL_QUEUE
#ifdef _USE_STL_QUEUE
// #include <queue>
// The problem with STL is not the stability or speed of their algorithms, but their unfettered use of the heap.
// Luckily there is a work-around which resolves that using fixed-block allocators for all STL containers (which also gives great speed improvements, even on a PC)...
#include "xqueue.h"
#endif

namespace XKoJen
{
#ifdef _USE_STL_QUEUE	
#else
	/** A 'static' fixed-size queue (no dynamic memory allocation), that follows the same interface as a std::queue, except for having a size template paramter.
		Define your size, up to to a max of 255 items.
		Uses move semantics.
	*/
	template<typename ptr_type, const uint8_t max_size = 255>
	class queue
	{
	public:
		queue(){
			configASSERT(max_size <= 255);
		}
		virtual ~queue(){}

		ptr_type& front(){
			return m_Items[m_Tail];
		}
		void pop(){
			if(m_Size>0){
				m_Tail++;
				m_Tail %= max_size; // moot if max_size is 255
				m_Size--;
			}
		}
// This is like a 'get front and pop'.
//		ptr_type pop(){			
//			ptr_type res;
//			if(m_Size>0)
//			{
//				res = std::move(m_Items[m_Tail++]);
//				m_Tail %= max_size; // moot if max_size is 255
//				m_Size--;
//			}
//			return res;			
//		}	
		
		/** As this is a fixed-size queue ... will not push if the queue is full (and will return false).
		*/
		bool push(ptr_type value){			
			if (m_Size == max_size)
				return false;
			m_Items[m_Head++] = std::move(value);
			m_Head %= max_size; // moot if max_size is 255
			m_Size++;
			return true;
		}
		
		bool empty() const{
			return (m_Size == 0);
		}
		
	protected:
		ptr_type m_Items[max_size];
		uint8_t m_Head=0;
		uint8_t m_Tail=0;
		uint8_t m_Size=0;
	};
#endif // _USE_STL_QUEUE

	/************************************************************************/
	/* BEGIN : Attempt STL interface for cleaner programming                */
	/************************************************************************/
		
	/// Definitions for dispatch event flags (condition variable emulation)
	#define DISPATCH_WAKE_EVT    (0x1)
	#define DISPATCH_EXIT_EVT    (0x2)

	// FWD declare
	struct condition_variable;
	/** Standard cplusplus style Lock -> use scope to lock/unlock a semaphore/mutex etc.
	*/
	struct lock_guard
	{
		explicit lock_guard(SemaphoreHandle_t& sem) :m_sem(sem) {
			// no need to check if this is true ... this blocks until it is
			auto status = xSemaphoreTake(m_sem, (TickType_t)portMAX_DELAY);
			configASSERT(status == pdTRUE); // "Failed to lock mutex!"
		}
		~lock_guard() {
			auto status = xSemaphoreGive(m_sem);
			configASSERT(status == pdTRUE); // "Failed to unlock mutex!"
		}
	private:
		friend struct condition_variable;
		SemaphoreHandle_t& m_sem;
	};
	/** Standard cplusplus style condition variable
	*/
	struct condition_variable
	{
		explicit condition_variable(){
			m_cond_flags = xEventGroupCreate();
			configASSERT(m_cond_flags != NULL); // "Failed to create event group!"
		}
		~condition_variable()
		{
			notify_exit();
		}
		template <class Predicate>
		void wait(lock_guard& lock, Predicate pred)
		{
			if(!pred()){
				// unlock
				auto status = xSemaphoreGive(lock.m_sem);
				configASSERT(status == pdTRUE); // "Failed to unlock mutex!"

				// wait for data (and exit) and clear the flags.
				xEventGroupWaitBits(m_cond_flags,DISPATCH_WAKE_EVT | DISPATCH_EXIT_EVT, pdTRUE, pdFALSE, portMAX_DELAY);

				// lock
				status = xSemaphoreTake(lock.m_sem, (TickType_t)portMAX_DELAY);
				configASSERT(status == pdTRUE); // "Failed to lock mutex!"
			}
		}
		void notify_one(){
			// Notifies threads that new work is in the queue
			auto status = xEventGroupSetBits(m_cond_flags, DISPATCH_WAKE_EVT);
			// According to : https://www.freertos.org/xEventGroupSetBits.html 
			// if a task was waiting (and/or has a higher priority) for the this bit
			// it may have already processed it (and cleared it) by the time this call returns...
			// so its not a good idea to assume any state here.
			//configASSERT(status != 0); // "Failed to set WAKE event flags!"
		}
		void notify_exit(){
			auto status = xEventGroupSetBits(m_cond_flags,DISPATCH_EXIT_EVT);
			//configASSERT(status != 0); // "Failed to set EXIT event flags!"
		}
		private:
			EventGroupHandle_t m_cond_flags;
	};
	
	/************************************************************************/
	/* END : Attempt STL interface for cleaner programming                */
	/************************************************************************/

	/** A templatized thread-safe queue. Ownership of items to/from by pushing/popping is transferred using C++11 move symantics.
	*	
	*	Thanks to Mr Anthony Williams, author of the boost::thread and std::thread libraries.
	*	This was slightly modified and extended from his original example in C++ Concurrency in Action.
	*	\example Test.ThreadingConcepts.cpp
	*/
	template<typename T>
	class threadsafe_queue
	{
	public:
		/** Type of pointer managed by the queue.
		* 
		*	A pointer is used so that the queue can hold base-class-of-polymorphic types.
		*	A unique_ptr is used as its more efficient compared to a shared_ptr, and it forces
		*	move-symmantics...the queue should own items whilst they are in the queue.
		*/
		typedef std::unique_ptr<T> ptr_type;
		/** Constructor
		*/
		explicit threadsafe_queue()
			//: m_stopped{ false }
		{
			m_mutex = xSemaphoreCreateMutex();
			configASSERT(m_mutex != NULL); // "Failed to create mutex!"
		}
		/** Destructor
		*/
		virtual ~threadsafe_queue()
		{
			//m_stopped = true;
			//m_cond.notify_all();
			m_cond.notify_exit();
		}
		/** Wait for an item to be put on the queue and return it (in 'value') therafter.
		*	If the thread that owns the queue was terminated whilst the waiting thread is waiting,
		*	it will unblock and value will remain untouched.
		* 
		*	@param value an output argument used to transfer ownership if successful.
		*	@return true if value was popped, false if not.
		*/
		bool wait_and_pop(T& value)
		{
			lock_guard lk(m_mutex);
			m_cond.wait(lk, [this]{return !m_data.empty() /*|| m_stopped*/;});
			if (!m_data.empty()){
				value = std::move(*m_data.front());
				m_data.pop();
				return true;
			}
			return false;
		}
		/** Try to pop an item (into 'value') without waiting and return immediately. 
		* 
		*	@param value an output argument used to transfer ownership if successful.
		*	@return true if an item was transferred to 'value' or false if the queue is empty.
		*/
		bool try_pop(T& value)
		{
			lock_guard lk(m_mutex);
			if(m_data.empty())
				return false;
			value = std::move(*m_data.front());
			m_data.pop();
			return true;
		}
		/** Wait for an item to be put on the queue and return it therafter.
		*	If the thread that owns the queue was terminated whilst the waiting thread is waiting,
		*	it will unblock and a nullptr returned.
		* 
		*	@return an item from the queue if available, otherwise a nullptr if the queue was 'stopped'.
		*	@see wake_up()
		*/
		ptr_type wait_and_pop()
		{
			lock_guard lk(m_mutex);
			m_cond.wait(lk, [this]{return !m_data.empty()/* || m_stopped*/;});
			ptr_type res;
			if(!m_data.empty()){
				res = std::move(m_data.front());
				m_data.pop();
			}
			return res;
		}
		/** Try to pop and item without waiting and return immediately.
		* 
		*	@return an item ofrom the queue if available, otherwise an empty pointer is returned if the queue is empty.
		*/
		ptr_type try_pop()
		{
			lock_guard lk(m_mutex);
			ptr_type res;
			if(m_data.empty())
				return res;
			res = std::move(m_data.front());
			m_data.pop();
			return res;
		}
		/** Push an item on the queue and transfer ownership.
		* 
		*	@param value is the value to put on the queue.
		*/
		void push(T value)
		{
			lock_guard lk(m_mutex);			
			m_data.push(std::make_unique<T>(std::move(value)));
			
			m_cond.notify_one();
		}
		/** Push a shared_ptr to an item on the queue and transfer complete ownership.
		* 
		*	@param value is the item to put on the queue. Ownership is transferred using C++11 move symantics, so the original point will no longer be valid after.
		*/
		//void push(ptr_type& value)
		void push(ptr_type value)
		{
			lock_guard lk(m_mutex);
			m_data.push(std::move(value));
			
			m_cond.notify_one();
		}
		/** For the case where a thread is waiting for another thread to put something on the queue ... but termination is required.
		* 
		*	@see wait_and_pop()
		*/
		void wake_up()
		{
			m_cond.notify_exit();
		}
		/** Indicates the size of queue
		* 
		* @return the number of items in the queue.
		*/
		size_t size()
		{
			lock_guard lk(m_mutex);
			return m_data.size();
		}
		/** Indicates that the queue is empty.
		* 
		*	@return true if the queue has no items, or false if it has items.
		*/
		bool empty() const
		{
			lock_guard lk(m_mutex);
			return m_data.empty();
		}
		private:
			mutable SemaphoreHandle_t m_mutex;
			//std::queue< ptr_type > m_data;
#ifdef _USE_STL_QUEUE			
			xqueue<ptr_type> m_data;
#else
			XKoJen::queue<ptr_type, 16> m_data;
#endif // _USE_STL_QUEUE			
			condition_variable m_cond;
			//bool m_stopped;
	};

}
#endif // __FREERTOS__