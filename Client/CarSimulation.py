import math

import numpy as np
from matplotlib import pyplot as plt

from direction_angle import vector_between_points, find_point_D, angle_between_vectors, get_direction


def euclidean_distance(point1, point2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(point1, point2)))


class PathFollower:
    def __init__(self, lookahead_distance=2.0):
        self.recorded_path = []
        self.path_index = 0
        self.lookahead_distance = lookahead_distance
        self.start_angle_deg = 0.0
        self.last_position = None

    def closest_point_with_index(self, target):
        if not self.recorded_path:
            return None, None

        min_distance = float('inf')
        closest_point = None
        closest_index = -1

        for i, point in enumerate(self.recorded_path):
            dist = euclidean_distance(target, point)
            if dist < min_distance:
                min_distance = dist
                closest_point = point
                closest_index = i

        return closest_point, closest_index

    def add_position(self, x, y, steering):
        x = round(x, 0)
        y = round(y, 0)
        # if len(self.recorded_path) > 1:
        #     angle = 0.0
        #     angle_diff = 0.0
        # else:
        #     angle = 0.0
        #     angle_diff = 0.0

        self.recorded_path.append((x, y))

    def show_path(self):
        plt.plot([point[0] for point in self.recorded_path], [point[1] for point in self.recorded_path])
        plt.show()

    def look_ahead(self, actual_position: (float, float)) -> (float, float):
        closest_point, closest_index = self.closest_point_with_index(actual_position)

        if len(self.recorded_path) > closest_index + self.lookahead_distance:
            return self.recorded_path[closest_index + self.lookahead_distance]
        else:
            return self.recorded_path[-1]

    def get_steering(self, actual_position: (float, float)) -> float:
        if not self.last_position:
            return 0.0
        destination = self.look_ahead(actual_position)

        car_dir = vector_between_points(destination, actual_position)

        icr = find_point_D(self.last_position, actual_position, destination)

        r = math.sqrt((self.last_position[0] - icr[0]) ** 2 + (self.last_position[1] - icr[1]) ** 2)
        wheel_dir = get_direction(line_point1=icr, line_point2=actual_position)

        angle, direction = angle_between_vectors(car_dir, wheel_dir)
        wheel_angle_needed = 90.0 - np.degrees(angle)
        print(wheel_angle_needed)
        return