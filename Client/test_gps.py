import time
import math
from typing import List, Tuple
import numpy as np
import matplotlib.pyplot as plt

from LapRecorder import GPSPosition


class VehicleController:
    """Simulates vehicle control interface"""

    def __init__(self):
        self.current_speed = 0.0
        self.current_steering = 0.0

    def send_commands(self, speed: float, steering: float):
        """Send speed (m/s) and steering angle (-1 to 1 where 0 is straight)"""
        self.current_speed = speed
        self.current_steering = steering
        print(f"Vehicle command: Speed={speed:.2f} m/s, Steering={steering:.2f}")


class PathFollower:
    def __init__(self, recorded_positions: List[GPSPosition]):
        self.path = recorded_positions
        self.current_index = 0
        self.last_error = 0
        self.integral = 0

    def calculate_steering(self, current_pos: GPSPosition) -> float:
        """Calculate steering angle using pure pursuit algorithm"""
        if self.current_index >= len(self.path) - 1:
            return 0.0

        # Find lookahead point (simplified - just use next point)
        lookahead_idx = min(self.current_index + 5, len(self.path) - 1)
        lookahead_point = self.path[lookahead_idx]

        # Convert to local vehicle coordinates
        dx = lookahead_point.longitude - current_pos.longitude
        dy = lookahead_point.latitude - current_pos.latitude

        # Transform to vehicle coordinate system
        heading_rad = math.radians(current_pos.heading)
        local_x = dx * math.cos(heading_rad) + dy * math.sin(heading_rad)
        local_y = -dx * math.sin(heading_rad) + dy * math.cos(heading_rad)

        # Calculate curvature (simplified)
        curvature = 2 * local_y / (local_x ** 2 + local_y ** 2)

        # Convert curvature to steering angle (-1 to 1)
        steering = np.clip(curvature * 0.5, -1.0, 1.0)
        return steering

    def calculate_speed(self, current_pos: GPSPosition) -> float:
        """Calculate target speed based on path curvature"""
        if self.current_index >= len(self.path):
            return 0.0

        # Base speed on recorded speed with some lookahead
        target_speed = self.path[self.current_index].speed

        # Reduce speed based on upcoming curvature
        lookahead_idx = min(self.current_index + 10, len(self.path) - 1)
        angle_diff = abs(self.path[lookahead_idx].heading - current_pos.heading)
        angle_diff = min(angle_diff, 360 - angle_diff)  # Handle wrap-around

        # Reduce speed for sharp turns
        if angle_diff > 30:
            target_speed *= 0.6
        elif angle_diff > 15:
            target_speed *= 0.8

        return target_speed

    def get_next_commands(self, current_pos: GPSPosition) -> Tuple[float, float]:
        """Get speed and steering commands for current position"""
        steering = self.calculate_steering(current_pos)
        speed = self.calculate_speed(current_pos)

        # Update path progress
        if self.current_index < len(self.path) - 1:
            next_point = self.path[self.current_index]
            distance = haversine(
                current_pos.longitude, current_pos.latitude,
                next_point.longitude, next_point.latitude
            )
            if distance < 2.0:  # Move to next point when close
                self.current_index += 1

        return speed, steering

    def reset(self):
        self.current_index = 0
        self.last_error = 0
        self.integral = 0


def haversine(lon1, lat1, lon2, lat2):
    """Calculate distance between two GPS points in meters"""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def simulate_gps_track(num_points=100):
    """Generate a realistic race track with straightaways and curves"""
    positions = []
    center_lat, center_lon = 48.8566, 2.3522

    for i in range(num_points):
        angle = 2 * math.pi * i / num_points

        # Create a more interesting track shape
        lat_scale = 0.01 + 0.005 * math.sin(angle * 2)
        lon_scale = 0.005 + 0.002 * math.cos(angle * 3)

        lat_offset = lat_scale * math.sin(angle)
        lon_offset = lon_scale * math.cos(angle)

        # Calculate derivatives for heading
        dx = -lat_scale * math.sin(angle) + lon_scale * math.cos(angle)
        dy = lat_scale * math.cos(angle) + lon_scale * math.sin(angle)
        heading = math.degrees(math.atan2(dy, dx)) % 360

        # Vary speed based on track curvature
        base_speed = 10  # m/s
        speed_variation = 5 * (1 - abs(math.sin(angle * 2)))
        speed = base_speed + speed_variation

        positions.append(GPSPosition(
            latitude=center_lat + lat_offset,
            longitude=center_lon + lon_offset,
            timestamp=time.time() + i,
            speed=speed,
            heading=heading
        ))

    return positions


def plot_path_with_commands(positions, commands):
    """Plot the path with speed and steering commands"""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))

    # Plot path
    lats = [p.latitude for p in positions]
    lons = [p.longitude for p in positions]
    ax1.plot(lons, lats, 'b-')
    ax1.set_title('Track Path')
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.grid()

    # Plot speed commands
    speeds = [c[0] for c in commands]
    ax2.plot(speeds, 'g-')
    ax2.set_title('Speed Commands')
    ax2.set_xlabel('Frame')
    ax2.set_ylabel('Speed (m/s)')
    ax2.grid()

    # Plot steering commands
    steerings = [c[1] for c in commands]
    ax3.plot(steerings, 'r-')
    ax3.set_title('Steering Commands')
    ax3.set_xlabel('Frame')
    ax3.set_ylabel('Steering (-1 to 1)')
    ax3.grid()

    plt.tight_layout()
    plt.show()


def main():
    # Simulate recording a lap
    recorder = LapRecorder()
    recorder.start_recording()

    simulated_positions = simulate_gps_track()
    for pos in simulated_positions:
        recorder.add_position(pos)

    recorder.stop_recording()

    # Create path follower and vehicle controller
    follower = PathFollower(recorder.recorded_positions)
    vehicle = VehicleController()

    # Simulate replaying the lap
    print("\nStarting autonomous lap replay...")
    commands = []

    # Start at first recorded position
    current_pos = recorder.recorded_positions[0]

    for _ in range(len(recorder.recorded_positions) * 2):  # Allow extra time
        # Get control commands
        speed, steering = follower.get_next_commands(current_pos)
        commands.append((speed, steering))

        # Send to vehicle
        vehicle.send_commands(speed, steering)

        # Simulate vehicle movement (in reality this would come from GPS)
        if follower.current_index < len(recorder.recorded_positions):
            current_pos = recorder.recorded_positions[follower.current_index]

        time.sleep(0.1)  # Simulate control loop timing

        if follower.current_index >= len(recorder.recorded_positions) - 1:
            print("Lap completed!")
            break

    # Visualize results
    plot_path_with_commands(recorder.recorded_positions, commands)