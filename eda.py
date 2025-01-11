# import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import tkinter as tk
# from tkinter import ttk
#
# import utils
# from utils import load_config
#
#
# def main():
#     config = load_config('config.ini')
#
#     data = pd.read_csv(config.get('DEFAULT', 'csv_path'))
#     # data = utils.normalize_columns_between_largest(data)
#
#     # Define numerical columns
#     numerical_columns = data.columns
#
#     # Create the main Tkinter window
#     root = tk.Tk()
#     root.title("Scrollable Plots")
#
#     # Create a canvas and scrollbar
#     canvas = tk.Canvas(root)
#     scroll_y = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
#
#     # Create a frame to hold the plots
#     frame = ttk.Frame(canvas)
#     canvas.create_window((0, 0), window=frame, anchor="nw")
#
#     # Configure the canvas to scroll with the scrollbar
#     canvas.configure(yscrollcommand=scroll_y.set)
#     canvas.pack(side="left", fill="both", expand=True)
#     scroll_y.pack(side="right", fill="y")
#
#     # Plot each numerical column and add to the frame
#     for col in numerical_columns:
#         fig, ax = plt.subplots(figsize=(5, 3))  # Adjust figure size as needed
#         sns.histplot(data[col], kde=True, ax=ax)
#         ax.set_title(f"Distribution of {col}")
#
#         # Embed the plot into the Tkinter frame
#         canvas_plot = FigureCanvasTkAgg(fig, master=frame)
#         canvas_plot.get_tk_widget().pack()
#
#     # Update the scroll region
#     frame.update_idletasks()
#     canvas.config(scrollregion=canvas.bbox("all"))
#
#     # Run the Tkinter event loop
#     root.mainloop()
#
#
# if __name__ == '__main__':
#     main()
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

from utils import load_config, preprocess_and_normalize

config = load_config('config.ini')

data = pd.read_csv(config.get('DEFAULT', 'csv_path'))

# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)

# Normalize the data
normalized_data = preprocess_and_normalize(data)

# Create the Tkinter window
root = tk.Tk()
root.title("Normalized Data Visualizations")

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

# Plot each normalized column
for col in normalized_data.columns:
    fig, ax = plt.subplots(figsize=(5, 3))  # Adjust the figure size
    sns.histplot(normalized_data[col], kde=True, ax=ax)
    ax.set_title(f"Normalized Distribution of {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Density")

    # Embed the plot into the Tkinter frame
    canvas_plot = FigureCanvasTkAgg(fig, master=frame)
    canvas_plot.get_tk_widget().pack()

# Update the scroll region
frame.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

# Run the Tkinter event loop
root.mainloop()
