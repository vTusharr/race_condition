**Graph-Theoretic and Logical Modeling of Race Condition Avoidance in Concurrent Scheduling**

## Overview

This project demonstrates race conditions and their solutions through deep technical analysis:
- **C Code Simulation**: Real race conditions and Peterson's algorithm implementation
- **Instruction Analysis**: Shows how C code translates to machine instructions and where races occur
- **Modern Architecture Challenges**: CPU pipelining, instruction reordering, cache coherency issues
- **C11 Atomics Solution**: Why atomics and memory barriers are essential on modern CPUs
- **Mutex Solutions**: Modern practical synchronization primitives for real-world applications
- **Formal Verification**: Visual proof that Peterson's algorithm guarantees mutual exclusion

## Core Concepts

### Race Condition: The Problem
A race condition occurs when multiple threads access shared memory without proper synchronization, leading to data corruption.

#### C Code Example (Unprotected Counter):
```c
void* increment_counter(void* arg) {
    for (int i = 0; i < ITERATIONS/2; i++) {
        // === RACE CONDITION ZONE ===
        long temp = counter;    // 1. READ
        temp = temp + 1;        // 2. MODIFY  
        counter = temp;         // 3. WRITE
        // Problem: Not atomic! Context switch can occur between operations
    }
}
```

#### What Happens at Assembly Level:
```asm
; Thread 1:
movl    counter(%rip), %eax    ; READ counter into register (counter=0)
; >>> CONTEXT SWITCH HERE! <<<
addl    $1, %eax                ; Increment register (eax=1)
movl    %eax, counter(%rip)    ; WRITE back to memory (counter=1)

; Thread 2 (interleaved):
movl    counter(%rip), %eax    ; READ counter (STILL 0! Not updated yet)
addl    $1, %eax                ; Increment (eax=1)
movl    %eax, counter(%rip)    ; WRITE (counter=1, lost Thread 1's update!)
```

**Result**: Expected counter=2, Actual counter=1 (Lost update!)

### Peterson's Algorithm: The Classical Solution

Peterson's algorithm achieves mutual exclusion using only two shared variables:
- `flag[2]`: Interest flags (each thread signals intent to enter critical section)
- `turn`: Tie-breaker (whose turn it is when both want access)

#### C Code with C11 Atomics:
```c
_Atomic bool flag[2] = {false, false};
_Atomic int turn = 0;
long counter = 0;

void* peterson_process(void* arg) {
    int id = *((int*)arg);
    int other = 1 - id;
    
    for (int i = 0; i < ITERATIONS/2; i++) {
        // === ENTRY PROTOCOL ===
        atomic_store_explicit(&flag[id], true, memory_order_seq_cst);
        atomic_store_explicit(&turn, other, memory_order_seq_cst);
        
        // Wait while other wants access AND it's their turn
        while (atomic_load_explicit(&flag[other], memory_order_seq_cst) && 
               atomic_load_explicit(&turn, memory_order_seq_cst) == other) {
            // Busy wait
        }
        
        // === CRITICAL SECTION (PROTECTED) ===
        long temp = counter;
        temp = temp + 1;
        counter = temp;
        // === END CRITICAL SECTION ===
        
        // === EXIT PROTOCOL ===
        atomic_store_explicit(&flag[id], false, memory_order_seq_cst);
    }
}
```

**Result**: Always counter=200000 (100000 iterations × 2 threads). No lost updates!

## Installation

### Prerequisites
- Python 3.12+
- GCC with C11 support 

### Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### Install GCC 

## Usage

### Run Main Application

```bash
uv run src/main.py
```

### Menu Options

1. **Race Condition State Graph** - NetworkX graph showing problematic paths
2. **Race Condition Timeline Diagram** - Timeline showing lost update
3. **Peterson's Algorithm State Graph** - Graph proving mutual exclusion
4. **Peterson's Algorithm Timeline Diagram** - Timeline showing blocking
5. **Run C Race Condition Example** - Execute compiled C code showing race
6. **Run C Peterson's Algorithm Example** - Execute C code with mutual exclusion
7. **Generate ALL Visualizations** - Create all 4 graphs at once

## Animations

### Race Condition Animations

**RaceConditionAnimation**: Shows two processes incrementing a shared counter
- Safe execution (sequential) → Correct result: 2
- Race condition (concurrent) → Wrong result: 1 (lost update)

**RaceConditionGraph**: State transition graph
- Orange nodes: Both processes reading (race starting)
- Red nodes: Both writing (lost update occurring)
- Shows problematic execution paths

### Peterson's Algorithm Animations

**PetersonAnimation**: Shows synchronized execution
- Displays flag and turn variables
- Shows one process waiting while other is in critical section
- Always produces correct result

**PetersonGraph**: State transition graph
- Green nodes: Safe critical section access
- Yellow nodes: Contention resolved by algorithm
- **Key**: No state exists where both are in critical section simultaneously

## Deep Dive: Instructions Analysis

### Race Condition in Assembly

From `race_condition.s` (line 94-103):
```asm
increment_counter:
    # C code: long temp = counter;
    movl    counter(%rip), %eax      # Load counter from memory into EAX register
    movl    %eax, -8(%rbp)           # Store in local variable 'temp'
    
    
    # C code: temp = temp + 1;
    addl    $1, -8(%rbp)             # Increment local temp
    
    # C code: counter = temp;
    movl    -8(%rbp), %eax           # Load temp back into register
    movl    %eax, counter(%rip)      # WRITE back to shared memory
    
    # RACE WINDOW: Between the movl instructions above!
    # Another thread can execute the SAME sequence with stale data
```

**The Race Condition Timeline**:
```
Time | Thread 1                    | Thread 2                    | counter value
-----|----------------------------|-----------------------------|--------------
  0  | movl counter, %eax (=0)    |                             | 0
  1  |                            | movl counter, %eax (=0)     | 0
  2  | addl $1, %eax (=1)         |                             | 0
  3  |                            | addl $1, %eax (=1)          | 0
  4  | movl %eax, counter (=1)    |                             | 1
  5  |                            | movl %eax, counter (=1)     | 1 ← WRONG!
```

### Peterson's Algorithm

From `peterson.s` (lines 119-130):
```asm
peterson_process:
    # C code: atomic_store_explicit(&flag[id], true, memory_order_seq_cst);
    leaq    flag(%rip), %rax         # Load address of flag array
    movb    $1, %dl                  # Prepare value 'true' (1)
    xchgb   (%rax), %dl              # ATOMIC EXCHANGE with memory barrier!
                                     # xchg has implicit LOCK prefix
    
    # C code: atomic_store_explicit(&turn, other, memory_order_seq_cst);
    leaq    turn(%rip), %rax         # Load address of turn
    movl    %ebx, %edx               # Prepare 'other' value
    xchgl   (%rax), %edx             # ATOMIC EXCHANGE (32-bit)
    
    # Spin loop: while (flag[other] && turn == other)
.L_spin:
    movzbl  flag+1(%rip), %eax       # Atomic load of flag[other]
    testb   %al, %al                 # Test if true
    je      .L_enter_cs              # If false, enter critical section
    movl    turn(%rip), %eax         # Atomic load of turn
    cmpl    %ebx, %eax               # Compare with 'other'
    je      .L_spin                  # If equal, keep spinning
    
.L_enter_cs:
    # Critical section code here (protected!)
    movl    counter(%rip), %eax
    addl    $1, %eax
    movl    %eax, counter(%rip)
```

**Key Difference**: 
- Race condition uses plain `movl` (not atomic, no barriers)
- Peterson's uses `xchg` (atomic + memory barrier + cache coherency)

### What `xchg` Does (x86-64):

1. **Atomically** exchanges register with memory
2. **Implicit LOCK prefix** → locks memory bus
3. **Memory barrier** → prevents instruction reordering
4. **Cache coherency** → invalidates other cores' caches
5. **Sequential consistency** → all cores see same order of operations

This is why `memory_order_seq_cst` is necessary!

## Graph Theory

The visualizations use **directed graphs** where:
- **Nodes** = System states (P1 state, P2 state, counter value, flags, turn)
- **Edges** = State transitions (process actions)
- **Paths** = Possible execution interleavings

### Race Condition Graph
- Multiple paths lead to same incorrect state (lost update)
- **Red paths** = Problematic interleavings

### Peterson's Graph
- **No paths** lead to mutual exclusion violation
- Proof by exhaustion: all reachable states are safe
- Visual proof of correctness!

### Compile and Run C Code

The C examples auto-compile when you run `main.py`. Or manually:

```bash
cd c_examples

# Compile race condition example
gcc -O0 -g race_condition_example.c -o race_condition.exe -lpthread

# Run it (results vary due to non-determinism!)
./race_condition.exe

# Compile Peterson's algorithm
gcc -O0 -g peterson_algorithm.c -o peterson.exe -lpthread

# Run 
./peterson.exe
```

### View Assembly (Educational)

```bash
# Generate assembly to see atomic operations
gcc -O0 -S race_condition_example.c -o race_condition.s
gcc -O0 -S peterson_algorithm.c -o peterson.s

# View the .s files to see how counter++ becomes multiple instructions
```

## Modern Synchronization: Mutex Solutions

While Peterson's algorithm is an elegant theoretical solution, modern applications use **mutex** (mutual exclusion locks) as the practical, production-grade approach to preventing race conditions.


A mutex is a synchronization primitive that ensures only one thread can access a critical section at a time. Unlike Peterson's algorithm, the mutex implementation is typically handled by the operating system or standard library, abstracting away low-level synchronization logic.

#### C Code w
```c
#include <pthread.h>

pthread_mutex_t counter_mutex = PTHREAD_MUTEX_INITIALIZER;
long counter = 0;

void* mutex_process(void* arg) {
    int id = *((int*)arg);
    
    for (int i = 0; i < ITERATIONS/2; i++) {
        // === LOCK ACQUISITION ===
        pthread_mutex_lock(&counter_mutex);
        
        // === CRITICAL SECTION (PROTECTED) ===
        long temp = counter;
        temp = temp + 1;
        counter = temp;
        // === END CRITICAL SECTION ===
        
        // === LOCK RELEASE ===
        pthread_mutex_unlock(&counter_mutex);
    }
}
```

**Result**:  counter=200000.

#### C Code with C11 Mutex (Optional):
```c
#include <threads.h>

mtx_t counter_mutex;
long counter = 0;

void* c11_mutex_process(void* arg) {
    int id = *((int*)arg);
    
    for (int i = 0; i < ITERATIONS/2; i++) {
        mtx_lock(&counter_mutex);
        
        // Critical section
        long temp = counter;
        temp = temp + 1;
        counter = temp;
        
        mtx_unlock(&counter_mutex);
    }
}
```

### Why Mutex Over Peterson's Algorithm?

| Aspect | Peterson's Algorithm | Mutex |
|--------|---------------------|-------|
| **Ease of Use** | Requires manual synchronization logic | Single `lock()`/`unlock()` calls |
| **Scalability** | Designed for 2 processes only | Works for unlimited threads |
| **Fairness** | May starve threads (priority issues) | OS scheduler ensures fairness |
| **Performance** | Busy-wait (wastes CPU cycles) | OS blocks waiting threads (sleeps) |
| **Debugging** | Complex state to track manually | Clear, straightforward semantics |
| **Modern CPUs** | Requires explicit memory barriers | Handled by mutex implementation |
| **Maintenance** | Error-prone, difficult to verify | Proven, battle-tested code |

### Mutex 

When `pthread_mutex_lock()` is called, it typically translates to:
```asm
# Simplified: actual implementation is complex
mutex_lock:
    mov     $1, %eax                ; Prepare lock value
.L_try_lock:
    cmpxchg %eax, (%rdi)            ; ATOMIC: Compare and exchange
    jne     .L_contended            ; If locked, thread must wait
    ret                              ; Lock acquired!
    
.L_contended:
    # Thread is blocked (sleeps) - OS handles scheduling
    syscall SYS_futex               ; Call kernel for efficient blocking
    jmp     .L_try_lock             ; Retry after woken up
```

**Key advantages**:
- Uses `cmpxchg` (atomic compare-and-swap) for efficient locking
- Threads don't busy-wait; they sleep and are awakened by OS
- Kernel scheduler manages fairness and priority
- No wasted CPU cycles on spinning

///////////////////////////////////////////////////////////////////////////////////////////////////

### Problem Resolution Summary

| Challenge | Peterson's Solution | Mutex Solution |
|-----------|---------------------|----------------|
| **CPU Pipelining** | `memory_order_seq_cst` | Handled by kernel/library |
| **Compiler Optimization** | `_Atomic` qualifier | Mutex code is not optimized away |
| **Store Buffers** | `xchg` with LOCK | OS ensures visibility |
| **Cache Coherency** | Atomic operations | Kernel synchronization |
| **Memory Visibility** | Memory barriers | Implicit in lock/unlock |
| **Instruction Reordering** | Sequential consistency | Serialization via mutex |
| **Scalability** | Only 2 threads | Unlimited threads |
| **CPU Efficiency** | Busy-wait (wasted cycles) | OS blocking (efficient) |

### When to Use Each

**Peterson's Algorithm**:
- Academic learning and theoretical understanding
- Embedded systems with minimal OS
- Educational demonstrations of synchronization principles
- Theoretical proofs of correctness

**Mutex (Production)**:
- Real-world applications
- Multi-threaded servers and services
- Any application with 3+ threads
- When performance and maintainability matter

**C11 Atomics**:
- Lock-free algorithms
- Performance-critical code requiring precise control
- When you understand memory ordering semantics
- Not typically for simple mutual exclusion (use mutex instead)

## Troubleshooting


**Import errors:**
- Make sure to run from the correct directory: `uv run src/main.py`

## References

- Peterson, G. L. (1981). "Myths About the Mutual Exclusion Problem"
- Dijkstra, E. W. (1965). "Solution of a problem in concurrent programming control"
- Lamport, L. (1974). "A New Solution of Dijkstra's Concurrent Programming Problem"
- POSIX Threads (pthreads) Programming: https://computing.llnl.gov/tutorials/pthreads/
