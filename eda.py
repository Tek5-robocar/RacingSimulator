import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

from train import augment_data
from utils import load_config, preprocess_and_normalize

# Load configuration and data
config = load_config('config.ini')
data = pd.read_csv(config.get('DEFAULT', 'csv_path'))
augmented_data = np.apply_along_axis(augment_data, axis=1, arr=data.to_numpy())


normalized_augmented_data = preprocess_and_normalize(pd.DataFrame(augmented_data))
normalized_augmented_data = normalized_augmented_data.to_numpy()
# normalized_augmented_data = np.array([normalized_augmented_data[:, :10], normalized_augmented_data[:, 13]])
# normalized_augmented_data = np.array([
#     normalized_augmented_data[:, :4].sum(axis=1) / 4,
#     normalized_augmented_data[:, 4:6].sum(axis=1) / 2,
#     normalized_augmented_data[:, 6:10].sum(axis=1) / 4,
#     normalized_augmented_data[:, 10],
#     normalized_augmented_data[:, 12]
# ]).T


normalized_data = preprocess_and_normalize(data)
normalized_data = normalized_data.to_numpy()
# normalized_data = np.array([normalized_data[:, :10], normalized_data[:, 13]])
# normalized_data = np.array([
#     normalized_data[:, :4].sum(axis=1) / 4,
#     normalized_data[:, 4:6].sum(axis=1) / 2,
#     normalized_data[:, 6:10].sum(axis=1) / 4,
#     normalized_data[:, 10],
#     normalized_data[:, 12]
# ]).T

normalized_data = pd.DataFrame(normalized_data)
normalized_augmented_data = pd.DataFrame(normalized_augmented_data, columns=normalized_data.columns)

# Create the Tkinter window
root = tk.Tk()
root.title("Normalized and Augmented Data Visualizations")

# Create a canvas and scrollbar
canvas = tk.Canvas(root)
scroll_y = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)

# Create a frame to hold the plots
frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=frame, anchor="nw")

# Configure the canvas
canvas.configure(yscrollcommand=scroll_y.set)
canvas.pack(side="left", fill="both", expand=True)
scroll_y.pack(side="right", fill="y")

# Plot each normalized and augmented column
for col in normalized_data.columns:
    fig, ax = plt.subplots(figsize=(5, 3))  # Adjust the figure size
    sns.histplot(normalized_augmented_data[col], kde=True, ax=ax, color="orange", label="Augmented")
    sns.histplot(normalized_data[col], kde=True, ax=ax, color="blue", label="Original")
    ax.set_title(f"Normalized and Augmented Distribution of {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Density")
    ax.legend()

    # Embed the plot into the Tkinter frame
    canvas_plot = FigureCanvasTkAgg(fig, master=frame)
    canvas_plot.get_tk_widget().pack()

# Update the scroll region
frame.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

# Run the Tkinter event loop
root.mainloop()