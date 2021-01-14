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

#include "basetypes.h"

namespace XKoJen 
{
	/** \brief wait_condition - Wait condition for one thread to block other threads and wake them up again.

			The blocked threads are put to sleep so that their scheduler time can be distributed to active threads,
			as opposed to wasting cpu time by spinning.
		*/
	class KOJEN_API wait_condition
	{
	public:
		/** The thread which should wait needs to call this.
		*/
		void wait();
		/** The thread which should wait (for a certain time only) needs to call this.
		*	
		*	@param ms_to_wait the number of milliseconds to wait for.
		*	@return 'false' for timeout, otherwise 'true'.
		*/
		bool wait(const int ms_to_wait);
		/** The thread which controls the enabling of other threads to waiting.
		*/
		void enable_wait();
		/** The thread which controls the disabling of other threads waiting.
		*/
		void disable_wait();
		/** Constructor
		*/
		explicit wait_condition(const bool start_waiting);
		/** Destructr
		*/
		virtual ~wait_condition();
		/** No copy constructor/operator or move constructor/operator.
		*/
		wait_condition(const wait_condition& other) = delete;
		wait_condition& operator=(wait_condition& other) = delete;
		wait_condition(wait_condition&& other) = delete;
		wait_condition& operator=(wait_condition&& other) = delete;
	protected:
		bool m_wait;
		std::mutex m_mutex;
		std::condition_variable m_condition;
	};
}