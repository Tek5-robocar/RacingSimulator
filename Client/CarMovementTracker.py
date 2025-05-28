import numpy as np
from math import atan2, degrees


class CarMovementTracker:
    def __init__(self):
        """
        Initialize the car movement tracker.
        Starts with no history and zero reference angle.
        """
        self.positions = []  # List to store all historical positions
        self.movement_angles = []  # List to store angles between consecutive positions
        self.reference_angles = []  # List to store angles relative to initial reference (0°)
        self.reference_direction = None  # Stores the initial movement direction
        self.has_reference = False  # Flag to track if we've established a reference

    def add_position(self, position):
        """
        Add a new position to the tracker and calculate angles.

        Args:
            position (tuple/list/np.array): (x, y) coordinates of the car
        """
        position = np.array(position, dtype=float)

        # Store the new position
        self.positions.append(position.copy())

        # Calculate movement angle if we have at least one previous position
        if len(self.positions) > 1:
            prev_pos = self.positions[-2]
            current_pos = self.positions[-1]

            # Calculate displacement vector
            displacement = current_pos - prev_pos

            # Calculate angle in radians, then convert to degrees
            angle_rad = atan2(displacement[1], displacement[0])
            angle_deg = degrees(angle_rad)

            # Store the raw movement angle
            self.movement_angles.append(angle_deg)

            # Set reference direction if this is our first movement
            if not self.has_reference:
                self.reference_direction = displacement
                self.reference_angles.append(0.0)
                self.has_reference = True
            else:
                # Calculate angle relative to reference direction
                ref_angle = self._angle_between_vectors(self.reference_direction, displacement)
                self.reference_angles.append(ref_angle)
        else:
            # First position, no angle to calculate yet
            self.movement_angles.append(None)
            self.reference_angles.append(None)

        print(f'last angle: {self.movement_angles[-1]}')

    def _angle_between_vectors(self, v1, v2):
        """
        Calculate the angle in degrees between two vectors.

        Args:
            v1, v2: numpy arrays representing vectors

        Returns:
            float: angle between vectors in degrees (-180 to 180)
        """
        # Handle zero vectors
        if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
            return 0.0

        # Calculate angle using dot product and cross product
        unit_v1 = v1 / np.linalg.norm(v1)
        unit_v2 = v2 / np.linalg.norm(v2)

        dot_product = np.dot(unit_v1, unit_v2)
        cross_product = np.cross(unit_v1, unit_v2)

        angle_rad = np.arctan2(cross_product, dot_product)
        return degrees(angle_rad)

    def get_current_data(self):
        """
        Get the most recent position and angle data.

        Returns:
            dict: {
                'position': current position,
                'movement_angle': angle from previous position (None if first position),
                'reference_angle': angle relative to initial direction (None if first position)
            }
        """
        if not self.positions:
            return None

        return {
            'position': self.positions[-1],
            'movement_angle': self.movement_angles[-1],
            'reference_angle': self.reference_angles[-1]
        }

    def get_all_data(self):
        """
        Get all recorded position and angle data.

        Returns:
            dict: {
                'positions': list of all positions,
                'movement_angles': list of all movement angles,
                'reference_angles': list of all reference angles
            }
        """
        return {
            'positions': self.positions,
            'movement_angles': self.movement_angles,
            'reference_angles': self.reference_angles
        }

    def reset(self):
        """Reset the tracker to initial state."""
        self.positions = []
        self.movement_angles = []
        self.reference_angles = []
        self.reference_direction = None
        self.has_reference = False