import math
import time
from dataclasses import dataclass
from typing import List, Optional

from matplotlib import pyplot as plt


@dataclass
class GPSPosition:
    latitude: float
    longitude: float
    timestamp: float
    heading: Optional[float] = None  # Now optional


class LapRecorder:
    def __init__(self):
        self.recorded_positions: List[GPSPosition] = []
        self.is_recording = False
        self._last_position = None
        self._heading_diff_associated_steering = []

    def add_position(self, lat: float, lon: float, chosen_steering: float):
        if not self.is_recording:
            return

        lat = round(lat, 1)
        lon = round(lon, 1)

        # Calculate heading from previous point if available
        heading = self._calculate_heading(lat, lon) if self._last_position else 0.0
        # heading = self._calculate_heading_diff(lat, lon)
        if self._last_position is not None:
            heading_diff = heading - self._last_position.heading
            print(f'heading diff: {heading_diff} for steering: {chosen_steering}')
            if round(heading_diff, 0) != 0.0:
                self._heading_diff_associated_steering.append((heading_diff, chosen_steering))
        new_pos = GPSPosition(
            latitude=lat,
            longitude=lon,
            timestamp=time.time(),
            heading=heading
        )

        self.recorded_positions.append(new_pos)
        self._last_position = new_pos

    def predict(self, lat: float, lon: float):
        if self.is_recording:
            return

        lat = round(lat, 1)
        lon = round(lon, 1)

        # Calculate heading from previous point if available
        heading = self._calculate_heading(lat, lon) if self._last_position else 0.0
        # heading = self._calculate_heading_diff(lat, lon)
        if self._last_position is not None:
            heading_diff = heading - self._last_position.heading
            print(f'heading diff: {heading_diff} for steering: {chosen_steering}')
            if round(heading_diff, 0) != 0.0:
                self._heading_diff_associated_steering.append((heading_diff, chosen_steering))
        new_pos = GPSPosition(
            latitude=lat,
            longitude=lon,
            timestamp=time.time(),
            heading=heading
        )

        self.recorded_positions.append(new_pos)
        self._last_position = new_pos

    # def _calculate_heading_diff(self, new_lat: float, new_lon: float) -> float:
    #     if not self._last_position:
    #         return 0.0
    #
    #     new = (new_lat, new_lon)
    #     old = (self._last_position.latitude, self._last_position.longitude)
    #     print(f'new : {new}, old: {old}')
        # hyp = math.sqrt((new[0] - old[0]) ** 2 + (new[1] - old[1]) ** 2)
        # adj = new[0] - old[0]
        # return math.acos(adj / hyp) - self._last_position.heading

    def _calculate_heading(self, new_lat: float, new_lon: float) -> float:
        """Calculate heading from last position to new position in degrees"""
        if not self._last_position:
            return 0.0

        # Convert to radians
        lat1 = math.radians(self._last_position.latitude)
        lon1 = math.radians(self._last_position.longitude)
        lat2 = math.radians(new_lat)
        lon2 = math.radians(new_lon)

        # Calculate bearing
        dlon = lon2 - lon1
        x = math.sin(dlon) * math.cos(lat2)
        y = (math.cos(lat1) * math.sin(lat2) -
             math.sin(lat1) * math.cos(lat2) * math.cos(dlon))

        bearing = math.degrees(math.atan2(x, y))
        return (bearing + 360) % 360  # Normalize to 0-359

    def start_recording(self):
        self.recorded_positions = []
        self.is_recording = True
        print("Recording started - driving data will be captured")

    def stop_recording(self):
        self.is_recording = False
        print(f"Recording stopped - captured {len(self.recorded_positions)} points")
        print(f'average steering for 1° diff: {sum([x[0]/x[1] if round(x[1], 0) != 0 else 0.0 for x in self._heading_diff_associated_steering])/len(self._heading_diff_associated_steering)}')
        plt.plot([position.latitude for position in self.recorded_positions], [position.longitude for position in self.recorded_positions])
        plt.show()

    def get_recording_positions(self):
        return self.recorded_positions
