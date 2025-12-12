import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------
# 1) Your measured times (seconds)
# ------------------------------------------------
procs = np.array([1, 2, 4])

# 2D decomposition times
T_2D = np.array([
    0.036733,  # p = 1
    0.055112,  # p = 2
    0.088805   # p = 4
])

# 1D decomposition times
T_1D = np.array([
    0.045687,  # p = 1
    0.050475,  # p = 2
    0.217445   # p = 4
])

# ------------------------------------------------
# 2) Compute speedup and efficiency
# ------------------------------------------------
S_2D = T_2D[0] / T_2D         # speedup = T1 / Tp
E_2D = S_2D / procs           # efficiency = S / p

S_1D = T_1D[0] / T_1D
E_1D = S_1D / procs

print("2D speedup:", S_2D)
print("2D efficiency:", E_2D)
print("1D speedup:", S_1D)
print("1D efficiency:", E_1D)

# ------------------------------------------------
# 3) Plot speedup
# ------------------------------------------------
plt.figure(figsize=(6,4))
plt.plot(procs, S_2D, marker="o", label="2D decomposition")
plt.plot(procs, S_1D, marker="s", label="1D decomposition")
plt.xlabel("Number of processes")
plt.ylabel("Speedup (T1 / Tp)")
plt.title("Parallel speedup: 1D vs 2D domain decomposition")
plt.xticks(procs)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("speedup_1d_vs_2d.png", dpi=200)

# ------------------------------------------------
# 4) Plot efficiency
# ------------------------------------------------
plt.figure(figsize=(6,4))
plt.plot(procs, E_2D, marker="o", label="2D decomposition")
plt.plot(procs, E_1D, marker="s", label="1D decomposition")
plt.xlabel("Number of processes")
plt.ylabel("Efficiency (Speedup / p)")
plt.title("Parallel efficiency: 1D vs 2D domain decomposition")
plt.xticks(procs)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("efficiency_1d_vs_2d.png", dpi=200)

plt.show()

