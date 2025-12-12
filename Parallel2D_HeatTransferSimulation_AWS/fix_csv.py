import numpy as np

files = [
    "output_rank_0.csv",
    "output_rank_1.csv",
    "output_rank_2.csv",
    "output_rank_3.csv",
]

for f in files:
    print(f"Fixing {f}...")

    arr = np.genfromtxt(f, delimiter=",", filling_values=0.0)

    # if the file has 101 columns, remove the last one
    if arr.shape[1] == 101:
        arr = arr[:, :100]

    # save the corrected CSV
    out_file = f.replace(".csv", "_fixed.csv")
    np.savetxt(out_file, arr, delimiter=",")

    print(f"Saved fixed file: {out_file}")

print("All CSV files fixed!")

