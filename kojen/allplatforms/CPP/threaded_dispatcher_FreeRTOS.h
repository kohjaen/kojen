/**

    MIT License

    Copyright (c) 2021 Eugene Grobbelaar (email : koh.jaen@yahoo.de)

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

#include "threadsafe_queue_FreeRTOS.h"
#include "thread_FreeRTOS.h"

namespace XKoJen
{
    /** A templatized threaded dispatcher. Uses a threadsafe_queue, and contains as many threads as desired.
    *
    *   Any movable type T can be dispatched on a thread. This may be structs, or function pointers etc.
    *   Simply inherit from this with your type 'T' of dispatch queue, and implement the handle_dispatch member.
    *
    *	\example Test.ThreadingConcepts.cpp
    */
    template<typename T>
    class threaded_dispatcher : public thread {
    public:
        /** dependant types.
        */
        typedef threadsafe_queue<T> queue_type;
        typedef typename threadsafe_queue<T>::ptr_type ptr_type;

        /** Constructor
        */
        explicit threaded_dispatcher(char const*name, unsigned portBASE_TYPE priority,	unsigned portSHORT stackDepth=configMINIMAL_STACK_SIZE)
          : thread(name, priority, stackDepth)
        {}
        /** Destructor
        */
        virtual ~threaded_dispatcher()
        {
            m_shutting_down = true;
            m_queue.wake_up();
        }
        /** Dispatch an item and transfer ownership to the dispatcher.
        *
        *	@param value is the value to dispatch.
        */
        void dispatch(T value)
        {
            m_queue.push(std::move(value));
        }
        /** Dispatch a shared_ptr to an item and transfer complete ownership.
        *
        *	@param value is the item to dispatch. Ownership is transferred using C++11 move symantics, so the original point will no longer be valid after.
        */
        void dispatch(ptr_type& value)
        {
            m_queue.push(std::move(value));
        }
    protected:
        /** Handle the item to be dispatched.
        *
        *	@param item the item to be dispatched.
        */
        virtual void handle_dispatch(ptr_type item) = 0;
    private:
        virtual void Run() override
        {
            while (!m_shutting_down) {
                ptr_type item_to_dispatch; // wait_and_pop will return nullptr if interrupted.
                if ((item_to_dispatch = m_queue.wait_and_pop()) && (!m_shutting_down)){
                    handle_dispatch(std::move(item_to_dispatch));
                }
            }
        }
        threadsafe_queue<T> m_queue;
        bool m_shutting_down = false;
    };
}
#endif // __FREERTOS__