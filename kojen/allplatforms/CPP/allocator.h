#pragma once

#include "basetypes.h"
#include <stddef.h>

/// See http://www.codeproject.com/Articles/1083210/An-efficient-Cplusplus-fixed-block-memory-allocato
class KOJEN_API Allocator
{
public:
    /// Constructor
    /// @param[in]  size - size of the fixed blocks
    /// @param[in]  objects - maximum number of object. If 0, new blocks are
	///		created off the heap as necessary.
	/// @param[in]	memory - pointer to a block of static memory for allocator or NULL 
	///		to obtain memory from global heap. If not NULL, the objects argument 
	///		defines the size of the memory block (size x objects = memory size in bytes).
	///	@param[in]	name - optional allocator name string.
    Allocator(size_t size, uint32 objects=0, char* memory = NULL, const char* name=NULL);

    /// Destructor
    ~Allocator();

    /// Get a pointer to a memory block. 
    /// @param[in]  size - size of the block to allocate
    /// @return     Returns pointer to the block. Otherwise NULL if unsuccessful.
    void* Allocate(size_t size);

    /// Return a pointer to the memory pool. 
    /// @param[in]  pBlock - block of memory deallocate (i.e push onto free-list)
    void Deallocate(void* pBlock);

    /// Get the allocator name string.
    /// @return		A pointer to the allocator name or NULL if none was assigned.
    const char* GetName() { return m_name; }

    /// Gets the fixed block memory size, in bytes, handled by the allocator.
    /// @return		The fixed block size in bytes.
    size_t GetBlockSize() { return m_blockSize; }

    /// Gets the maximum number of blocks created by the allocator.
    /// @return		The number of fixed memory blocks created.
    uint32 GetBlockCount() { return m_blockCnt; }

    /// Gets the number of blocks in use.
    /// @return		The number of blocks in use by the application.
    uint32 GetBlocksInUse() { return m_blocksInUse; }

    /// Gets the total number of allocations for this allocator instance.
    /// @return		The total number of allocations.
    uint32 GetAllocations() { return m_allocations; }

    /// Gets the total number of deallocations for this allocator instance.
    /// @return		The total number of deallocations.
    uint32 GetDeallocations() { return m_deallocations; }
	
private:
    /// Push a memory block onto head of free-list.
    /// @param[in]  pMemory - block of memory to push onto free-list
    void Push(void* pMemory);

    /// Pop a memory block from head of free-list.
    /// @return     Returns pointer to the block. Otherwise NULL if unsuccessful.
    void* Pop();

    struct Block
    {
        Block* pNext;
    };

	enum AllocatorMode { HEAP_BLOCKS, HEAP_POOL, STATIC_POOL };

    const size_t m_blockSize;
    const size_t m_objectSize;
    const uint32 m_maxObjects;
	AllocatorMode m_allocatorMode;
    Block* m_pHead;
    char* m_pPool;
    uint32 m_poolIndex;
    uint32 m_blockCnt;
    uint32 m_blocksInUse;
    uint32 m_allocations;
    uint32 m_deallocations;
    const char* m_name;
};

// Template class to create external memory pool
template <class T, uint32 Objects>
class AllocatorPool : public Allocator
{
public:
	AllocatorPool() : Allocator(sizeof(T), Objects, m_memory)
	{
	}
private:
	char m_memory[sizeof(T) * Objects];
};

// macro to provide header file interface
#define DECLARE_ALLOCATOR \
    public: \
        void* operator new(size_t size) { \
            return _allocator.Allocate(size); \
        } \
        void operator delete(void* pObject) { \
            _allocator.Deallocate(pObject); \
        } \
		static uint32 GetBlocksInUse() { return _allocator.GetBlocksInUse(); }\
		static uint32 GetAllocations() { return _allocator.GetAllocations(); }\
		static uint32 GetDeallocations() { return _allocator.GetDeallocations(); }\
    private: \
        static Allocator _allocator; 

// macro to provide source file interface
#define IMPLEMENT_ALLOCATOR(class, objects, memory) \
	Allocator class::_allocator(sizeof(class), objects, memory, #class);



