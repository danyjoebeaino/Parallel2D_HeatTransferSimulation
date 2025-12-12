# Parallel Heat Diffusion (MPI + Python)

## Overview
Heat diffusion solver/visualizations for a 2D plate. The solver was run on four AWS instances (one MPI rank per instance) using SSH access via `cluster-key.pem`, producing per-rank CSV dumps that are stitched together for plotting and animation. The repo focuses on comparing 1D vs 2D domain decomposition, visualizing the temperature field, and looking at the scaling behavior.

## Quick MPI + EC2 setup (4 nodes)
1) Launch four Ubuntu EC2 instances in the same VPC; allow SSH (port 22) between them and from your IP. Keep the private DNS/IPs handy for the hostfile.
2) Place `cluster-key.pem` in this repo, set permissions, and load it so `mpirun` can hop between nodes:
   ```bash
   chmod 600 cluster-key.pem
   eval "$(ssh-agent)" && ssh-add cluster-key.pem
   # sanity check (repeat for each node)
   ssh -i cluster-key.pem ubuntu@<public-dns-or-ip>
   ```
3) Install MPI and Python deps on every node:
   ```bash
   sudo apt-get update
   sudo apt-get install -y openmpi-bin libopenmpi-dev python3-pip
   pip install numpy matplotlib
   ```
4) Sync the solver code to each node (git clone or `scp -i cluster-key.pem -r ./ <node>:/home/ubuntu/ParallelProject`).
5) On the root node, create a `hosts` file listing the private DNS/IPs (one per line) and point `mpirun` at it:
   ```bash
   cat > hosts <<'EOF'
   ip-10-0-0-1
   ip-10-0-0-2
   ip-10-0-0-3
   ip-10-0-0-4
   EOF
   mpirun -np 4 -hostfile hosts ./heat_solver --nx 200 --ny 200 --steps 500
   ```
   The `-hostfile` uses the private network so ranks talk over the VPC; `ssh-agent` with `cluster-key.pem` handles hop-by-hop auth.

## Repo layout
- `animate_heat.py` – standalone NumPy animation of a 200x200 grid with hot top/bottom plates.
- `heat_pro_visualization.py`, `visualize_ranks_overlay.py` – rebuild 2D MPI outputs, diffuse with custom boundary rules, and animate (2D heatmap + 3D surface).
- `visualize_1d.py`, `visualize2.py` – stitch rank CSVs (1D and 2D decompositions) into a global grid heatmap.
- `plot_heat.py` – applies top/bottom hot bands and diffuses to a final heatmap.
- `fix_csv.py` – trims any extra column in raw MPI CSVs and writes `_fixed` copies.
- `plot_scaling.py` – plots speedup/efficiency for 1D vs 2D decomposition using measured runtimes.
- `output*_rank_*.csv`, `*_fixed.csv` – raw and cleaned MPI outputs; `*.png` – generated plots.

## Quick start (local)
```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy matplotlib

# Animate a local run (no MPI needed)
python animate_heat.py

# Rebuild 2D MPI outputs and animate in 2D/3D
python heat_pro_visualization.py          # uses output_rank_*.csv
python visualize_ranks_overlay.py

# Rebuild 1D decomposition output
python visualize_1d.py                    # uses output1d_rank_*.csv

# Fix raw CSVs (drops stray 101st column if present)
python fix_csv.py

# Plot scaling curves
python plot_scaling.py                    # writes speedup_1d_vs_2d.png and efficiency_1d_vs_2d.png
```

## Distributed run notes (AWS + MPI)
- Four EC2 instances were used; each ran one MPI rank. Access was via `ssh -i cluster-key.pem ubuntu@<host>`.
- Typical prep: `chmod 600 cluster-key.pem`, then copy the solver to each node or mount a shared FS.
- Example launch (replace hosts with your public/private DNS names):
  ```bash
  mpirun -np 4 -hostfile hosts ./heat_solver --nx 200 --ny 200 --steps 500
  ```
  This produces rank-local CSVs (e.g., `output_rank_0.csv` or `output1d_rank_0.csv`). Pull them back with `scp` and use the Python scripts above to visualize.

## 1D vs 2D domain decomposition
- **1D (striping):** Each rank owns a horizontal band spanning the full X dimension. Only two neighbor exchanges (top/bottom halos) are required, but with four ranks the stripes get short and per-step communication dominates, hurting scaling.
- **2D (block/tiled):** Ranks own quadrants (2x2 grid for four ranks) and exchange four halos (N/S/E/W). Communication is higher per rank, but the surface-to-volume ratio improves as the grid grows, so scaling is better for larger problems.
- Boundary conditions explored here: hot top/bottom plates (30-cell bands) with cold or free sides; explicit time stepping for diffusion (`dt` chosen for stability).

## Performance metrics (from `plot_scaling.py`)
Measured wall times (seconds) for a modest grid:

| Procs | 2D time | 1D time |
|-------|---------|---------|
| 1     | 0.0367  | 0.0457  |
| 2     | 0.0551  | 0.0505  |
| 4     | 0.0888  | 0.2174  |

Derived speedup / efficiency:
- 2D: speedup = [1.000, 0.667, 0.414], efficiency = [1.000, 0.333, 0.103]
- 1D: speedup = [1.000, 0.905, 0.210], efficiency = [1.000, 0.453, 0.053]

Observations: The small problem size and cross-node latency dominate, so 4-way runs slow down (especially 1D). Larger grids or co-locating ranks on fewer instances would improve the surface-to-volume ratio and hide latency.

## Visual outputs
- `heat_with_mpi_ranks.png` shows the stitched 2D domain and rank layout.
- `speedup_1d_vs_2d.png`, `efficiency_1d_vs_2d.png` plot the scaling metrics.
- Other scripts generate additional PNGs or on-screen animations; see comments in each file for saving animations to MP4.

## Re-running experiments
1. Run the MPI solver on the cluster to regenerate rank CSVs (1D vs 2D layouts).
2. Copy CSVs locally; if needed, run `python fix_csv.py`.
3. Visualize with `visualize_1d.py`, `visualize2.py`, or `visualize_ranks_overlay.py`.
4. Update `plot_scaling.py` with new timings to refresh the speedup/efficiency charts.
