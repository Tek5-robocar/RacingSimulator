import csv
import json
import math
import os
import threading
import time

import torch
import tkinter as tk
from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.base_env import ActionTuple
import numpy as np
from pynput import keyboard

from Agent import Agent
from LapRecorder import LapRecorder
from PathFollower import PathFollower
# from XYLivePlot import LiveXYPlotApp
from utils import load_config


def on_press(key):
    try:
        if hasattr(key, 'char') and key.char in keys.keys():
            keys[key.char] = True
            if key.char == 'z':
                keys['s'] = False
            if key.char == 's':
                keys['z'] = False
            if key.char == 'q':
                keys['d'] = False
            if key.char == 'd':
                keys['q'] = False
    except Exception as e:
        print(f"Error in on_press: {e}")


def on_release(key):
    try:
        if hasattr(key, 'char') and key.char in keys.keys():
            keys[key.char] = False
    except Exception as e:
        print(f"Error in on_release: {e}")


def keyboard_controller(current_speed, current_steer):
    if keys['z']:
        current_speed = MAX_SPEED
    elif keys['s']:
        current_speed = -MAX_SPEED
    else:
        current_speed -= 1 if current_speed > 0 else 0

    if keys['q']:
        current_steer -= STEERING_OFFSET if current_steer > -MAX_STEERING else -MAX_STEERING
    elif keys['d']:
        current_steer += STEERING_OFFSET if current_steer < MAX_STEERING else MAX_STEERING
    else:
        current_steer = 0
    return current_speed, current_steer


def get_numeric_steering(prediction: str) -> float:
    steering = sum(steering_map[prediction[0]]) / 2
    return steering


def append_to_csv(row, file_path, header):
    file_exists = os.path.isfile(file_path) and os.path.getsize(file_path) > 0

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(row)


# def mlagent_controller(app):
def mlagent_controller():
    try:
        additional_args = ["--config-path", json_path]
        print(additional_args)
        env = UnityEnvironment(
            file_name=config.get('unity', 'env_path'),
            additional_args=additional_args,
            # file_name=None,
            base_port=5004,
        )
        print('before reset')
        env.reset()
        print('after reset')

        first_lap_done = False
        recorder = LapRecorder()
        recorder.start_recording()
        follower = None

        behavior_names = list(env.behavior_specs.keys())
        print(f"Agent behaviors: {behavior_names}")
        behavior_names = [(behavior_names[i], 0, 0, keyboard_agent[i]) for i in range(len(behavior_names))]
        my_agent = Agent('model_car.pth', min_value, max_value)
        try:
            while True:
                for i in range(len(behavior_names)):
                    behavior_name, current_speed, current_steer, is_keyboard = behavior_names[i]

                    decision_steps, terminal_steps = env.get_steps(behavior_name)
                    if len(decision_steps.obs) == 0:
                        break
                    state = decision_steps.obs[0]
                    # x_y = (state[0][-3], state[0][-1])

                    if not first_lap_done:
                        recorder.add_position(
                            lat=state[0][-3],
                            lon=state[0][-1],
                            timestamp=time.time() + i,
                            speed=state[0][-4],
                        )
                        # app.update_from_external_data(state[0][-3], state[0][-1])

                    reward = decision_steps.reward[0]
                    done = len(terminal_steps) > 0
                    if done:
                        first_lap_done = True
                        recorder.stop_recording()
                        follower = PathFollower(recorder.recorded_positions)
                        print('end episode')
                    if is_keyboard:
                        if first_lap_done and follower is not None:
                            speed, steering = follower.get_commands(state[0][-3], state[0][-1])
                            print(speed, steering)
                        else:
                            current_speed, current_steer = keyboard_controller(current_speed, current_steer)
                            for steering in steering_map:
                                if steering_map[steering][0] * 10 <= current_steer <= steering_map[steering][1] * 10:
                                    append_to_csv(
                                        [str(nb) for nb in state[0][:json_agent['agents'][i]['nbRay']]] + [steering] + [
                                            str(current_steer / 10)], file_paths[i], headers[i])
                                    break
                    else:
                        current_speed = 1.0
                        current_steer = my_agent.act(torch.tensor(state[0, :10]))
                        current_steer = current_steer * 2 - 1
                        current_speed *= 10
                        current_steer *= 10

                    action = ActionTuple()
                    continuous_action = np.array(
                        [[current_speed / 10, current_steer / 10]],
                        dtype=np.float32
                    )

                    decision_steps, _ = env.get_steps(behavior_name)
                    num_agents = len(decision_steps.agent_id)
                    batch_action = ActionTuple()
                    batch_action.add_continuous(np.repeat(continuous_action, num_agents, axis=0))
                    env.set_actions(behavior_name, batch_action)
                env.step()

        except KeyboardInterrupt:
            print("Interrupted by user")
    except Exception as e:
        print(f"Error: {str(e)}")
        print(e.with_traceback())
    finally:
        if 'env' in locals():
            env.close()
        print("Connection closed")


def main():
    # root = tk.Tk()
    # app = LiveXYPlotApp(root)
    update_thread = threading.Thread(target=mlagent_controller, daemon=True)
    # update_thread = threading.Thread(target=mlagent_controller, args=(app,), daemon=True)
    update_thread.start()

    keyboard_thread = threading.Thread(
        target=lambda: keyboard.Listener(on_press=on_press, on_release=on_release).start(),
        daemon=True
    )
    keyboard_thread.start()

    # root.mainloop()



if __name__ == "__main__":
    steering_map = {
        "left_19": (-1.0, -0.95),
        "left_18": (-0.95, -0.9),
        "left_17": (-0.9, -0.85),
        "left_16": (-0.85, -0.8),
        "left_15": (-0.8, -0.75),
        "left_14": (-0.75, -0.7),
        "left_13": (-0.7, -0.65),
        "left_12": (-0.65, -0.6),
        "left_11": (-0.6, -0.55),
        "left_10": (-0.55, -0.5),
        "left_9": (-0.5, -0.45),
        "left_8": (-0.45, -0.4),
        "left_7": (-0.4, -0.35),
        "left_6": (-0.35, -0.3),
        "left_5": (-0.3, -0.25),
        "left_4": (-0.25, -0.2),
        "left_3": (-0.2, -0.15),
        "left_2": (-0.15, -0.1),
        "left_1": (-0.1, -0.05),
        "center": (-0.05, 0.05),
        "right_1": (0.05, 0.1),
        "right_2": (0.1, 0.15),
        "right_3": (0.15, 0.2),
        "right_4": (0.2, 0.25),
        "right_5": (0.25, 0.3),
        "right_6": (0.3, 0.35),
        "right_7": (0.35, 0.4),
        "right_8": (0.4, 0.45),
        "right_9": (0.45, 0.5),
        "right_10": (0.5, 0.55),
        "right_11": (0.55, 0.6),
        "right_12": (0.6, 0.65),
        "right_13": (0.65, 0.7),
        "right_14": (0.7, 0.75),
        "right_15": (0.75, 0.8),
        "right_16": (0.8, 0.85),
        "right_17": (0.85, 0.9),
        "right_18": (0.9, 0.95),
        "right_19": (0.95, 1.0)
    }

    keys = {
        'z': False,
        'q': False,
        's': False,
        'd': False
    }

    MAX_SPEED = 10
    MAX_STEERING = 10
    STEERING_OFFSET = 7

    keyboard_agent = [True]
    config = load_config('config.ini')

    json_path = config.get('DEFAULT', 'json_path')
    with open(json_path) as f:
        json_agent = json.load(f)
    print(json_agent)

    headers = []
    file_paths = []
    i = 0
    for agent in json_agent['agents']:
        headers.append([f'raycast_{i}' for i in range(agent['nbRay'])] + ['steering_discrete', 'steering_continuous'])
        file_paths.append(config.get('DEFAULT', 'csv_path').replace('.csv', f'_fov{agent["fov"]}_{i}.csv'))
        i += 1

    print(headers)
    print(file_paths)

    max_value = float(config.getfloat('normalization', 'ray_value_max'))
    min_value = float(config.getfloat('normalization', 'ray_value_min'))

    main()
