import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# --------------------------------------------------
# 1) Load & rebuild global grid from 2D MPI outputs
# --------------------------------------------------
def load_block(filename: str) -> np.ndarray:
    rows = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.endswith(","):
                line = line[:-1]
            parts = [p for p in line.split(",") if p != ""]
            rows.append([float(p) for p in parts])
    return np.array(rows)


b0 = load_block("output_rank_0.csv")
b1 = load_block("output_rank_1.csv")
b2 = load_block("output_rank_2.csv")
b3 = load_block("output_rank_3.csv")

top_row = np.hstack((b0, b1))
bottom_row = np.hstack((b2, b3))
full_grid = np.vstack((top_row, bottom_row))

NX, NY = full_grid.shape
print("Global grid:", NX, "x", NY)

# --------------------------------------------------
# 2) Initial condition: thick hot bands (30 cells)
# --------------------------------------------------
u = full_grid.copy()

hot_T = 100.0
cold_T = 0.0

u[:, :] = 0.0  # start fully cold

top_band = 30
bottom_band = 30

# TOP: first 30 rows hot
u[0:top_band, :] = hot_T
# BOTTOM: last 30 rows hot
u[-bottom_band:, :] = hot_T

# sides cold
u[:, 0] = cold_T
u[:, -1] = cold_T

# smaller dt + more steps = smoother gradient
dt = 0.15
steps_total = 2000
snap_every = 10

snapshots = [u.copy()]

def step_heat(u_arr: np.ndarray) -> np.ndarray:
    """One explicit heat-equation step with thick hot bands."""
    NX, NY = u_arr.shape
    new = u_arr.copy()

    # interior update
    new[1:-1, 1:-1] = (
        u_arr[1:-1, 1:-1]
        + dt * (
            u_arr[2:, 1:-1] + u_arr[:-2, 1:-1] +
            u_arr[1:-1, 2:] + u_arr[1:-1, :-2] -
            4.0 * u_arr[1:-1, 1:-1]
        )
    )

    # re-apply thick boundaries every step
    new[0:top_band, :] = hot_T
    new[-bottom_band:, :] = hot_T
    new[:, 0] = cold_T
    new[:, -1] = cold_T

    return new

for step in range(steps_total):
    u = step_heat(u)
    if step % snap_every == 0:
        snapshots.append(u.copy())

n_frames = len(snapshots)
print("Frames:", n_frames)

# --------------------------------------------------
# 3) Side-by-side 2D heatmap + 3D surface animation
# --------------------------------------------------
X, Y = np.meshgrid(np.arange(NY), np.arange(NX))

fig = plt.figure(figsize=(10, 4.5))

# Left: 2D heatmap
ax1 = fig.add_subplot(1, 2, 1)
im = ax1.imshow(
    snapshots[0],
    cmap="coolwarm",
    origin="upper",
    vmin=0,
    vmax=100,
    interpolation="bicubic"  # smooth rendering
)
cbar = plt.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
cbar.set_label("Temperature (°C)", fontsize=10)
ax1.set_title("Heat map (top & bottom 30 cells hot)", fontsize=11)
ax1.set_xlabel("X")
ax1.set_ylabel("Y")

# Right: 3D surface
ax2 = fig.add_subplot(1, 2, 2, projection="3d")
surf = ax2.plot_surface(
    X, Y, snapshots[0],
    rstride=2, cstride=2,
    cmap="coolwarm",
    linewidth=0,
    antialiased=True
)
ax2.set_zlim(0, 100)
ax2.set_title("3D temperature surface", fontsize=11)
ax2.set_xlabel("X")
ax2.set_ylabel("Y")
ax2.set_zlabel("T (°C)")
ax2.view_init(elev=35, azim=-135)

fig.tight_layout()

def update(frame):
    Z = snapshots[frame]

    # 2D
    im.set_array(Z)

    # 3D
    global surf
    ax2.collections.clear()
    surf = ax2.plot_surface(
        X, Y, Z,
        rstride=2, cstride=2,
        cmap="coolwarm",
        linewidth=0,
        antialiased=True
    )
    ax2.set_zlim(0, 100)
    ax2.set_title(f"3D temperature surface  (step {frame * snap_every})",
                  fontsize=11)
    return [im, surf]

anim = FuncAnimation(
    fig,
    update,
    frames=n_frames,
    interval=60,
    blit=False
)

plt.show()

# To save:
# anim.save("heat_2d_3d_bands_smooth.mp4", fps=30, dpi=200)

