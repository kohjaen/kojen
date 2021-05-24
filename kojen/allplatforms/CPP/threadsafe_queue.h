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

#ifdef __arm__

#ifdef __FREERTOS__
#pragma message "Use threadsafe_queue_FreeRTOS.h."
#else
#pragma message "threadsafe_queue needs to be ported to your ARM RTOS."
#endif // __FREERTOS__

#else

#include <queue>
#include <mutex>
#include <condition_variable>
#include <memory>

namespace XKoJen
{
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
            : m_stopped{ false }
        {}
        /** Destructor
        */
        virtual ~threadsafe_queue()
        {
            m_stopped = true;
            m_cond.notify_all();
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
            std::unique_lock<std::mutex> lk(m_mutex);
            m_cond.wait(lk, [this]{return !m_data.empty() || m_stopped; });
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
            std::lock_guard<std::mutex> lk(m_mutex);
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
            std::unique_lock<std::mutex> lk(m_mutex);
            m_cond.wait(lk,[this]{return !m_data.empty() || m_stopped;});
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
            std::lock_guard<std::mutex> lk(m_mutex);
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
            std::lock_guard<std::mutex> lk(m_mutex);
            m_data.push(std::make_unique<T>(std::move(value)));
            m_cond.notify_one();
        }
        /** Push a shared_ptr to an item on the queue and transfer complete ownership.
        *
        *	@param value is the item to put on the queue. Ownership is transferred using C++11 move symantics, so the original point will no longer be valid after.
        */
        void push(ptr_type& value)
        {
            std::lock_guard<std::mutex> lk(m_mutex);
            m_data.push(std::move(value));
            m_cond.notify_one();
        }
        /** For the case where a thread is waiting for another thread to put something on the queue ... but termination is required.
        *
        *	@see wait_and_pop()
        */
        void wake_up()
        {
            {
                std::lock_guard<std::mutex> lk(m_mutex);
                m_stopped = true;
            }
            m_cond.notify_all();
        }
        /** Indicates the size of queue
        *
        * @return the number of items in the queue.
        */
        size_t size()
        {
            std::lock_guard<std::mutex> lk(m_mutex);
            return m_data.size();
        }
        /** Indicates that the queue is empty.
        *
        *	@return true if the queue has no items, or false if it has items.
        */
        bool empty() const
        {
            std::lock_guard<std::mutex> lk(m_mutex);
            return m_data.empty();
        }
        private:
            mutable std::mutex m_mutex;
            std::queue< ptr_type > m_data;
            std::condition_variable m_cond;
            bool m_stopped;
    };
}
#endif // __arm__
