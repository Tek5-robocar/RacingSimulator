import math
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class GPSPosition:
    latitude: float
    longitude: float
    timestamp: float
    speed: float
    heading: Optional[float] = None  # Now optional


class LapRecorder:
    def __init__(self):
        self.recorded_positions: List[GPSPosition] = []
        self.is_recording = False
        self._last_position = None

    def add_position(self, lat: float, lon: float,
                     timestamp: float, speed: float):
        if not self.is_recording:
            return

        # Calculate heading from previous point if available
        heading = self._calculate_heading(lat, lon) if self._last_position else 0.0

        new_pos = GPSPosition(
            latitude=lat,
            longitude=lon,
            timestamp=timestamp,
            speed=speed,
            heading=heading
        )

        self.recorded_positions.append(new_pos)
        self._last_position = new_pos

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
        print("Started recording lap...")

    def stop_recording(self):
        self.is_recording = False
        print(f"Stopped recording. Captured {len(self.recorded_positions)} positions.")
