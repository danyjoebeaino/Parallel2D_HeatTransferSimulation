import numpy as np
import matplotlib.pyplot as plt

files = [
    "output_rank_0_fixed.csv",
    "output_rank_1_fixed.csv",
    "output_rank_2_fixed.csv",
    "output_rank_3_fixed.csv"
]

data = []
for f in files:
    print("Loading:", f)
    arr = np.genfromtxt(f, delimiter=",", filling_values=0.0)
    data.append(arr)

# Stitch 2x2 layout
top = np.hstack((data[0], data[1]))
bottom = np.hstack((data[2], data[3]))
global_grid = np.vstack((top, bottom))

print("Global grid shape:", global_grid.shape)

plt.figure(figsize=(7,7))
plt.imshow(global_grid, cmap='hot', interpolation='bilinear', origin='lower')
plt.colorbar()
plt.title("Heatmap from 4 rank CSVs")
plt.show()

