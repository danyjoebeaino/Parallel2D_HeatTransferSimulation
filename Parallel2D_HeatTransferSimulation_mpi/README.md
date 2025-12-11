MPI 2D Heat Transfer Simulation
===============================

A distributed-memory version of the 2D heat equation solver using MPI. The grid is split by rows across ranks, with halo exchanges each timestep and snapshots gathered on rank 0 for visualization.

## Requirements
- OpenMPI (or MPICH) with `mpicc` and `mpirun`
- `gcc` toolchain
- Python 3 with `numpy`, `matplotlib`, `scipy`, `pillow` (for visualization)
  - Install the Python bits: `make install-deps`

## Build
```bash
make            # builds heat_mpi using mpicc
```

## Run (single machine, 4 ranks)
```bash
make run        # mpirun -np 4 ./heat_mpi
```

## Run across 4 Ubuntu nodes
1) Ensure all 4 nodes can see the same project path (shared FS) or copy the built binary to each node.
2) Create a hostfile named `hosts` in this folder, e.g.:
   ```
   node1 slots=1
   node2 slots=1
   node3 slots=1
   node4 slots=1
   ```
3) Launch from any node with MPI access:
   ```bash
   make run-hosts   # uses mpirun -np 4 --hostfile hosts ./heat_mpi
   ```
   Adjust hostnames/slots as needed; ensure passwordless SSH for the MPI user.

## Outputs
- Snapshots: `output_step_*.txt`
- Final state: `output_final.txt`
- Only rank 0 writes files; keep a shared directory so all nodes can access results.

## Visualize (after a run)
```bash
make visualize           # heatmaps + animation (heat_simulation.gif)
make visualize-advanced  # comparison grid, 3D surface, convergence, flux, GIF
```

## Notes
- Default grid: 100x100, dt=1e-4, steps=1000, output every 100 steps. Tune in `heat_mpi.c` near the top.
- Stability check will warn if dt exceeds the CFL limit.
- Cleanup: `make clean` (binary) or `make clean-all` (binary + outputs/plots/GIFs).
