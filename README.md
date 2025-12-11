2D Heat Transfer Simulation
===========================

A compact C and Python toolkit to experiment with the 2D heat equation using an explicit finite-difference scheme. The repo includes a basic serial solver, a richer version with progress tracking and residual monitoring, validation helpers, and multiple visualization workflows (heatmaps, animations, 3D surfaces, and convergence plots).

## What’s here
- `heat_serial.c`: Minimal 2D heat solver (fixed grid and boundary conditions).
- `heat_serial_advanced.c`: Feature-rich solver with validation, progress bars, residual checks, and configurable boundary temperatures.
- `validation_simple.c`: Sanity checks for grid, timestep stability, and memory footprint.
- `visualize.py`: Generates heatmaps, slices, and a basic animation from simulation outputs.
- `advanced_visualize.py`: Higher-end visuals (comparison grids, 3D surface, heat flux analysis, advanced GIF).
- `config.json`: Defaults for visualization/customization.
- `run_simulation.sh`: One-shot helper to build, run, and visualize the basic pipeline.

## Prerequisites
- `gcc`, `make`
- `python3` with `numpy`, `matplotlib`, `scipy`, `pillow`
  - Install the Python bits via `make install-deps` (uses `pip3`).

## Quick start
```bash
make all            # build basic + advanced solvers and the validator
make run-advanced   # run the advanced solver (writes output_step_*.txt + output_final.txt)
make visualize      # create heatmaps/animation from the saved outputs
make visualize-advanced  # run the richer visualization suite
```

Prefer a single “go” command? `./run_simulation.sh` will build, run the basic solver, and call `visualize.py`.

## Typical workflow
1) Build: `make all`  
2) (Optional) Validate params only: `make validate`  
3) Run a solver:
   - Basic: `make run` (uses `heat_serial.c`)
   - Advanced: `make run-advanced` (uses `heat_serial_advanced.c`)
4) Visualize:
   - Basic plots/GIF: `make visualize`
   - Advanced visuals (comparison grid, 3D surface, convergence, heat flux, GIF): `make visualize-advanced`

## Outputs
- Simulation snapshots: `output_step_*.txt`, `output_final.txt`
- Basic visuals: `plots/heatmap_*.png`, `heat_simulation.gif`, `final_temperature.png`, `temperature_slices_final.png`
- Advanced visuals: `temperature_comparison.png`, `3d_surface_final.png`, `convergence_analysis.png`, `heat_flux_analysis.png`, `advanced_simulation.gif`
- Cleanup: `make clean` (binaries) or `make clean-all` (binaries + outputs/plots/GIFs)

## Tweaks and notes
- Adjust the simulation parameters in `heat_serial_advanced.c` (`SimulationConfig config`) for grid size, timestep, diffusivity, and boundary temps.
- The advanced solver prints a stability warning when `dt` exceeds the CFL limit; reduce `dt` if you see the warning.
- Visualization defaults (colormap, animation FPS, DPI) live in `config.json`; edit them to taste.
