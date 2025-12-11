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
#define STEPS 1000
#define OUTPUT_INTERVAL 100

void initialize(double T[NX][NY]) {
    // Initialize with zero temperature everywhere
    for (int i = 0; i < NX; i++) {
        for (int j = 0; j < NY; j++) {
            T[i][j] = 0.0;
        }
    }
    
    // Set boundary conditions: heat from top and bottom
    for (int j = 0; j < NY; j++) {
        T[0][j] = 100.0;      // Top boundary (hot)
        T[NX-1][j] = 100.0;   // Bottom boundary (hot)
        T[j][0] = 0.0;        // Left boundary (cold)
        T[j][NY-1] = 0.0;     // Right boundary (cold)
    }
}

void update_temperature(double T[NX][NY], double T_new[NX][NY]) {
    double dx2 = DX * DX;
    double dy2 = DY * DY;
    
    // Update interior points
    for (int i = 1; i < NX-1; i++) {
        for (int j = 1; j < NY-1; j++) {
            double d2T_dx2 = (T[i+1][j] - 2*T[i][j] + T[i-1][j]) / dx2;
            double d2T_dy2 = (T[i][j+1] - 2*T[i][j] + T[i][j-1]) / dy2;
            
            T_new[i][j] = T[i][j] + ALPHA * DT * (d2T_dx2 + d2T_dy2);
        }
    }
    
    // Apply boundary conditions (keep constant)
    for (int j = 0; j < NY; j++) {
        T_new[0][j] = 100.0;      // Top
        T_new[NX-1][j] = 100.0;   // Bottom
    }
    for (int i = 0; i < NX; i++) {
        T_new[i][0] = 0.0;        // Left
        T_new[i][NY-1] = 0.0;     // Right
    }
}

void save_to_file(double T[NX][NY], const char* filename) {
    FILE *fp = fopen(filename, "w");
    for (int i = 0; i < NX; i++) {
        for (int j = 0; j < NY; j++) {
            fprintf(fp, "%.6f ", T[i][j]);
        }
        fprintf(fp, "\n");
    }
    fclose(fp);
    printf("Saved data to %s\n", filename);
}

int main() {
    double T[NX][NY], T_new[NX][NY];
    
    printf("Initializing 2D Heat Simulation...\n");
    printf("Grid size: %dx%d\n", NX, NY);
    printf("Time steps: %d\n", STEPS);
    printf("Boundary conditions: Top=100°C, Bottom=100°C, Sides=0°C\n");
    
    initialize(T);
    save_to_file(T, "output_step_0000.txt");
    
    for (int step = 0; step < STEPS; step++) {
        update_temperature(T, T_new);
        
        // Copy T_new to T for next iteration
        memcpy(T, T_new, NX * NY * sizeof(double));
        
        if ((step + 1) % OUTPUT_INTERVAL == 0) {
            char filename[50];
            snprintf(filename, sizeof(filename), "output_step_%04d.txt", step + 1);
            save_to_file(T, filename);
            printf("Completed step %d\n", step + 1);
        }
    }
    
    save_to_file(T, "output_final.txt");
    printf("Simulation completed successfully!\n");
    
    return 0;
}
