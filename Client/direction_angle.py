import math
import random

import numpy as np
from matplotlib import pyplot as plt

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc


def angle_between_vectors(a, b):
    """
    Calculate the angle between two vectors in radians.

    Parameters:
        a, b: Input vectors (as lists or numpy arrays)

    Returns:
        Angle in radians between 0 and π
    """
    a = np.array(a)
    b = np.array(b)

    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    # Handle division by zero
    if norm_a == 0 or norm_b == 0:
        raise ValueError("One of the vectors has zero magnitude")

    cos_theta = dot_product / (norm_a * norm_b)
    # Handle floating point precision issues
    cos_theta = np.clip(cos_theta, -1.0, 1.0)

    return np.arccos(cos_theta), 'left' if dot_product < 10 else 'right'

def get_direction(line_point1, line_point2):
    p1 = np.array(line_point1)
    p2 = np.array(line_point2)

    direction = p2 - p1
    return direction

def draw_perpendicular_line(through_point, direction, length: float = 5):
    tp = np.array(through_point)
    perpendicular_dir = np.array([-direction[1], direction[0]])

    perpendicular_dir = perpendicular_dir / np.linalg.norm(perpendicular_dir)

    start_point = tp - perpendicular_dir * length
    end_point = tp + perpendicular_dir * length

    plt.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]], 'r-', label='Perpendicular line')


def find_perpendicular_point(p1, p2, distance, side='right'):
    p1 = np.array(p1)
    p2 = np.array(p2)

    direction = p2 - p1

    if side == 'right':
        perpendicular = np.array([direction[1], -direction[0]])
    else:
        perpendicular = np.array([-direction[1], direction[0]])

    perpendicular = perpendicular / np.linalg.norm(perpendicular)

    third_point = p1 + perpendicular * distance

    return third_point[0], third_point[1]


def draw_circle_parametric(center, radius, points=100):
    theta = np.linspace(0, 2 * np.pi, points)
    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)

    plt.plot(x, y, '--')


def get_random_point_on_path(path):
    """
    Returns a random point along the path.

    Args:
        path: List of (x,y) tuples representing the path

    Returns:
        (x,y) tuple of a random point on the path
    """
    # Calculate the length of each segment
    segment_lengths = []
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        segment_lengths.append(np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

    total_length = sum(segment_lengths)

    # Choose a random distance along the path
    random_distance = random.uniform(0, total_length)

    # Find which segment this distance falls in
    accumulated = 0
    for i in range(len(segment_lengths)):
        if accumulated + segment_lengths[i] >= random_distance:
            # This is our segment
            x1, y1 = path[i]
            x2, y2 = path[i + 1]

            # Calculate the position along this segment
            segment_fraction = (random_distance - accumulated) / segment_lengths[i]
            x = x1 + segment_fraction * (x2 - x1)
            y = y1 + segment_fraction * (y2 - y1)
            return (x, y)

        accumulated += segment_lengths[i]

    # If we get here (shouldn't happen), return last point
    return path[-1]


def find_point_D(A, B, C):
    """
    Find point D such that:
    - AD is perpendicular to AB
    - AD = CD

    Parameters:
        A, B, C: Tuple or list of (x,y) coordinates

    Returns:
        D: (x,y) coordinates of point D (only one solution exists)
    """
    A = np.array(A, dtype=float)
    B = np.array(B, dtype=float)
    C = np.array(C, dtype=float)

    # 1. Find equation of line perpendicular to AB through A
    # AB vector
    AB = B - A

    # Slope of AB (m1)
    if AB[0] == 0:  # Vertical line
        # Perpendicular is horizontal: y = A[1]
        perp_slope = 0
        perp_intercept = A[1]
    else:
        m1 = AB[1] / AB[0]
        # Slope of perpendicular (m2 = -1/m1)
        perp_slope = -1 / m1
        perp_intercept = A[1] - perp_slope * A[0]

    # 2. Find perpendicular bisector of AC
    # Midpoint of AC
    midpoint = (A + C) / 2

    # Slope of AC (m3)
    if C[0] - A[0] == 0:  # Vertical line
        # Perpendicular bisector is horizontal: y = midpoint[1]
        bisector_slope = 0
        bisector_intercept = midpoint[1]
    else:
        m3 = (C[1] - A[1]) / (C[0] - A[0])
        # Slope of perpendicular bisector (m4 = -1/m3)
        bisector_slope = -1 / m3
        bisector_intercept = midpoint[1] - bisector_slope * midpoint[0]

    # 3. Find intersection of these two lines
    if AB[0] == 0:  # Original AB is vertical
        # Perpendicular is horizontal (y = perp_intercept)
        # Plug into bisector equation
        x = A[0]  # Same x as point A
        y = perp_intercept
    elif C[0] - A[0] == 0:  # AC is vertical
        # Bisector is horizontal (y = midpoint[1])
        # Plug into perpendicular equation
        x = (midpoint[1] - perp_intercept) / perp_slope
        y = midpoint[1]
    else:
        # Solve system of equations
        # y = perp_slope*x + perp_intercept
        # y = bisector_slope*x + bisector_intercept
        x = (bisector_intercept - perp_intercept) / (perp_slope - bisector_slope)
        y = perp_slope * x + perp_intercept

    D = np.array([x, y])

    # Verify distances
    AD = np.linalg.norm(D - A)
    CD = np.linalg.norm(D - C)

    return D


def vector_between_points(A, B):
    """Returns the vector from point A to point B in 2D"""
    return (B[0] - A[0], B[1] - A[1])


def draw_arc_with_direction(A, B, r, direction='left'):
    """
    Draw a circular arc between two points with specified radius and direction.

    Parameters:
        A, B: Tuples (x,y) of the two points
        r: Desired radius of the arc
        direction: 'left' or 'right' to specify curve direction
        figsize: Size of the figure
    """
    A = np.array(A)
    B = np.array(B)

    # Calculate AB vector and length
    AB = B - A
    AB_length = np.linalg.norm(AB)

    # Check radius feasibility
    if r < AB_length / 2:
        min_r = AB_length / 2
        print(f"Error: Radius too small. Minimum radius is {min_r:.2f}")
        return

    # Find midpoint and perpendicular direction
    midpoint = (A + B) / 2
    perp_dir = np.array([-AB[1], AB[0]]) / AB_length  # Normalized perpendicular

    # Calculate center position based on direction
    h = np.sqrt(r ** 2 - (AB_length / 2) ** 2)
    if direction.lower() == 'left':
        center = midpoint + h * perp_dir
    elif direction.lower() == 'right':
        center = midpoint - h * perp_dir
    else:
        raise ValueError("Direction must be either 'left' or 'right'")

    # Calculate angles for the arc
    vec_A = A - center
    vec_B = B - center
    angle_A = np.degrees(np.arctan2(vec_A[1], vec_A[0]))
    angle_B = np.degrees(np.arctan2(vec_B[1], vec_B[0]))

    # Ensure proper angle order
    if angle_B < angle_A:
        angle_A, angle_B = angle_B, angle_A

    arc = Arc(center, 2 * r, 2 * r, angle=0,
              theta1=angle_A, theta2=angle_B,
              color='green', linewidth=2)
    plt.gca().add_patch(arc)

if __name__ == '__main__':
    path = [
        (0.0, 0.0),
        (1.0, 2.0),
        (2.0, 2.5),
        (4.0, 3.0),
        (10.0, 1.0),
    ]
    plt.plot([path_point[0] for path_point in path], [path_point[1] for path_point in path])

    target_pos = get_random_point_on_path(path)
    plt.plot(target_pos[0], target_pos[1], 'o')

    front_w_pos = (1.0, 0.5)
    back_w_pos = (0.5, 0.2)
    plt.plot([back_w_pos[0], front_w_pos[0]], [back_w_pos[1], front_w_pos[1]])

    car_dir = vector_between_points(target_pos, front_w_pos)

    # icr = find_perpendicular_point(back_w_pos, front_w_pos, distance=r, side='left')
    icr = find_point_D(back_w_pos, front_w_pos, target_pos)
    # plt.plot(icr[0], icr[1], 'o')

    r = math.sqrt((back_w_pos[0] - icr[0]) ** 2 + (back_w_pos[1] - icr[1]) ** 2)

    # draw_circle_parametric(center=icr, radius=r)
    wheel_dir = get_direction(line_point1=icr, line_point2=front_w_pos)
    draw_perpendicular_line(direction=wheel_dir, through_point=front_w_pos, length=0.5)

    angle, direction = angle_between_vectors(car_dir, wheel_dir)
    wheel_angle_needed = 90.0 - np.degrees(angle)

    draw_arc_with_direction(A=back_w_pos, B=target_pos, r=r, direction=direction)

    print(f'Wheel angle needed: {wheel_angle_needed}, angle: {angle}')

    plt.axis('equal')
    plt.show()
