#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

#define ITERATIONS 100000


long counter = 0;

void* increment_counter(void* arg) {
    for (int i = 0; i < ITERATIONS/2; i++) {
        // === CRITICAL SECTION (UNPROTECTED) ===
        // The following three operations are NOT atomic together:
        
        // 1. READ: Load counter value from memory
        long temp = counter;

        // Simulate a context switch to increase chance of race
        usleep(1);
        
        // 2. MODIFY: Increment the value
        temp = temp + 1;
        
        // 3. WRITE: Store back to memory
        counter = temp;
        
    }
    return NULL;
}

int main() {
    pthread_t t1, t2;
    
    printf("=== Race Condition Demonstration ===\n");
    printf("Expected final value: %d\n", ITERATIONS);
    printf("Starting threads without synchronization...\n\n");
    
    
    pthread_create(&t1, NULL, increment_counter, NULL);
    pthread_create(&t2, NULL, increment_counter, NULL);
    
    
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    
    
    printf("Actual final value: %ld\n", counter);
    
    if (counter < ITERATIONS) {
        printf(" RACE CONDITION DETECTED! Lost %ld updates\n", ITERATIONS - counter);
        printf("Reason: Both threads read same value before either writes\n");
    } else {
        printf("No race detected this run (non-deterministic - try again)\n");
    }
    
    return 0;
}