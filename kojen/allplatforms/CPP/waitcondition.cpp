#include "waitcondition.h"
#include <chrono>

namespace XKoJen
{
	wait_condition::wait_condition(const bool start_waiting) : m_wait { start_waiting }
	{}
	wait_condition::~wait_condition()
	{
		m_wait = false;
		m_condition.notify_all();
	}
	void wait_condition::wait()
	{
		std::unique_lock<std::mutex> lk(m_mutex);
		m_condition.wait(lk, [&] {return !m_wait; });
		lk.unlock();
	}
	bool wait_condition::wait(const int ms_to_wait)
	{
		std::unique_lock<std::mutex> lk(m_mutex);
		auto wakeup_time = std::chrono::system_clock::now() + std::chrono::milliseconds(ms_to_wait);
		bool result = m_condition.wait_until(lk, wakeup_time, [&] {return !m_wait; });
		lk.unlock();
		return result;
	}
	void wait_condition::enable_wait()
	{
		std::lock_guard<std::mutex> lk(m_mutex);
		m_wait = true;
	}
	void wait_condition::disable_wait()
	{
		std::lock_guard<std::mutex> lk(m_mutex);
		m_wait = false;
		m_condition.notify_all();
	}
}