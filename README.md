Heat Transfer Simulation: Local vs MPI
=====================================

This repo now has two parallel 2D heat equation projects side by side so you can compare single-node (local) runs with a distributed MPI version.

## Layout
- `Parallel2D_HeatTransferSimulation_local/` — original single-machine code (serial/advanced solver, validation, visualizations).
- `Parallel2D_HeatTransferSimulation_mpi/` — MPI row-decomposed solver for multi-node runs.

## Typical comparison workflow
1) Local run (in `Parallel2D_HeatTransferSimulation_local`):
   ```bash
   make all
   make run-advanced      # writes output_step_*.txt + output_final.txt
   make visualize         # generates heatmaps + heat_simulation.gif
   ```
2) MPI run (in `Parallel2D_HeatTransferSimulation_mpi`):
   ```bash
   make
   mpirun -np 4 --hostfile hosts ./heat_mpi   # adjust hostfile for your nodes
   make visualize                             # reuse the same visualization scripts
   ```
3) Compare:
   - Field snapshots: diff `output_step_XXXX.txt` and `output_final.txt` between runs.
   - Visuals: compare GIFs/PNGs (same filenames across folders).
   - Performance: note total runtime reported by each solver and steps/s.

## Notes
- Each folder has its own README with detailed build/run steps.
- Keep outputs separated by running visualizations from within each folder.
- MPI run expects passwordless SSH and a consistent path to the project on all nodes.
