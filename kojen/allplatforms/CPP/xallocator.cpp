#include "xallocator.h"
#include "allocator.h"
#include "Fault.h"
#ifdef __FREERTOS__
#include <FreeRTOS.h>
#include <task.h>
#include <string.h>
#endif
#ifdef WIN32
#include <windows.h>
#include <synchapi.h>
#endif

using namespace std;

#ifndef CHAR_BIT
#define CHAR_BIT	8 
#endif

#if defined(__FREERTOS__)
// use taskENTER_CRITICAL
#else if defined(_MSC_VER)
static CRITICAL_SECTION _criticalSection; 
static bool _xallocInitialized = false;
#else if defined(__GNUC__) || defined(__clang__) ) && !defined(__arm__)
/* Sample C/C++, Unix/Linux */
#include <pthread.h>
/* This is the critical section object (statically allocated). */
static pthread_mutex_t _criticalSection =  PTHREAD_RECURSIVE_MUTEX_INITIALIZER_NP;
static bool _xallocInitialized = false;
#endif

// Define STATIC_POOLS to switch from heap blocks mode to static pools mode
//#define STATIC_POOLS 
#ifdef STATIC_POOLS
	// Update this section as necessary if you want to use static memory pools.
	// See also xalloc_init() and xalloc_destroy() for additional updates required.
	#define MAX_ALLOCATORS	12
	#define MAX_BLOCKS		32

	// Create static storage for each static allocator instance
	uint8* _allocator8 [sizeof(AllocatorPool<uint8[8], MAX_BLOCKS>)];
	uint8* _allocator16 [sizeof(AllocatorPool<uint8[16], MAX_BLOCKS>)];
	uint8* _allocator32 [sizeof(AllocatorPool<uint8[32], MAX_BLOCKS>)];
	uint8* _allocator64 [sizeof(AllocatorPool<uint8[64], MAX_BLOCKS>)];
	uint8* _allocator128 [sizeof(AllocatorPool<uint8[128], MAX_BLOCKS>)];
	uint8* _allocator256 [sizeof(AllocatorPool<uint8[256], MAX_BLOCKS>)];
	uint8* _allocator396 [sizeof(AllocatorPool<uint8[396], MAX_BLOCKS>)];
	uint8* _allocator512 [sizeof(AllocatorPool<uint8[512], MAX_BLOCKS>)];
	uint8* _allocator768 [sizeof(AllocatorPool<uint8[768], MAX_BLOCKS>)];
	uint8* _allocator1024 [sizeof(AllocatorPool<uint8[1024], MAX_BLOCKS>)];
	uint8* _allocator2048 [sizeof(AllocatorPool<uint8[2048], MAX_BLOCKS>)];	
	uint8* _allocator4096 [sizeof(AllocatorPool<uint8[4096], MAX_BLOCKS>)];

	// Array of pointers to all allocator instances
	static Allocator* _allocators[MAX_ALLOCATORS];

#else
	#define MAX_ALLOCATORS  15
	static Allocator* _allocators[MAX_ALLOCATORS];
#endif	// STATIC_POOLS

// For C++ applications, must define AUTOMATIC_XALLOCATOR_INIT_DESTROY to 
// correctly ensure allocators are initialized before any static user C++ 
// construtor/destructor executes which might call into the xallocator API. 
// This feature costs 1-byte of RAM per C++ translation unit. This feature 
// can be disabled only under the following circumstances:
// 
// 1) The xallocator is only used within C files. 
// 2) STATIC_POOLS is undefined and the application never exits main (e.g. 
// an embedded system). 
//
// In either of the two cases above, call xalloc_init() in main at startup, 
// and xalloc_destroy() before main exits. In all other situations
// XallocInitDestroy must be used to call xalloc_init() and xalloc_destroy().
#ifdef AUTOMATIC_XALLOCATOR_INIT_DESTROY
int XallocInitDestroy::refCount = 0;
XallocInitDestroy::XallocInitDestroy() 
{ 
	// Track how many static instances of XallocInitDestroy are created
	if (refCount++ == 0)
		xalloc_init();
}

XallocInitDestroy::~XallocInitDestroy()
{
	// Last static instance to have destructor called?
	if (--refCount == 0)
		xalloc_destroy();
}
#endif	// AUTOMATIC_XALLOCATOR_INIT_DESTROY

/// Returns the next higher powers of two. For instance, pass in 12 and 
/// the value returned would be 16. 
/// @param[in] k - numeric value to compute the next higher power of two.
/// @return	The next higher power of two based on the input k. 
template <class T>
T nexthigher(T k) 
{
    k--;
    for (size_t i=1; i<sizeof(T)*CHAR_BIT; i<<=1)
        k |= (k >> i);
    return k+1;
}

#ifdef __FREERTOS__
// Simply use a critical section of FreeRTOS
#else
/// Create the xallocator lock. Call only one time at startup. 
static void lock_init()
{
#if defined(_MSC_VER)
	BOOL success = InitializeCriticalSectionAndSpinCount(&_criticalSection, 0x00000400);
	ASSERT_TRUE(success != 0);
#endif
	_xallocInitialized = TRUE;
}

/// Destroy the xallocator lock.
static void lock_destroy()
{
#if defined(_MSC_VER)
	DeleteCriticalSection(&_criticalSection);
#endif
	_xallocInitialized = FALSE;
}

/// Lock the shared resource. 
static inline void lock_get()
{
	if (_xallocInitialized == FALSE)
		return;
#if defined(_MSC_VER)
	EnterCriticalSection(&_criticalSection);
#else if defined(__GNUC__) || defined(__clang__) ) && !defined(__arm__)
	/* Enter the critical section -- other threads are locked out */
    pthread_mutex_lock( &_criticalSection );
 #endif
}

/// Unlock the shared resource. 
static inline void lock_release()
{
	if (_xallocInitialized == FALSE)
		return;
#if defined(_MSC_VER)
	LeaveCriticalSection(&_criticalSection);
#else if defined(__GNUC__) || defined(__clang__) ) && !defined(__arm__)
	/*Leave the critical section -- other threads can now pthread_mutex_lock()  */
    pthread_mutex_unlock( &_criticalSection );
#endif
}
#endif

/// Stored a pointer to the allocator instance within the block region. 
///	a pointer to the client's area within the block.
/// @param[in] block - a pointer to the raw memory block. 
///	@param[in] size - the client requested size of the memory block.
/// @return	A pointer to the client's address within the raw memory block. 
static inline void *set_block_allocator(void* block, Allocator* allocator)
{
	// Cast the raw block memory to a Allocator pointer
	Allocator** pAllocatorInBlock = static_cast<Allocator**>(block);

	// Write the size into the memory block
	*pAllocatorInBlock = allocator;

	// Advance the pointer past the Allocator* block size and return a pointer to
	// the client's memory region
	return ++pAllocatorInBlock;
}

/// Gets the size of the memory block stored within the block.
/// @param[in] block - a pointer to the client's memory block. 
/// @return	The original allocator instance stored in the memory block.
static inline Allocator* get_block_allocator(void* block)
{
	// Cast the client memory to a Allocator pointer
	Allocator** pAllocatorInBlock = static_cast<Allocator**>(block);

	// Back up one Allocator* position to get the stored allocator instance
	pAllocatorInBlock--;

	// Return the allocator instance stored within the memory block
	return *pAllocatorInBlock;
}

/// Returns the raw memory block pointer given a client memory pointer. 
/// @param[in] block - a pointer to the client memory block. 
/// @return	A pointer to the original raw memory block address. 
static inline void *get_block_ptr(void* block)
{
	// Cast the client memory to a Allocator* pointer
	Allocator** pAllocatorInBlock = static_cast<Allocator**>(block);

	// Back up one Allocator* position and return the original raw memory block pointer
	return --pAllocatorInBlock;
}

/// Returns an allocator instance matching the size provided
/// @param[in] size - allocator block size
/// @return Allocator instance handling requested block size or NULL
/// if no allocator exists. 
static inline Allocator* find_allocator(size_t size)
{
	for (int i=0; i<MAX_ALLOCATORS; i++)
	{
		if (_allocators[i] == 0)
			break;
		
		if (_allocators[i]->GetBlockSize() == size)
			return _allocators[i];
	}
	
	return NULL;
}

/// Insert an allocator instance into the array
/// @param[in] allocator - An allocator instance
static inline void insert_allocator(Allocator* allocator)
{
	for (int i=0; i<MAX_ALLOCATORS; i++)
	{
		if (_allocators[i] == 0)
		{
			_allocators[i] = allocator;
			return;
		}
	}
	
	ASSERT();
}

/// This function must be called exactly one time *before* any other xallocator
/// API is called. XallocInitDestroy constructor calls this function automatically. 
extern "C" void xalloc_init()
{
#ifdef __FREERTOS__
#else	
	lock_init();
#endif

#ifdef STATIC_POOLS
	// For STATIC_POOLS mode, the allocators must be initialized before any other
	// static user class constructor is run. Therefore, use placement new to initialize
	// each allocator into the previously reserved static memory locations.
	new (&_allocator8) AllocatorPool<uint8[8], MAX_BLOCKS>();
	new (&_allocator16) AllocatorPool<uint8[16], MAX_BLOCKS>();
	new (&_allocator32) AllocatorPool<uint8[32], MAX_BLOCKS>();
	new (&_allocator64) AllocatorPool<uint8[64], MAX_BLOCKS>();
	new (&_allocator128) AllocatorPool<uint8[128], MAX_BLOCKS>();
	new (&_allocator256) AllocatorPool<uint8[256], MAX_BLOCKS>();
	new (&_allocator396) AllocatorPool<uint8[396], MAX_BLOCKS>();
	new (&_allocator512) AllocatorPool<uint8[512], MAX_BLOCKS>();
	new (&_allocator768) AllocatorPool<uint8[768], MAX_BLOCKS>();
	new (&_allocator1024) AllocatorPool<uint8[1024], MAX_BLOCKS>();
	new (&_allocator2048) AllocatorPool<uint8[2048], MAX_BLOCKS>();
	new (&_allocator4096) AllocatorPool<uint8[4096], MAX_BLOCKS>();

	// Populate allocator array with all instances 
	_allocators[0] = (Allocator*)&_allocator8;
	_allocators[1] = (Allocator*)&_allocator16;
	_allocators[2] = (Allocator*)&_allocator32;
	_allocators[3] = (Allocator*)&_allocator64;
	_allocators[4] = (Allocator*)&_allocator128;
	_allocators[5] = (Allocator*)&_allocator256;
	_allocators[6] = (Allocator*)&_allocator396;
	_allocators[7] = (Allocator*)&_allocator512;
	_allocators[8] = (Allocator*)&_allocator768;
	_allocators[9] = (Allocator*)&_allocator1024;
	_allocators[10] = (Allocator*)&_allocator2048;
	_allocators[11] = (Allocator*)&_allocator4096;
#endif
}

/// Called one time when the application exits to cleanup any allocated memory.
/// ~XallocInitDestroy destructor calls this function automatically. 
extern "C" void xalloc_destroy()
{
#ifdef __FREERTOS__
	taskENTER_CRITICAL();
#else	
	lock_get();
#endif

#ifdef STATIC_POOLS
	for (int i=0; i<MAX_ALLOCATORS; i++)
	{
		_allocators[i]->~Allocator();
		_allocators[i] = 0;
	}
#else
	for (int i=0; i<MAX_ALLOCATORS; i++)
	{
		if (_allocators[i] == 0)
			break;
		delete _allocators[i];
		_allocators[i] = 0;
	}
#endif

#ifdef __FREERTOS__
	taskEXIT_CRITICAL();
#else
	lock_release();

	lock_destroy();
#endif
}

/// Get an Allocator instance based upon the client's requested block size.
/// If a Allocator instance is not currently available to handle the size,
///	then a new Allocator instance is create.
///	@param[in] size - the client's requested block size.
///	@return An Allocator instance that handles blocks of the requested
///	size.
extern "C" Allocator* xallocator_get_allocator(size_t size)
{
	// Based on the size, find the next higher powers of two value.
	// Add sizeof(Allocator*) to the requested block size to hold the size
	// within the block memory region. Most blocks are powers of two,
	// however some common allocator block sizes can be explicitly defined
	// to minimize wasted storage. This offers application specific tuning.
	size_t blockSize = size + sizeof(Allocator*);
	if (blockSize > 256 && blockSize <= 396)
		blockSize = 396;
	else if (blockSize > 512 && blockSize <= 768)
		blockSize = 768;
	else
		blockSize = nexthigher<size_t>(blockSize);

	Allocator* allocator = find_allocator(blockSize);

#ifdef STATIC_POOLS
	ASSERT_TRUE(allocator != NULL);
#else
	// If there is not an allocator already created to handle this block size
	if (allocator == NULL)  
	{
		// Create a new allocator to handle blocks of the size required
		allocator = new Allocator(blockSize, 0, 0, "xallocator");

		// Insert allocator into array
		insert_allocator(allocator);
	}
#endif
	
	return allocator;
}

/// Allocates a memory block of the requested size. The blocks are created from
///	the fixed block allocators.
///	@param[in] size - the client requested size of the block.
/// @return	A pointer to the client's memory block.
extern "C" void *xmalloc(size_t size)
{
#ifdef __FREERTOS__
	taskENTER_CRITICAL();
#else	
	lock_get();
#endif
	// Allocate a raw memory block 
	Allocator* allocator = xallocator_get_allocator(size);
	void* blockMemoryPtr = allocator->Allocate(sizeof(Allocator*) + size);

#ifdef __FREERTOS__
	taskEXIT_CRITICAL();
#else
	lock_release();
#endif

	// Set the block Allocator* within the raw memory block region
	void* clientsMemoryPtr = set_block_allocator(blockMemoryPtr, allocator);
	return clientsMemoryPtr;
}

/// Frees a memory block previously allocated with xalloc. The blocks are returned
///	to the fixed block allocator that originally created it.
///	@param[in] ptr - a pointer to a block created with xalloc.
extern "C" void xfree(void* ptr)
{
	if (ptr == 0)
		return;

	// Extract the original allocator instance from the caller's block pointer
	Allocator* allocator = get_block_allocator(ptr);

	// Convert the client pointer into the original raw block pointer
	void* blockPtr = get_block_ptr(ptr);

#ifdef __FREERTOS__
	taskENTER_CRITICAL();
#else
	lock_get();
#endif

	// Deallocate the block 
	allocator->Deallocate(blockPtr);

#ifdef __FREERTOS__
	taskEXIT_CRITICAL();
#else
	lock_release();
#endif
}

/// Reallocates a memory block previously allocated with xalloc.
///	@param[in] ptr - a pointer to a block created with xalloc.
///	@param[in] size - the client requested block size to create.
extern "C" void *xrealloc(void *oldMem, size_t size)
{
	if (oldMem == 0)
		return xmalloc(size);

	if (size == 0) 
	{
		xfree(oldMem);
		return 0;
	}
	else 
	{
		// Create a new memory block
		void* newMem = xmalloc(size);
		if (newMem != 0) 
		{
			// Get the original allocator instance from the old memory block
			Allocator* oldAllocator = get_block_allocator(oldMem);
			size_t oldSize = oldAllocator->GetBlockSize() - sizeof(Allocator*);

			// Copy the bytes from the old memory block into the new (as much as will fit)
			memcpy(newMem, oldMem, (oldSize < size) ? oldSize : size);

			// Free the old memory block
			xfree(oldMem);

			// Return the client pointer to the new memory block
			return newMem;
		}
		return 0;
	}
}

/// Output xallocator usage statistics
extern "C" void xalloc_stats()
{
#ifdef __FREERTOS__
	taskENTER_CRITICAL();
	
	for (int i=0; i<MAX_ALLOCATORS; i++)
	{
		if (_allocators[i] == 0)
			break;
#ifdef printf
		if (_allocators[i]->GetName() != NULL)
			printf("%s\r\n",_allocators[i]->GetName());
		printf(" Block Size: %i\r\n",_allocators[i]->GetBlockSize());
		printf(" Block Count: %i\r\n",_allocators[i]->GetBlockCount());
		printf(" Blocks In Use: %i\r\n",_allocators[i]->GetBlocksInUse());
#endif
	}
	
	taskEXIT_CRITICAL();
#else
	lock_get();
	
	for (INT i=0; i<MAX_ALLOCATORS; i++)
	{
		if (_allocators[i] == 0)
			break;

		if (_allocators[i]->GetName() != NULL)
			cout << _allocators[i]->GetName();
		cout << " Block Size: " << _allocators[i]->GetBlockSize();
		cout << " Block Count: " << _allocators[i]->GetBlockCount();
		cout << " Blocks In Use: " << _allocators[i]->GetBlocksInUse();
		cout << endl;
	}
	
	lock_release();
#endif
}


