#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#define NX 100
#define NY 100
#define ALPHA 0.1
#define DX 0.01
#define DY 0.01
#define DT 0.0001

// Add this function to your existing heat_serial.c
int validate_parameters() {
    printf("🔍 Validating simulation parameters...\n");
    
    // Check stability
    double stable_dt = 0.25 * fmin(DX * DX, DY * DY) / ALPHA;
    if (DT > stable_dt) {
        printf("❌ ERROR: Time step dt=%.6f is too large!\n", DT);
        printf("   Maximum stable dt=%.6f\n", stable_dt);
        printf("   Reduce DT or increase DX/DY for stability.\n");
        return 0;
    }
    
    // Check grid size
    if (NX < 10 || NY < 10) {
        printf("❌ ERROR: Grid too small (%dx%d). Minimum 10x10 required.\n", NX, NY);
        return 0;
    }
    
    // Check memory
    size_t memory_mb = NX * NY * sizeof(double) * 2 / (1024 * 1024);
    if (memory_mb > 1000) {
        printf("⚠️  WARNING: High memory usage (%.1f MB)\n", memory_mb);
    }
    
    printf("✅ Validation passed - simulation can proceed.\n\n");
    return 1;
}

// Your existing initialize function
void initialize(double T[NX][NY]) {
    for (int i = 0; i < NX; i++) {
        for (int j = 0; j < NY; j++) {
            T[i][j] = 0.0;
        }
    }
    for (int j = 0; j < NY; j++) {
        T[0][j] = 100.0;
        T[NX-1][j] = 100.0;
    }
}

// Your existing update_temperature function
void update_temperature(double T[NX][NY], double T_new[NX][NY]) {
    // ... your existing code
}

int main() {
    // Validate before running
    if (!validate_parameters()) {
        printf("Simulation aborted due to validation errors.\n");
        return 1;
    }
    
    // Your existing simulation code
    double T[NX][NY], T_new[NX][NY];
    initialize(T);
    
    for (int step = 0; step < 1000; step++) {
        update_temperature(T, T_new);
        // ... rest of your code
    }
    
    return 0;
}
