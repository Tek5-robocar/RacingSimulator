import math
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class GPSPosition:
    latitude: float
    longitude: float
    timestamp: float
    speed: Optional[float] = None
    heading: Optional[float] = None


class PathFollower:
    def __init__(self, path: List[GPSPosition]):
        self.path = self._enhance_path(path)
        self.current_index = 0
        self.last_position = None
        self.last_heading = None
        self.lookahead_distance = 5.0  # meters
        self.wheelbase = 2.5  # meters (adjust for your vehicle)

    def get_commands(self, current_lat: float, current_lon: float) -> Tuple[float, float]:
        """Returns (speed, steering) commands"""
        current_time = time.time()

        # Calculate current speed and heading from movement
        current_speed, current_heading = self._calculate_kinematics(current_lat, current_lon, current_time)

        # Get lookahead point
        lookahead_point = self._get_lookahead_point()

        # Calculate required commands
        steering = self._calculate_steering(current_lat, current_lon, current_heading, lookahead_point)
        speed = self._calculate_speed(current_heading, lookahead_point)

        # Update position tracking
        self._update_position(current_lat, current_lon, current_time, current_speed, current_heading)

        return speed, steering

    def _calculate_kinematics(self, lat: float, lon: float, timestamp: float) -> Tuple[float, float]:
        """Calculate current speed (m/s) and heading (degrees) from position history"""
        if self.last_position is None:
            return 0.0, 0.0

        # Calculate distance and time differences
        distance = self._haversine(self.last_position.longitude, self.last_position.latitude, lon, lat)
        time_diff = timestamp - self.last_position.timestamp

        # Calculate speed (m/s)
        speed = distance / time_diff if time_diff > 0 else 0.0

        # Calculate heading (degrees)
        heading = self._calculate_bearing(
            self.last_position.latitude, self.last_position.longitude,
            lat, lon
        )

        return speed, heading

    def _calculate_steering(self, lat: float, lon: float, heading: float,
                            lookahead: GPSPosition) -> float:
        """Calculate steering angle using pure pursuit"""
        # Convert to vehicle coordinate system
        heading_rad = math.radians(heading)
        dx = lookahead.longitude - lon
        dy = lookahead.latitude - lat

        # Transform to vehicle coordinates
        local_x = dx * math.cos(heading_rad) + dy * math.sin(heading_rad)
        local_y = -dx * math.sin(heading_rad) + dy * math.cos(heading_rad)

        # Calculate curvature (1/m)
        curvature = 2 * local_y / (local_x ** 2 + local_y ** 2)

        # Convert to steering angle using bicycle model
        steering_angle = math.atan(curvature * self.wheelbase)

        # Normalize to [-1, 1] range
        return max(-1.0, min(1.0, steering_angle / math.radians(30)))  # 30° max wheel angle

    def _calculate_speed(self, current_heading: float, lookahead: GPSPosition) -> float:
        """Calculate adaptive speed based on path curvature"""
        # Base speed from recorded path
        base_speed = self.path[self.current_index].speed if self.path[self.current_index].speed else 5.0

        # Calculate path heading change
        path_heading = self._calculate_bearing(
            self.path[self.current_index].latitude, self.path[self.current_index].longitude,
            lookahead.latitude, lookahead.longitude
        )
        heading_diff = abs((path_heading - current_heading + 180) % 360 - 180)

        # Reduce speed based on heading difference
        speed_factor = max(0.3, 1.0 - (heading_diff / 90.0))  # 30% minimum speed
        return base_speed * speed_factor

    def _get_lookahead_point(self) -> GPSPosition:
        """Find point ahead on the path"""
        total_dist = 0.0
        lookahead_idx = self.current_index

        while lookahead_idx < len(self.path) - 1 and total_dist < self.lookahead_distance:
            segment_dist = self._haversine(
                self.path[lookahead_idx].longitude, self.path[lookahead_idx].latitude,
                self.path[lookahead_idx + 1].longitude, self.path[lookahead_idx + 1].latitude
            )
            total_dist += segment_dist
            lookahead_idx += 1

        return self.path[lookahead_idx]

    def _update_position(self, lat: float, lon: float, timestamp: float,
                         speed: float, heading: float):
        """Update position tracking"""
        self.last_position = GPSPosition(
            latitude=lat,
            longitude=lon,
            timestamp=timestamp,
            speed=speed,
            heading=heading
        )

        # Update path progress
        closest_dist = float('inf')
        for i in range(max(0, self.current_index - 10),
                       min(len(self.path), self.current_index + 10)):
            dist = self._haversine(
                lon, lat,
                self.path[i].longitude, self.path[i].latitude
            )
            if dist < closest_dist:
                closest_dist = dist
                self.current_index = i

    def _enhance_path(self, path: List[GPSPosition]) -> List[GPSPosition]:
        """Calculate missing headings and speeds in path"""
        enhanced = []
        for i in range(len(path)):
            current = path[i]

            # Calculate heading if missing
            if current.heading is None:
                if i > 0:
                    current.heading = self._calculate_bearing(
                        path[i - 1].latitude, path[i - 1].longitude,
                        current.latitude, current.longitude
                    )
                else:
                    current.heading = 0.0

            # Calculate speed if missing
            if current.speed is None:
                if i > 0 and current.timestamp and path[i - 1].timestamp:
                    dist = self._haversine(
                        path[i - 1].longitude, path[i - 1].latitude,
                        current.longitude, current.latitude
                    )
                    time_diff = current.timestamp - path[i - 1].timestamp
                    current.speed = dist / time_diff if time_diff > 0 else 0.0
                else:
                    current.speed = 0.0

            enhanced.append(current)
        return enhanced

    @staticmethod
    def _haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """Calculate distance between two GPS points in meters"""
        R = 6371000  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (math.sin(delta_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    @staticmethod
    def _calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate initial bearing between two points in degrees"""
        dlon = math.radians(lon2 - lon1)
        y = math.sin(dlon) * math.cos(math.radians(lat2))
        x = (math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) -
             math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(dlon))
        bearing = math.degrees(math.atan2(y, x))
        return (bearing + 360) % 360