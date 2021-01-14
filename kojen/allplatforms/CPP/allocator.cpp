#include "allocator.h"
#include <new>

#ifdef __FREERTOS__
#include <FreeRTOS.h>
#include <task.h>

// FreeRTOS is written in C. 
// C++ calls 'malloc' and 'free' directly.
// - this has a problem in that its out of FreeRTOS management.
// For C++ we thus want to use the FreeRTOS heap, as its malloc/free are thread safe, and it would be a good idea to keep track of consumption.

void * operator new( size_t size )
{
	return pvPortMalloc( size );
}

void * operator new[]( size_t size )
{
	return pvPortMalloc(size);
}

void operator delete( void * ptr )
{
	vPortFree ( ptr );
}

void operator delete[]( void * ptr )
{
	vPortFree ( ptr );
}
#else
#include <assert.h>
#endif // __FREERTOS__

//------------------------------------------------------------------------------
// Constructor
//------------------------------------------------------------------------------
Allocator::Allocator(size_t size, uint32 objects, char* memory, const char* name) :
    m_blockSize(size < sizeof(long*) ? sizeof(long*):size),
    m_objectSize(size),
    m_maxObjects(objects),
    m_pHead(NULL),
    m_poolIndex(0),
    m_blockCnt(0),
    m_blocksInUse(0),
    m_allocations(0),
    m_deallocations(0),
    m_name(name)
{
    // If using a fixed memory pool 
	if (m_maxObjects)
	{
		// If caller provided an external memory pool
		if (memory)
		{
			m_pPool = memory;
			m_allocatorMode = STATIC_POOL;
		}
		else 
		{
			m_pPool = (char*)new char[m_blockSize * m_maxObjects];
			m_allocatorMode = HEAP_POOL;
		}
	}
	else
		m_allocatorMode = HEAP_BLOCKS;
}

//------------------------------------------------------------------------------
// Destructor
//------------------------------------------------------------------------------
Allocator::~Allocator()
{
	// If using pool then destroy it, otherwise traverse free-list and 
	// destroy each individual block
	if (m_allocatorMode == HEAP_POOL)
		delete [] m_pPool;
	else if (m_allocatorMode == HEAP_BLOCKS)
	{
		while(m_pHead)
			delete [] (char*)Pop();
	}
}

//------------------------------------------------------------------------------
// Allocate
//------------------------------------------------------------------------------
void* Allocator::Allocate(size_t size)
{
#ifdef __FREERTOS__
	configASSERT(size <= m_objectSize);
#else	
    assert(size <= m_objectSize);
#endif
	
    // If can't obtain existing block then get a new one
    void* pBlock = Pop();
    if (!pBlock)
    {
        // If using a pool method then get block from pool,
        // otherwise using dynamic so get block from heap
        if (m_maxObjects)
        {
            // If we have not exceeded the pool maximum
            if(m_poolIndex < m_maxObjects)
            {
                pBlock = (void*)(m_pPool + (m_poolIndex++ * m_blockSize));
            }
            else
            {
                // Get the pointer to the new handler
                std::new_handler handler = std::set_new_handler(0);
                std::set_new_handler(handler);

                // If a new handler is defined, call it
                if (handler)
                    (*handler)();
                else
#ifdef __FREERTOS__
					configASSERT(0);
#else				
                    assert(0);
#endif
            }
        }
        else
        {
        	m_blockCnt++;
            pBlock = (void*)new char[m_blockSize];
        }
    }

    m_blocksInUse++;
    m_allocations++;
	
    return pBlock;
}

//------------------------------------------------------------------------------
// Deallocate
//------------------------------------------------------------------------------
void Allocator::Deallocate(void* pBlock)
{
    Push(pBlock);
	m_blocksInUse--;
	m_deallocations++;
}

//------------------------------------------------------------------------------
// Push
//------------------------------------------------------------------------------
void Allocator::Push(void* pMemory)
{
    Block* pBlock = (Block*)pMemory;
    pBlock->pNext = m_pHead;
    m_pHead = pBlock;
}

//------------------------------------------------------------------------------
// Pop
//------------------------------------------------------------------------------
void* Allocator::Pop()
{
    Block* pBlock = NULL;

    if (m_pHead)
    {
        pBlock = m_pHead;
        m_pHead = m_pHead->pNext;
    }

    return (void*)pBlock;
}





