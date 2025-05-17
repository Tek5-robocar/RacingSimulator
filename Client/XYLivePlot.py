import math
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import queue
import threading


class LiveXYPlotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ML-Agents Live XY Plot")

        # Thread-safe data queue
        self.data_queue = queue.Queue()

        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Agent Position Tracking")
        self.ax.set_xlabel("X Position")
        self.ax.set_ylabel("Y Position")
        self.ax.grid(True)

        # Initialize plot
        self.line, = self.ax.plot([], [], 'bo-', markersize=5, alpha=0.5)
        self.line2, = self.ax.plot([], [], 'bo-', markersize=5, alpha=0.5)
        self.current_pos, = self.ax.plot([], [], 'ro', markersize=8)
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)

        # Embed in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Data storage
        self.x_data = []
        self.y_data = []

        self.x_pos = []
        self.y_pos = []

        # Start update loop
        self.update_interval = 100  # ms
        self.schedule_update()

    def schedule_update(self):
        """Schedule the next plot update"""
        self.root.after(self.update_interval, self.update_plot)

    def update_plot(self):
        """Check for new data and update plot"""
        # Get all available points from queue
        new_points = []
        while True:
            try:
                x, y = self.data_queue.get_nowait()
                new_points.append((x, y))
            except queue.Empty:
                break

        # Add new data
        for x, y in new_points:
            self.x_data.append(x)
            self.y_data.append(y)

        if self.x_pos:
            self.line.set_data(self.x_pos, self.y_pos)

        # Update plot if we have data
        if self.x_data:
            self.line.set_data(self.x_data, self.y_data)

            # Show current position
            if new_points:
                last_x, last_y = new_points[-1]
                self.current_pos.set_data([last_x], [last_y])

            # Auto-scale axes with padding
            if len(self.x_data) > 1:
                x_min, x_max = min(self.x_data), max(self.x_data)
                y_min, y_max = min(self.y_data), max(self.y_data)

                x_padding = max((x_max - x_min) * 0.1, 0.5)
                y_padding = max((y_max - y_min) * 0.1, 0.5)

                self.ax.set_xlim(x_min - x_padding, x_max + x_padding)
                self.ax.set_ylim(y_min - y_padding, y_max + y_padding)

            self.canvas.draw()

        # Schedule next update
        self.schedule_update()

    def update_from_external_data(self, x, y):
        """Thread-safe method to add data from ML-Agents"""
        self.data_queue.put((x, y))

    def get_closest_point(self, x, y):
        closest_point = (self.x_pos[0], self.y_pos[0])
        closest_distance = math.sqrt((x - closest_point[0]) ** 2 + (y - closest_point[1]) ** 2)
        for x1, y1 in zip(self.x_pos, self.y_pos):
            distance = math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
            if distance < closest_distance:
                closest_distance = distance
                closest_point = (x1, y1)
        return closest_point

    def get_next_point(self, last, actual):
        last_x_index = self.x_data.index(last[0])
        last_y_index = self.y_data.index(last[1])

        actual_x_index = self.x_data.index(actual[0])
        actual_y_index = self.y_data.index(actual[1])

        x_index_diff = last_x_index - actual_x_index
        y_index_diff = last_y_index - actual_y_index

        return self.x_data[actual_x_index + x_index_diff], self.y_data[actual_y_index + y_index_diff]
