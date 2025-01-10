import os
import subprocess
import time

import numpy as np

from Agent import Agent
from unity import send_command_to_unity
from utils import load_config

UNITY_BUILD_PATH = os.path.join(os.getcwd(), '..', 'unity-simulator', 'UnityBuild', 'RacingSimulator.x86_64')


def loop(agent: Agent):
    for i in range(100):
        result = send_command_to_unity("GET_INFOS_RAYCAST;GET_SPEED;GET_STEERING")
        result_splitted = result.split(';')
        print(result_splitted)
        if len(result_splitted) != 3:
            continue
        raycast = result_splitted[0]
        speed = result_splitted[1]
        steering = result_splitted[2]
        splitted_raycast = raycast.split(':')
        splitted_speed = speed.split(':')
        splitted_steering = steering.split(':')
        print(splitted_raycast, splitted_speed, splitted_steering)
        if len(splitted_raycast) != 12 or splitted_raycast[0] != 'OK' or splitted_raycast[
            1] != 'GET_INFOS_RAYCAST' or len(splitted_speed) != 3 or len(splitted_steering) != 3 or splitted_speed[
            1] != 'GET_SPEED' or splitted_steering[1] != 'GET_STEERING':
            continue
        float_arr = [float(elem) for elem in splitted_raycast[2:]]
        float_arr.append(float(splitted_speed[2]))
        float_arr.append(float(splitted_steering[2]))
        print(float_arr)
        prediction = agent.predict(np.array(float_arr))
        send_command_to_unity(f"SET_SPEED:{prediction[0]};SET_STEERING:{prediction[1]}")
        print(prediction)


def main():
    unity_process = subprocess.Popen([UNITY_BUILD_PATH])
    time.sleep(5)

    agent = Agent(config, 'cuda')

    try:
        loop(agent)
    except:
        pass

    send_command_to_unity("END_SIMULATION")
    if unity_process:
        unity_process.terminate()


if __name__ == '__main__':
    config = load_config('config.ini')
    main()
