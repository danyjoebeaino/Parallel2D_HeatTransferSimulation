Heat Transfer Simulation Suite
==============================

Three related projects live here so you can compare single-node, multi-node MPI, and an AWS-focused experiment set with scaling plots and visualizations.

## Layout
- `Parallel2D_HeatTransferSimulation_local/` — original single-machine code (serial + advanced solvers, validation, visualization).
- `Parallel2D_HeatTransferSimulation_mpi/` — MPI row-decomposed solver meant for 4 Ubuntu nodes (master + 3 workers), with reusable visualization.
- `Parallel2D_HeatTransferSimulation_AWS/` — artifacts and Python scripts from 4-node AWS runs (per-rank CSVs, stitching/animation, scaling plots).

## Quick starts
- Local (single machine):  
  ```bash
  cd Parallel2D_HeatTransferSimulation_local
  make all
  make run-advanced
  make visualize
  ```

- MPI (4 nodes or 4 ranks locally):  
  ```bash
  cd Parallel2D_HeatTransferSimulation_mpi
  make
  mpirun -np 4 --hostfile hosts ./heat_mpi   # hostfile only needed across nodes
  make visualize
  ```

- AWS experiment assets:  
  ```bash
  cd Parallel2D_HeatTransferSimulation_AWS
  python -m venv .venv && source .venv/bin/activate
  pip install numpy matplotlib
  python heat_pro_visualization.py   # stitch/animate rank CSVs
  python plot_scaling.py             # regenerate speedup/efficiency plots
  ```

## What to compare
- **Field correctness:** diff `output_step_*.txt` / `output_final.txt` from local vs MPI runs; visualize with the shared Python scripts.
- **Performance:** use the MPI runtime printouts (steps/s) and the AWS `plot_scaling.py` charts to discuss speedup/efficiency and communication overheads.
- **Decompositions:** local solver uses a monolithic grid; MPI splits rows; AWS scripts include 1D vs 2D block comparisons on real cluster runs.

Each subfolder has its own README with details. Keep outputs separate by running commands from inside each folder. MPI runs expect passwordless SSH and identical paths on all nodes when using a hostfile.
