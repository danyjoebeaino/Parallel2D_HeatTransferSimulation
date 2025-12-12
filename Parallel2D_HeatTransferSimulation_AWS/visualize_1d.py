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


# ---------------------------------------------------------
# 1) Load the 1D MPI blocks
#    Each rank has a horizontal stripe (same width, fewer rows)
# ---------------------------------------------------------
b0 = load_block("output1d_rank_0.csv")
b1 = load_block("output1d_rank_1.csv")
b2 = load_block("output1d_rank_2.csv")
b3 = load_block("output1d_rank_3.csv")

print("Block shapes:")
print("rank 0:", b0.shape)
print("rank 1:", b1.shape)
print("rank 2:", b2.shape)
print("rank 3:", b3.shape)

# Stack vertically in rank order:
full_grid_1d = np.vstack((b0, b1, b2, b3))
print("Full 1D-reconstructed grid shape:", full_grid_1d.shape)


# ---------------------------------------------------------
# 2) Plot the full 1D reconstruction
# ---------------------------------------------------------
plt.figure(figsize=(6,5))
im = plt.imshow(
    full_grid_1d,
    cmap="coolwarm",
    origin="upper",
    vmin=0,
    vmax=100
)
plt.colorbar(im, label="Temperature (°C)")
plt.title("2D Heat Distribution (1D domain decomposition result)")
plt.xlabel("X")
plt.ylabel("Y")
plt.tight_layout()
plt.savefig("heat_1d_final.png", dpi=200)
plt.show()

