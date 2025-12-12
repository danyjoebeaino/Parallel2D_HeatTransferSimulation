import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# --------------------------------------------------
# Grid + physical parameters
# --------------------------------------------------
NX, NY = 200, 200      # grid size (change if you want)
hot_T = 100.0
cold_T = 0.0

dt = 0.2               # time step
steps_total = 600      # total solver steps
snap_every = 3         # solver steps between frames
n_frames = steps_total // snap_every

# --------------------------------------------------
# Initial condition: cold interior, hot top/bottom
# --------------------------------------------------
u = np.zeros((NX, NY), dtype=float)

# hot plates
u[0, :]   = hot_T      # top
u[-1, :]  = hot_T      # bottom

# left/right cold (already 0, but we force it every step)
u[:, 0]   = cold_T
u[:, -1]  = cold_T

def step_heat(u):
    """One explicit time step of 2D heat equation."""
    new = u.copy()
    new[1:-1, 1:-1] = (
        u[1:-1, 1:-1]
        + dt * (
            u[2:, 1:-1] +
            u[:-2, 1:-1] +
            u[1:-1, 2:] +
            u[1:-1, :-2] -
            4 * u[1:-1, 1:-1]
        )
    )

    # Re-apply boundary conditions (hot top/bottom, cold sides)
    new[0, :]  = hot_T
    new[-1, :] = hot_T
    new[:, 0]  = cold_T
    new[:, -1] = cold_T

    return new

# --------------------------------------------------
# Set up animation
# --------------------------------------------------
fig, ax = plt.subplots(figsize=(6, 5))
im = ax.imshow(
    u,
    cmap="coolwarm",
    origin="upper",
    vmin=0,
    vmax=100
)
cbar = plt.colorbar(im, ax=ax, label="Temperature (°C)")
ax.set_xlabel("X")
ax.set_ylabel("Y")
title = ax.set_title("Heat propagation — step 0")

def update(frame):
    global u
    # do several solver steps between frames so it moves nicely
    for _ in range(snap_every):
        u = step_heat(u)

    im.set_array(u)
    title.set_text(f"Heat propagation — step {frame * snap_every}")
    return [im, title]

anim = FuncAnimation(
    fig,
    update,
    frames=n_frames,
    interval=50,   # ms between frames
    blit=True
)

plt.tight_layout()
plt.show()

# If you want to save it as a video (needs ffmpeg installed):
# anim.save("heat_propagation_top_bottom.mp4", fps=30, dpi=200)

