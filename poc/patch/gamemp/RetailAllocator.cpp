// Retail Engine.dll owns the heap of objects crossing the GameMP boundary.
// Compile as x86, /MD, without the SDK precompiled header.
#include <cstddef>
#include <climits>
#include <new>

__declspec(dllimport) void *AllocMemory(long size);
__declspec(dllimport) void FreeMemory(void *memory);

void *operator new(std::size_t size) {
  if (size > LONG_MAX) throw std::bad_alloc();
  return AllocMemory(static_cast<long>(size ? size : 1));
}
void *operator new[](std::size_t size) { return ::operator new(size); }
void operator delete(void *memory) noexcept { if (memory) FreeMemory(memory); }
void operator delete[](void *memory) noexcept { ::operator delete(memory); }
void operator delete(void *memory, std::size_t) noexcept { ::operator delete(memory); }
void operator delete[](void *memory, std::size_t) noexcept { ::operator delete(memory); }
