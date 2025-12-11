#include <mpi.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Default global configuration
#define NX 100
#define NY 100
#define ALPHA 0.1
#define DX 0.01
#define DY 0.01
#define DT 0.0001
#define STEPS 1000
#define OUTPUT_INTERVAL 100
#define RESIDUAL_INTERVAL 100

// Boundary temperatures
#define TOP_TEMP 100.0
#define BOTTOM_TEMP 100.0
#define LEFT_TEMP 0.0
#define RIGHT_TEMP 0.0

typedef struct {
    int nx, ny;
    double alpha, dx, dy, dt;
    int steps;
    int output_interval;
    int residual_interval;
    double top_temp, bottom_temp, left_temp, right_temp;
} SimulationConfig;

static inline int idx(int i, int j, int ny) {
    return i * ny + j;
}

void distribute_rows(int nx, int size, int *counts, int *displs) {
    int base = nx / size;
    int extra = nx % size;
    int offset = 0;
    for (int r = 0; r < size; r++) {
        counts[r] = base + (r < extra ? 1 : 0);
        displs[r] = offset;
        offset += counts[r];
    }
}

void initialize_local(double *T, SimulationConfig config, int local_nx, int start_row) {
    int ny = config.ny;

    // Zero everything (including halos)
    for (int i = 0; i < (local_nx + 2) * ny; i++) {
        T[i] = 0.0;
    }

    for (int i = 1; i <= local_nx; i++) {
        int global_i = start_row + i - 1;
        for (int j = 0; j < ny; j++) {
            double value = 0.0;

            if (global_i == 0) {
                value = config.top_temp;
            } else if (global_i == config.nx - 1) {
                value = config.bottom_temp;
            } else if (j == 0) {
                value = config.left_temp;
            } else if (j == ny - 1) {
                value = config.right_temp;
            }

            T[idx(i, j, ny)] = value;
        }
    }

    // Initialize halo rows for physical boundaries
    if (start_row == 0) {
        for (int j = 0; j < ny; j++) {
            T[idx(0, j, ny)] = config.top_temp;
        }
    }
    if (start_row + local_nx == config.nx) {
        for (int j = 0; j < ny; j++) {
            T[idx(local_nx + 1, j, ny)] = config.bottom_temp;
        }
    }
}

void exchange_halos(double *T, SimulationConfig config, int local_nx, int rank, int size, MPI_Comm comm) {
    int ny = config.ny;

    if (local_nx == 0) {
        // No rows on this rank; keep halos consistent with boundaries if applicable
        if (rank == 0) {
            for (int j = 0; j < ny; j++) {
                T[idx(0, j, ny)] = config.top_temp;
            }
        }
        if (rank == size - 1) {
            for (int j = 0; j < ny; j++) {
                T[idx(1, j, ny)] = config.bottom_temp;
            }
        }
        return;
    }

    int up = rank - 1;
    int down = rank + 1;
    if (up < 0) up = MPI_PROC_NULL;
    if (down >= size) down = MPI_PROC_NULL;

    // Send first real row upward, receive bottom halo from below
    MPI_Sendrecv(
        &T[idx(1, 0, ny)], ny, MPI_DOUBLE, up, 0,
        &T[idx(local_nx + 1, 0, ny)], ny, MPI_DOUBLE, down, 0,
        comm, MPI_STATUS_IGNORE);

    // Send last real row downward, receive top halo from above
    MPI_Sendrecv(
        &T[idx(local_nx, 0, ny)], ny, MPI_DOUBLE, down, 1,
        &T[idx(0, 0, ny)], ny, MPI_DOUBLE, up, 1,
        comm, MPI_STATUS_IGNORE);

    // Enforce physical boundaries at global edges
    if (up == MPI_PROC_NULL) {
        for (int j = 0; j < ny; j++) {
            T[idx(0, j, ny)] = config.top_temp;
        }
    }
    if (down == MPI_PROC_NULL) {
        for (int j = 0; j < ny; j++) {
            T[idx(local_nx + 1, j, ny)] = config.bottom_temp;
        }
    }
}

void update_temperature(double *T, double *T_new, SimulationConfig config, int local_nx, int start_row) {
    int ny = config.ny;
    double dx2 = config.dx * config.dx;
    double dy2 = config.dy * config.dy;
    double factor = config.alpha * config.dt;

    for (int i = 1; i <= local_nx; i++) {
        int global_i = start_row + i - 1;

        // Keep physical boundary rows fixed
        if (global_i == 0) {
            for (int j = 0; j < ny; j++) {
                T_new[idx(i, j, ny)] = config.top_temp;
            }
            continue;
        } else if (global_i == config.nx - 1) {
            for (int j = 0; j < ny; j++) {
                T_new[idx(i, j, ny)] = config.bottom_temp;
            }
            continue;
        }

        // Left/right boundaries fixed for all interior rows
        T_new[idx(i, 0, ny)] = config.left_temp;
        T_new[idx(i, ny - 1, ny)] = config.right_temp;

        for (int j = 1; j < ny - 1; j++) {
            double d2T_dx2 = (T[idx(i + 1, j, ny)] - 2.0 * T[idx(i, j, ny)] + T[idx(i - 1, j, ny)]) / dx2;
            double d2T_dy2 = (T[idx(i, j + 1, ny)] - 2.0 * T[idx(i, j, ny)] + T[idx(i, j - 1, ny)]) / dy2;
            T_new[idx(i, j, ny)] = T[idx(i, j, ny)] + factor * (d2T_dx2 + d2T_dy2);
        }
    }
}

double compute_local_residual(double *T, SimulationConfig config, int local_nx, int start_row) {
    int ny = config.ny;
    double dx2 = config.dx * config.dx;
    double dy2 = config.dy * config.dy;
    double max_res = 0.0;

    for (int i = 1; i <= local_nx; i++) {
        int global_i = start_row + i - 1;
        if (global_i == 0 || global_i == config.nx - 1) {
            continue;
        }
        for (int j = 1; j < ny - 1; j++) {
            double laplacian = (T[idx(i + 1, j, ny)] - 2.0 * T[idx(i, j, ny)] + T[idx(i - 1, j, ny)]) / dx2 +
                                (T[idx(i, j + 1, ny)] - 2.0 * T[idx(i, j, ny)] + T[idx(i, j - 1, ny)]) / dy2;
            double res = fabs(laplacian);
            if (res > max_res) {
                max_res = res;
            }
        }
    }
    return max_res;
}

void write_snapshot(const double *global_T, SimulationConfig config, const char *filename) {
    FILE *fp = fopen(filename, "w");
    if (!fp) {
        fprintf(stderr, "[root] ERROR: Unable to open %s for writing\n", filename);
        return;
    }

    for (int i = 0; i < config.nx; i++) {
        for (int j = 0; j < config.ny; j++) {
            fprintf(fp, "%.6f ", global_T[idx(i, j, config.ny)]);
        }
        fprintf(fp, "\n");
    }
    fclose(fp);
    printf("[root] Saved %s\n", filename);
}

void gather_and_write(double *T, SimulationConfig config, int local_nx, int rank,
                      const int *recvcounts, const int *displs_elems,
                      double *global_buffer, const char *filename) {
    // Pointer to first owned row (skip top halo)
    double *sendbuf = &T[idx(1, 0, config.ny)];
    int sendcount = local_nx * config.ny;

    MPI_Gatherv(sendbuf, sendcount, MPI_DOUBLE,
                global_buffer, recvcounts, displs_elems, MPI_DOUBLE,
                0, MPI_COMM_WORLD);

    if (rank == 0) {
        write_snapshot(global_buffer, config, filename);
    }
}

void print_header(SimulationConfig config, int rank, int size) {
    if (rank != 0) return;
    printf("==============================================\n");
    printf("   MPI 2D Heat Equation Simulation\n");
    printf("==============================================\n");
    printf("Grid: %d x %d\n", config.nx, config.ny);
    printf("Steps: %d (output every %d)\n", config.steps, config.output_interval);
    printf("Diffusivity (alpha): %.3f\n", config.alpha);
    printf("dt = %.6f, dx = %.3f, dy = %.3f\n", config.dt, config.dx, config.dy);
    printf("Boundary temps: top=%.1f, bottom=%.1f, left=%.1f, right=%.1f\n",
           config.top_temp, config.bottom_temp, config.left_temp, config.right_temp);
    printf("MPI tasks: %d\n", size);
    printf("==============================================\n\n");
}

void validate_parameters(SimulationConfig config, int rank) {
    double stable_dt = 0.25 * fmin(config.dx * config.dx, config.dy * config.dy) / config.alpha;
    if (rank == 0) {
        if (config.dt > stable_dt) {
            printf("[root] WARNING: dt=%.6f exceeds stable dt=%.6f\n", config.dt, stable_dt);
            printf("        Reduce dt or increase dx/dy for stability.\n");
        } else {
            printf("[root] Stability check OK (dt=%.6f <= %.6f)\n\n", config.dt, stable_dt);
        }
    }
}

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    SimulationConfig config = {
        .nx = NX, .ny = NY,
        .alpha = ALPHA, .dx = DX, .dy = DY, .dt = DT,
        .steps = STEPS,
        .output_interval = OUTPUT_INTERVAL,
        .residual_interval = RESIDUAL_INTERVAL,
        .top_temp = TOP_TEMP, .bottom_temp = BOTTOM_TEMP,
        .left_temp = LEFT_TEMP, .right_temp = RIGHT_TEMP
    };

    print_header(config, rank, size);
    validate_parameters(config, rank);

    int *counts = (int *)malloc(size * sizeof(int));
    int *displs = (int *)malloc(size * sizeof(int));
    distribute_rows(config.nx, size, counts, displs);

    int local_nx = counts[rank];
    int start_row = displs[rank];

    // Prepare Gatherv metadata (elements, not rows)
    int *recvcounts = (int *)malloc(size * sizeof(int));
    int *displs_elems = (int *)malloc(size * sizeof(int));
    for (int r = 0; r < size; r++) {
        recvcounts[r] = counts[r] * config.ny;
        displs_elems[r] = displs[r] * config.ny;
    }

    double *global_buffer = NULL;
    if (rank == 0) {
        global_buffer = (double *)malloc((size_t)config.nx * config.ny * sizeof(double));
        if (!global_buffer) {
            fprintf(stderr, "[root] ERROR: failed to allocate global buffer\n");
            MPI_Abort(MPI_COMM_WORLD, 1);
        }
    }

    double *T = (double *)calloc((size_t)(local_nx + 2) * config.ny, sizeof(double));
    double *T_new = (double *)calloc((size_t)(local_nx + 2) * config.ny, sizeof(double));
    if (!T || !T_new) {
        fprintf(stderr, "[rank %d] ERROR: allocation failed\n", rank);
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    initialize_local(T, config, local_nx, start_row);

    // Write initial state
    gather_and_write(T, config, local_nx, rank, recvcounts, displs_elems, global_buffer, "output_step_0000.txt");

    MPI_Barrier(MPI_COMM_WORLD);
    double t0 = MPI_Wtime();
    double residual = 0.0;

    for (int step = 0; step < config.steps; step++) {
        exchange_halos(T, config, local_nx, rank, size, MPI_COMM_WORLD);
        update_temperature(T, T_new, config, local_nx, start_row);

        double *tmp = T;
        T = T_new;
        T_new = tmp;

        if ((step + 1) % config.residual_interval == 0) {
            double local_res = compute_local_residual(T, config, local_nx, start_row);
            MPI_Allreduce(&local_res, &residual, 1, MPI_DOUBLE, MPI_MAX, MPI_COMM_WORLD);
        }

        if ((step + 1) % config.output_interval == 0) {
            char fname[64];
            snprintf(fname, sizeof(fname), "output_step_%04d.txt", step + 1);
            gather_and_write(T, config, local_nx, rank, recvcounts, displs_elems, global_buffer, fname);
            if (rank == 0) {
                printf("[root] Completed step %d / %d | residual %.2e\n", step + 1, config.steps, residual);
            }
        }
    }

    double local_elapsed = MPI_Wtime() - t0;
    double max_elapsed = 0.0;
    MPI_Reduce(&local_elapsed, &max_elapsed, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

    // Final output
    gather_and_write(T, config, local_nx, rank, recvcounts, displs_elems, global_buffer, "output_final.txt");

    if (rank == 0) {
        printf("\nSimulation complete.\n");
        printf("Elapsed (max across ranks): %.3f s\n", max_elapsed);
        printf("Throughput: %.2f steps/s\n", config.steps / max_elapsed);
        printf("Snapshots: output_step_*.txt + output_final.txt\n");
    }

    free(T);
    free(T_new);
    free(counts);
    free(displs);
    free(recvcounts);
    free(displs_elems);
    if (rank == 0) {
        free(global_buffer);
    }

    MPI_Finalize();
    return 0;
}
