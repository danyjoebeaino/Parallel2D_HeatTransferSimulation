#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <unistd.h>

// Configuration structure
typedef struct {
    int nx, ny;
    double alpha, dx, dy, dt;
    int steps;
    double top_temp, bottom_temp, left_temp, right_temp;
    int output_interval;
    int progress_bar_width;
} SimulationConfig;

// Function declarations
double get_current_time();
void print_progress_bar(int iteration, int total, double start_time, int bar_width);
void print_simulation_header(SimulationConfig config);
void initialize(double **T, SimulationConfig config);
void update_temperature(double **T, double **T_new, SimulationConfig config);
double calculate_residual(double **T, SimulationConfig config);
void save_to_file(double **T, SimulationConfig config, const char* filename);
double **allocate_2d_array(int nx, int ny);
void free_2d_array(double **array, int nx);
void validate_simulation(SimulationConfig config);

// High-resolution timer
double get_current_time() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec + tv.tv_usec * 1e-6;
}

// Progress bar display
void print_progress_bar(int iteration, int total, double start_time, int bar_width) {
    double progress = (double)iteration / total;
    int pos = (int)(bar_width * progress);
    
    double elapsed = get_current_time() - start_time;
    double eta = (elapsed / (iteration + 1)) * (total - iteration - 1);
    
    printf("\r[");
    for (int i = 0; i < bar_width; ++i) {
        if (i < pos) printf("=");
        else if (i == pos) printf(">");
        else printf(" ");
    }
    printf("] %d/%d (%.1f%%) | Elapsed: %.1fs | ETA: %.1fs", 
           iteration + 1, total, progress * 100.0, elapsed, eta);
    fflush(stdout);
}

// Print simulation information
void print_simulation_header(SimulationConfig config) {
    printf("╔══════════════════════════════════════════════════════════════╗\n");
    printf("║                 2D HEAT EQUATION SIMULATION                  ║\n");
    printf("╠══════════════════════════════════════════════════════════════╣\n");
    printf("║ Grid Size: %dx%d                                            ║\n", config.nx, config.ny);
    printf("║ Time Steps: %-8d                                  ║\n", config.steps);
    printf("║ Thermal Diffusivity (α): %-8.3f                     ║\n", config.alpha);
    printf("║ Time Step (Δt): %-12.6f                      ║\n", config.dt);
    printf("║ Spatial Steps (Δx, Δy): (%-6.3f, %-6.3f)               ║\n", config.dx, config.dy);
    printf("╠══════════════════════════════════════════════════════════════╣\n");
    printf("║ Boundary Conditions:                                        ║\n");
    printf("║   Top: %6.1f°C   Bottom: %6.1f°C                      ║\n", 
           config.top_temp, config.bottom_temp);
    printf("║   Left: %6.1f°C   Right: %6.1f°C                       ║\n", 
           config.left_temp, config.right_temp);
    printf("╚══════════════════════════════════════════════════════════════╝\n");
    printf("\n");
}

// Memory allocation with error checking
double **allocate_2d_array(int nx, int ny) {
    double **array = (double **)malloc(nx * sizeof(double *));
    if (array == NULL) {
        fprintf(stderr, "ERROR: Memory allocation failed for rows\n");
        exit(EXIT_FAILURE);
    }
    
    for (int i = 0; i < nx; i++) {
        array[i] = (double *)malloc(ny * sizeof(double));
        if (array[i] == NULL) {
            fprintf(stderr, "ERROR: Memory allocation failed for columns\n");
            exit(EXIT_FAILURE);
        }
    }
    return array;
}

void free_2d_array(double **array, int nx) {
    for (int i = 0; i < nx; i++) {
        free(array[i]);
    }
    free(array);
}

// Validation function
void validate_simulation(SimulationConfig config) {
    printf("Validating simulation parameters...\n");
    
    // Check stability condition (CFL condition for 2D heat equation)
    double stable_dt = 0.25 * fmin(config.dx * config.dx, config.dy * config.dy) / config.alpha;
    
    if (config.dt > stable_dt) {
        printf("⚠️  WARNING: Time step may be unstable!\n");
        printf("   Current Δt = %.6f\n", config.dt);
        printf("   Maximum stable Δt = %.6f\n", stable_dt);
        printf("   Consider reducing Δt for stability\n\n");
    } else {
        printf("✓ Time step stability: OK (Δt = %.6f <= %.6f)\n", config.dt, stable_dt);
    }
    
    // Check grid size
    if (config.nx < 10 || config.ny < 10) {
        printf("⚠️  WARNING: Grid size is very small (%dx%d)\n", config.nx, config.ny);
        printf("   Consider increasing grid size for better accuracy\n\n");
    } else {
        printf("✓ Grid size: OK (%dx%d)\n", config.nx, config.ny);
    }
    
    // Check memory requirements
    size_t memory_mb = config.nx * config.ny * sizeof(double) / (1024 * 1024);
    printf("✓ Estimated memory: %zu MB\n\n", memory_mb);
}

// Initialize temperature field
void initialize(double **T, SimulationConfig config) {
    for (int i = 0; i < config.nx; i++) {
        for (int j = 0; j < config.ny; j++) {
            T[i][j] = 0.0;
        }
    }
    
    // Set boundary conditions
    for (int j = 0; j < config.ny; j++) {
        T[0][j] = config.top_temp;
        T[config.nx-1][j] = config.bottom_temp;
    }
    for (int i = 0; i < config.nx; i++) {
        T[i][0] = config.left_temp;
        T[i][config.ny-1] = config.right_temp;
    }
}

// Update temperature using finite differences
void update_temperature(double **T, double **T_new, SimulationConfig config) {
    double dx2 = config.dx * config.dx;
    double dy2 = config.dy * config.dy;
    double factor = config.alpha * config.dt;
    
    for (int i = 1; i < config.nx-1; i++) {
        for (int j = 1; j < config.ny-1; j++) {
            double d2T_dx2 = (T[i+1][j] - 2*T[i][j] + T[i-1][j]) / dx2;
            double d2T_dy2 = (T[i][j+1] - 2*T[i][j] + T[i][j-1]) / dy2;
            
            T_new[i][j] = T[i][j] + factor * (d2T_dx2 + d2T_dy2);
        }
    }
    
    // Apply boundary conditions (keep constant)
    for (int j = 0; j < config.ny; j++) {
        T_new[0][j] = config.top_temp;
        T_new[config.nx-1][j] = config.bottom_temp;
    }
    for (int i = 0; i < config.nx; i++) {
        T_new[i][0] = config.left_temp;
        T_new[i][config.ny-1] = config.right_temp;
    }
}

// Calculate residual for convergence monitoring
double calculate_residual(double **T, SimulationConfig config) {
    double max_residual = 0.0;
    double dx2 = config.dx * config.dx;
    double dy2 = config.dy * config.dy;
    
    for (int i = 1; i < config.nx-1; i++) {
        for (int j = 1; j < config.ny-1; j++) {
            double laplacian = (T[i+1][j] - 2*T[i][j] + T[i-1][j]) / dx2 +
                             (T[i][j+1] - 2*T[i][j] + T[i][j-1]) / dy2;
            double residual = fabs(laplacian);
            if (residual > max_residual) {
                max_residual = residual;
            }
        }
    }
    return max_residual;
}

// Save temperature field to file
void save_to_file(double **T, SimulationConfig config, const char* filename) {
    FILE *fp = fopen(filename, "w");
    if (fp == NULL) {
        fprintf(stderr, "ERROR: Cannot open file %s for writing\n", filename);
        return;
    }
    
    for (int i = 0; i < config.nx; i++) {
        for (int j = 0; j < config.ny; j++) {
            fprintf(fp, "%.6f ", T[i][j]);
        }
        fprintf(fp, "\n");
    }
    fclose(fp);
}

int main() {
    // Simulation configuration
    SimulationConfig config = {
        .nx = 100, .ny = 100,
        .alpha = 0.1, .dx = 0.01, .dy = 0.01, .dt = 0.0001,
        .steps = 1000,
        .top_temp = 100.0, .bottom_temp = 100.0,
        .left_temp = 0.0, .right_temp = 0.0,
        .output_interval = 100,
        .progress_bar_width = 40
    };
    
    // Start timing
    double start_time = get_current_time();
    
    // Print simulation header
    print_simulation_header(config);
    
    // Validate simulation parameters
    validate_simulation(config);
    
    // Allocate memory
    printf("Allocating memory...\n");
    double **T = allocate_2d_array(config.nx, config.ny);
    double **T_new = allocate_2d_array(config.nx, config.ny);
    
    // Initialize temperature field
    printf("Initializing temperature field...\n");
    initialize(T, config);
    save_to_file(T, config, "output_step_0000.txt");
    printf("✓ Initial state saved to output_step_0000.txt\n\n");
    
    printf("Starting simulation...\n");
    printf("Press Ctrl+C to interrupt early\n\n");
    
    double residual = 0.0;
    
    // Main simulation loop
    for (int step = 0; step < config.steps; step++) {
        // Update temperature
        update_temperature(T, T_new, config);
        
        // Swap pointers for next iteration
        double **temp = T;
        T = T_new;
        T_new = temp;
        
        // Calculate residual every 100 steps
        if ((step + 1) % 100 == 0) {
            residual = calculate_residual(T, config);
        }
        
        // Save output and show progress
        if ((step + 1) % config.output_interval == 0) {
            char filename[50];
            snprintf(filename, sizeof(filename), "output_step_%04d.txt", step + 1);
            save_to_file(T, config, filename);
            
            // Show progress with additional info
            printf("\r");
            print_progress_bar(step + 1, config.steps, start_time, config.progress_bar_width);
            printf(" | Residual: %.2e", residual);
            fflush(stdout);
        }
    }
    
    // Save final state
    save_to_file(T, config, "output_final.txt");
    
    // Calculate total time
    double total_time = get_current_time() - start_time;
    
    // Print completion message
    printf("\n\n");
    printf("╔══════════════════════════════════════════════════════════════╗\n");
    printf("║                     SIMULATION COMPLETE                      ║\n");
    printf("╠══════════════════════════════════════════════════════════════╣\n");
    printf("║ Total time: %8.2f seconds                             ║\n", total_time);
    printf("║ Performance: %8.2f steps/second                      ║\n", config.steps / total_time);
    printf("║ Final residual: %.2e                            ║\n", residual);
    printf("║ Output files: %d temperature snapshots              ║\n", config.steps / config.output_interval + 2);
    printf("╚══════════════════════════════════════════════════════════════╝\n");
    printf("\n");
    
    // Free memory
    free_2d_array(T, config.nx);
    free_2d_array(T_new, config.nx);
    
    printf("✓ Memory freed successfully\n");
    printf("✓ Simulation completed successfully!\n");
    
    return 0;
}
