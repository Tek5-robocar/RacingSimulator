import os
import subprocess
import time

import numpy as np

from Agent import Agent
from unity import send_command_to_unity
from utils import load_config

def loop(agent: Agent):
    for i in range(300):
        print('--------')
        result = send_command_to_unity("GET_INFOS_RAYCAST;GET_SPEED;GET_STEERING")
        result_splitted = result.split(';')
        if len(result_splitted) != 3:
            continue
        raycast = result_splitted[0]
        speed = result_splitted[1]
        steering = result_splitted[2]
        splitted_raycast = raycast.split(':')
        splitted_speed = speed.split(':')
        splitted_steering = steering.split(':')
        if len(splitted_raycast) != 12 or splitted_raycast[0] != 'OK' or splitted_raycast[
            1] != 'GET_INFOS_RAYCAST' or len(splitted_speed) != 3 or len(splitted_steering) != 3 or splitted_speed[
            1] != 'GET_SPEED' or splitted_steering[1] != 'GET_STEERING':
            continue
        float_arr = [float(elem) for elem in splitted_raycast[2:]]
        float_arr.append(float(splitted_speed[2]))
        float_arr.append(float(splitted_steering[2]))
        float_arr = np.array([(float_arr[i] - agent.extremum[i][0]) / (agent.extremum[i][1] - agent.extremum[i][0]) for i in range(len(float_arr))])
        # float_arr = np.array([sum(float_arr[:4])/4, sum(float_arr[4:6])/2, sum(float_arr[6:10])/4, float_arr[10]])
        # float_arr = np.array([sum(float_arr[:4])/4, sum(float_arr[4:6])/2, sum(float_arr[6:10])/4, float_arr[10], float_arr[11]])
        print(float_arr.shape)
        float_arr = float_arr[list(range(10)) + [11]]
        print(float_arr)
        prediction = agent.predict(np.array(float_arr))
        print(prediction[0])
        send_command_to_unity(f"SET_SPEED:{0.5};SET_STEERING:{prediction[0]}")
        print('--------')


def main():
    unity_process = subprocess.Popen([config.get('unity', 'env_path')])
    time.sleep(5)

    agent = Agent(config, 'cuda')

    try:
        for _ in range(5):
            loop(agent)
            send_command_to_unity("SET_RANDOM_POSITION")
    except Exception as e:
        print(e)

    send_command_to_unity("END_SIMULATION")
    if unity_process:
        unity_process.terminate()


if __name__ == '__main__':
    config = load_config('config.ini')
    main()
