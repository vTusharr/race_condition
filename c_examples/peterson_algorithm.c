#include <stdio.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdatomic.h>

#define ITERATIONS 100000

// Peterson's Algorithm variables
// Using atomic for memory ordering guarantees (Peterson's predates C11 atomics,
// but volatile alone is insufficient on modern CPUs due to reordering)
_Atomic bool flag[2] = {false, false};  // Interest flags
_Atomic int turn = 0;                   // Whose turn it is
long counter = 0;                        // Shared counter


void* peterson_process(void* arg) {
    int id = *((int*)arg);
    int other = 1 - id;
    
    for (int i = 0; i < ITERATIONS/2; i++) {
        // === ENTRY SECTION ===
        atomic_store_explicit(&flag[id], true, memory_order_seq_cst);
        atomic_store_explicit(&turn, other, memory_order_seq_cst);
        
        
        while (atomic_load_explicit(&flag[other], memory_order_seq_cst) && 
               atomic_load_explicit(&turn, memory_order_seq_cst) == other) {
            
        }
        
    
        long temp = counter;
        temp = temp + 1;
        counter = temp;
    
        

        atomic_store_explicit(&flag[id], false, memory_order_seq_cst);
        
    

    }
    return NULL;
}

int main() {
    pthread_t t1, t2;
    int id0 = 0, id1 = 1;
    
    printf("=== Peterson's Algorithm Demonstration ===\n");
    printf("Expected final value: %d\n", ITERATIONS);
    printf("Starting threads with Peterson's mutual exclusion...\n\n");

    pthread_create(&t1, NULL, peterson_process, &id0);
    pthread_create(&t2, NULL, peterson_process, &id1);
    
    
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    
    
    printf("Actual final value: %ld\n", counter);
    
    if (counter == ITERATIONS) {
        printf("MUTUAL EXCLUSION GUARANTEED - No lost updates\n");
        printf("Peterson's algorithm prevents race conditions\n");
    } else {
        printf("Unexpected result: %ld\n", counter);
    }
    
    return 0;
}