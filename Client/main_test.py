import unittest
import subprocess

from time import sleep
from unity import send_command_to_unity
from utils import load_config


class TestUnityCommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = load_config('config.ini')
        cls.unity_process = subprocess.Popen([config.get('unity', 'env_path')])
        sleep(5)

    @classmethod
    def tearDownClass(cls):
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
        self.assertEqual(response, "KO:SET_SPEED;OK:SET_STEERING;OK:GET_INFOS_RAYCAST:184.00:169.00:162.00:161.00:165.00:164.00:154.00:152.00:155.00:165.00")
        send_command_to_unity("SET_STEERING:0")

    def test_get_speed(self):
        response = send_command_to_unity("GET_SPEED")
        self.assertEqual(response, "OK:GET_SPEED:0.00")

    def test_get_steering(self):
        response = send_command_to_unity("GET_STEERING")
        self.assertEqual(response, "OK:GET_STEERING:0.00")

    def test_get_infos_raycast(self):
        response = send_command_to_unity("GET_INFOS_RAYCAST")
        self.assertEqual(response,"OK:GET_INFOS_RAYCAST:184.00:169.00:162.00:161.00:165.00:164.00:154.00:152.00:155.00:165.00")

    def test_get_position(self):
        response = send_command_to_unity("GET_POSITION")
        self.assertEqual(response, "OK:GET_POSITION:0.00:0.00:13.44")

    def test_set_random_position(self):
        response = send_command_to_unity("SET_RANDOM_POSITION")
        self.assertTrue(response.startswith("OK:SET_RANDOM_POSITION:"))


if __name__ == '__main__':
    unittest.main()
