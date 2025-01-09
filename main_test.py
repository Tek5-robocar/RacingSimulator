import unittest
import os
import subprocess
from time import sleep

from unity import send_command_to_unity

UNITY_BUILD_PATH = os.path.join(os.getcwd(), 'UnityBuild', 'RacingSimulator.x86_64')


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

    def test_set_positive_speed(self):
        response = send_command_to_unity("SET_SPEED:0.71")
        self.assertEqual(response, "OK:SET_SPEED")
        send_command_to_unity("SET_SPEED:0")

    def test_set_negative_speed(self):
        response = send_command_to_unity("SET_SPEED:-0.71")
        self.assertEqual(response, "OK:SET_SPEED")
        send_command_to_unity("SET_SPEED:0")

    def test_set_high_speed(self):
        response = send_command_to_unity("SET_SPEED:1.32")
        self.assertEqual(response, "KO:SET_SPEED")

    def test_set_low_speed(self):
        response = send_command_to_unity("SET_SPEED:-1.01")
        self.assertEqual(response, "KO:SET_SPEED")

    def test_set_positive_steering(self):
        response = send_command_to_unity("SET_STEERING:0.3")
        self.assertEqual(response, "OK:SET_STEERING")
        send_command_to_unity("SET_STEERING:0")

    def test_set_negative_steering(self):
        response = send_command_to_unity("SET_STEERING:-0.3")
        self.assertEqual(response, "OK:SET_STEERING")
        send_command_to_unity("SET_STEERING:0")

    def test_set_high_steering(self):
        response = send_command_to_unity("SET_STEERING:10")
        self.assertEqual(response, "KO:SET_STEERING")

    def test_set_low_steering(self):
        response = send_command_to_unity("SET_STEERING:-2")
        self.assertEqual(response, "KO:SET_STEERING")

    def test_set_speed_steering(self):
        response = send_command_to_unity("SET_SPEED:-0.71;SET_STEERING:0.3")
        self.assertEqual(response, "OK:SET_SPEED;OK:SET_STEERING")
        send_command_to_unity("SET_STEERING:0")
        send_command_to_unity("SET_SPEED:0")

    def test_get_speed_set_speed_steering(self):
        response = send_command_to_unity("GET_SPEED;SET_SPEED:-0.71;SET_STEERING:0.3")
        self.assertEqual(response, "OK:GET_SPEED:0.00;OK:SET_SPEED;OK:SET_STEERING")
        send_command_to_unity("SET_STEERING:0")
        send_command_to_unity("SET_SPEED:0")

    def test_set_high_speed_steering_get_infos_raycast(self):
        response = send_command_to_unity("SET_SPEED:1.71;SET_STEERING:0.3;GET_INFOS_RAYCAST")
        self.assertEqual(response, "KO:SET_SPEED;OK:SET_STEERING;OK:GET_INFOS_RAYCAST:174.00:185.00:227.00:163.00:164.00:160.00:168.00:227.00:185.00:174.00")
        send_command_to_unity("SET_STEERING:0")

    def test_get_speed(self):
        response = send_command_to_unity("GET_SPEED")
        self.assertEqual(response, "OK:GET_SPEED:0.00")

    def test_get_steering(self):
        response = send_command_to_unity("GET_STEERING")
        self.assertEqual(response, "OK:GET_STEERING:0.00")

    def test_get_infos_raycast(self):
        response = send_command_to_unity("GET_INFOS_RAYCAST")
        self.assertEqual(response,"OK:GET_INFOS_RAYCAST:174.00:185.00:227.00:163.00:164.00:160.00:168.00:227.00:185.00:174.00")

    def test_get_position(self):
        response = send_command_to_unity("GET_POSITION")
        self.assertEqual(response, "OK:GET_POSITION:0.00:0.00:13.44")

    def test_set_random_position(self):
        response = send_command_to_unity("SET_RANDOM_POSITION")
        self.assertTrue(response.startswith("OK:SET_RANDOM_POSITION:"))


if __name__ == '__main__':
    unittest.main()
