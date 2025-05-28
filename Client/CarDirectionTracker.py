import math


class CarDirectionTracker:
    def __init__(self):
        self.positions = []  # Stores history of (front_pos, back_pos) tuples
        self.reference_vector = None  # Initial direction vector (normalized)
        self.last_angle = None  # Last calculated angle

    def add_position(self, front_pos, back_pos):
        """
        Add a new position measurement (front and back points of the car)

        Args:
            front_pos: (x, y) tuple of front point
            back_pos: (x, y) tuple of back point
        """
        # Store the new position
        self.positions.append((front_pos, back_pos))

        # If this is the first position, set it as reference
        if len(self.positions) == 1:
            self._set_reference_vector(front_pos, back_pos)
            self.last_angle = 0.0
            return 0.0  # No angle change on first frame

        # Calculate current angle and change
        current_angle = self._calculate_current_angle(front_pos, back_pos)
        angle_change = self._calculate_angle_change(current_angle)

        self.last_angle = current_angle
        return angle_change

    def _set_reference_vector(self, front_pos, back_pos):
        """Set the initial reference vector (direction at angle 0°)"""
        dx = front_pos[0] - back_pos[0]
        dy = front_pos[1] - back_pos[1]
        length = math.sqrt(dx * dx + dy * dy)
        self.reference_vector = (dx / length, dy / length)

    def _calculate_current_angle(self, front_pos, back_pos):
        """Calculate current angle relative to reference vector"""
        # Get current direction vector
        dx = front_pos[0] - back_pos[0]
        dy = front_pos[1] - back_pos[1]
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:
            return self.last_angle  # No movement, return last angle

        current_vector = (dx / length, dy / length)

        # Calculate angle between reference and current vector
        dot_product = (self.reference_vector[0] * current_vector[0] +
                       self.reference_vector[1] * current_vector[1])

        # Clamp to avoid floating point errors
        dot_product = max(-1.0, min(1.0, dot_product))

        angle = math.degrees(math.acos(dot_product))

        # Determine sign using cross product
        cross_product = (self.reference_vector[0] * current_vector[1] -
                         self.reference_vector[1] * current_vector[0])

        if cross_product < 0:
            angle = -angle

        return angle

    def _calculate_angle_change(self, current_angle):
        """Calculate the difference between current angle and last angle"""
        if self.last_angle is None:
            return 0.0

        # Calculate minimal angle difference (handles wrap-around at 180°)
        diff = current_angle - self.last_angle
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360

        return diff

    def get_current_direction(self):
        """Get the current direction angle in degrees"""
        if not self.positions:
            return None
        front, back = self.positions[-1]
        return self._calculate_current_angle(front, back)

    def get_reference_direction(self):
        """Get the reference direction vector"""
        return self.reference_vector