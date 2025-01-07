import unittest
import os
import subprocess
from time import sleep

from unity import send_command_to_unity

UNITY_BUILD_PATH = os.path.join(os.getcwd(), '..', 'unity-simulator', 'UnityBuild', 'RacingSimulator.x86_64')


class TestUnityCommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Start the Unity simulation before tests."""
        cls.unity_process = subprocess.Popen([UNITY_BUILD_PATH])
        sleep(5)

    @classmethod
    def tearDownClass(cls):
        """Terminate the Unity simulation after tests."""
        send_command_to_unity("END_SIMULATION")
        if cls.unity_process:
            cls.unity_process.terminate()

    def test_set_speed(self):
        response = send_command_to_unity("SET_SPEED:0")
        self.assertEqual(response, "OK")

    def test_set_steering(self):
        response = send_command_to_unity("SET_STEERING:0")
        self.assertEqual(response, "OK")

    def test_get_speed(self):
        response = send_command_to_unity("GET_SPEED")
        self.assertEqual(response, "OK:0.00")

    def test_get_steering(self):
        response = send_command_to_unity("GET_STEERING")
        self.assertEqual(response, "OK:0.00")

    def test_get_infos_raycast(self):
        response = send_command_to_unity("GET_INFOS_RAYCAST")
        self.assertEqual(response, "OK:174.00:185.00:227.00:163.00:164.00:160.00:168.00:227.00:185.00:174.00")

    def test_get_position(self):
        response = send_command_to_unity("GET_POSITION")
        self.assertEqual(response, "OK:0.00:0.00:13.44")

    def test_get_max_speed(self):
        response = send_command_to_unity("GET_MAX_SPEED")
        self.assertEqual(response, "OK:100.00")

    def test_get_min_speed(self):
        response = send_command_to_unity("GET_MIN_SPEED")
        self.assertEqual(response, "OK:-100.00")

    def test_set_random_position(self):
        response = send_command_to_unity("SET_RANDOM_POSITION")
        self.assertTrue(response.startswith("OK:"))  # Accept dynamic responses


if __name__ == '__main__':
    unittest.main()
