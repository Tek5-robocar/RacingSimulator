import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

from utils import load_config


def init_window():
    """
    Initialize the window and return the Tkinter window, frame where the widget will be added and scrollable canvas
    """
    root = tk.Tk()
    root.title("Normalized and Augmented Data Visualizations")
    canvas = tk.Canvas(root)
    scroll_y = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scroll_y.set)
    canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")
    return root, frame, canvas


def display_distribution_graph(data: pd.DataFrame, frame):
    """
    Display the distribution matplotlib plot on the Tkinter frame
    """
    for col in data.columns:
        fig, ax = plt.subplots(figsize=(5, 3))
        sns.histplot(data[col], kde=True, ax=ax, color="blue", label="Original")
        ax.set_title(f"Normalized and Augmented Distribution of {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Density")
        ax.legend()
        canvas_plot = FigureCanvasTkAgg(fig, master=frame)
        canvas_plot.get_tk_widget().pack()
        plt.close(fig)


def main():
    root, frame, canvas = init_window()

    config = load_config('config.ini')
    data = pd.read_csv(config.get('DEFAULT', 'csv_path'))
    display_distribution_graph(data, frame)

    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    root.mainloop()


if __name__ == '__main__':
    main()
