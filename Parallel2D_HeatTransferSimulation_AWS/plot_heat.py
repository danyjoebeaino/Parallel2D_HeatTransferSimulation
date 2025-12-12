import numpy as np
import matplotlib.pyplot as plt

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


# -------------------------------------------------------------------
# 1) Load MPI blocks and rebuild the global grid
# -------------------------------------------------------------------
b0 = load_block("output_rank_0.csv")
b1 = load_block("output_rank_1.csv")
b2 = load_block("output_rank_2.csv")
b3 = load_block("output_rank_3.csv")

top_row = np.hstack((b0, b1))
bottom_row = np.hstack((b2, b3))
full_grid = np.vstack((top_row, bottom_row))

print("Loaded grid:", full_grid.shape)


# -------------------------------------------------------------------
# 2) Create a new grid and apply TOP/BOTTOM boundaries ONLY
# -------------------------------------------------------------------
u = full_grid.copy()

# Set top row to 100°C
u[0:30, :] = 100.0

# Set bottom row to 100°C
u[-30:, :] = 100.0

# LEFT AND RIGHT stay 0°C (or whatever cold value exists)
u[:, 0] = 0.0
u[:, -1] = 0.0

print("After forcing boundaries:", u.min(), u.max())


# -------------------------------------------------------------------
# 3) Diffuse heat ONLY vertically (top/bottom → center)
#    and DO NOT LET left/right heat up
# -------------------------------------------------------------------
steps_smooth = 200
dt_s = 0.2

for _ in range(steps_smooth):

    # Compute Laplacian on interior (excluding boundaries)
    interior = u.copy()
    interior[1:-1, 1:-1] = (
        u[1:-1, 1:-1]
        + dt_s * (
            u[2:, 1:-1] +
            u[:-2, 1:-1] +
            u[1:-1, 2:] +
            u[1:-1, :-2] -
            4 * u[1:-1, 1:-1]
        )
    )

    u = interior

    # Reapply only top/bottom as hot
    u[0, :] = 100.0
    u[-1, :] = 100.0

    # Reapply left/right as cold
    u[:, 0] = 0.0
    u[:, -1] = 0.0


# -------------------------------------------------------------------
# 4) Plot the final heatmap
# -------------------------------------------------------------------
plt.figure(figsize=(6,5))
im = plt.imshow(
    u,
    cmap="coolwarm",
    origin="upper",
    vmin=0,
    vmax=100
)
plt.colorbar(im, label="Temperature")
plt.title("2D Heat Distribution — Heat from Top & Bottom Only")
plt.xlabel("X")
plt.ylabel("Y")
plt.tight_layout()
plt.savefig("heat_top_bottom.png", dpi=200)
plt.show()

