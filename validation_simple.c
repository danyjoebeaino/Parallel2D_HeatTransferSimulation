#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    int nx, ny;
    double alpha, dx, dy, dt;
    double top_temp, bottom_temp;
} SimulationConfig;

int validate_simulation(SimulationConfig config) {
    printf("🔍 Validating Simulation Parameters...\n");
    printf("========================================\n");
    
    int errors = 0;
    int warnings = 0;
    
    // 1. Check stability condition
    double stable_dt = 0.25 * fmin(config.dx * config.dx, config.dy * config.dy) / config.alpha;
    printf("Stability Check:\n");
    printf("  Current dt = %.6f\n", config.dt);
    printf("  Maximum stable dt = %.6f\n", stable_dt);
    
    if (config.dt > stable_dt) {
        printf("  ❌ ERROR: Time step too large! Simulation may be unstable.\n");
        errors++;
    } else {
        printf("  ✅ PASS: Time step is stable.\n");
    }
    
    // 2. Check grid size
    printf("\nGrid Size Check:\n");
    printf("  Grid dimensions: %d x %d\n", config.nx, config.ny);
    
    if (config.nx < 10 || config.ny < 10) {
        printf("  ⚠️  WARNING: Very small grid may give poor results.\n");
        warnings++;
    } else {
        printf("  ✅ PASS: Grid size is reasonable.\n");
    }
    
    // 3. Check memory requirements
    size_t memory_bytes = config.nx * config.ny * sizeof(double) * 2; // T and T_new
    double memory_mb = memory_bytes / (1024.0 * 1024.0);
    printf("\nMemory Check:\n");
    printf("  Estimated memory: %.1f MB\n", memory_mb);
    
    if (memory_mb > 1000) {
        printf("  ⚠️  WARNING: High memory usage (>1GB).\n");
        warnings++;
    } else {
        printf("  ✅ PASS: Memory usage is reasonable.\n");
    }
    
    // 4. Check boundary conditions
    printf("\nBoundary Conditions Check:\n");
    printf("  Top temperature: %.1f°C\n", config.top_temp);
    printf("  Bottom temperature: %.1f°C\n", config.bottom_temp);
    
    if (config.top_temp < -273.15 || config.bottom_temp < -273.15) {
        printf("  ❌ ERROR: Temperature below absolute zero!\n");
        errors++;
    } else {
        printf("  ✅ PASS: Temperatures are physically reasonable.\n");
    }
    
    // Summary
    printf("\n========================================\n");
    printf("Validation Summary:\n");
    printf("  Errors: %d\n", errors);
    printf("  Warnings: %d\n", warnings);
    
    if (errors > 0) {
        printf("❌ VALIDATION FAILED - Please fix errors before running.\n");
        return 0;
    } else if (warnings > 0) {
        printf("⚠️  VALIDATION PASSED with warnings - Simulation should run.\n");
        return 1;
    } else {
        printf("✅ VALIDATION PASSED - All checks passed!\n");
        return 1;
    }
}

int main() {
    // Test with your simulation parameters
    SimulationConfig config = {
        .nx = 100, .ny = 100,
        .alpha = 0.1, .dx = 0.01, .dy = 0.01, .dt = 0.0001,
        .top_temp = 100.0, .bottom_temp = 100.0
    };
    
    return validate_simulation(config) ? 0 : 1;
}
