import csv
import json
import os
import pickle
import threading

import torch
from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.base_env import ActionTuple
import numpy as np
from pynput import keyboard

from Client.Agent import Agent
from Client.ppo_agent import PPO
from utils import load_config


def ai_controller(rf_model, state):
    float_arr = [(float(elem) - min_value) / (max_value - min_value) for elem in state]
    prediction = rf_model(torch.tensor([float_arr]))
    return 1.0, prediction[0][0].item()


def mlagent_controller():
    try:
        additional_args = ["--config-path", json_path]

        env = UnityEnvironment(
            file_name=os.path.join('..', 'RacingSimulator', 'RL', 'RacingSimulator.x86_64'),
            additional_args=additional_args,
            # file_name=None,
            base_port=5004,
        )
        env.reset()

        behavior_names = list(env.behavior_specs.keys())
        print(f"Agent behaviors: {behavior_names}")

        behavior_names = [(behavior_names[i], 0, 0) for i in range(len(behavior_names))]
        models = []
        for i in range(len(behavior_names)):
            models.append(PPO(obs_dim=json_agent['agents'][i]['nbRay'], act_dim=2))

        try:
            models_train_data = []
            while True:
                for i in range(len(behavior_names)):
                    behavior_name, current_speed, current_steer = behavior_names[i]

                    decision_steps, terminal_steps = env.get_steps(behavior_name)
                    if len(decision_steps.obs) == 0:
                        break
                    state = decision_steps.obs[0]
                    reward = decision_steps.reward[0]
                    if len(models_train_data) <= i:
                        models_train_data.append({
                            'obs': None,
                            'logs_probs': None,
                            'acts': None,
                            'rews': None
                        })
                    else:
                        models_train_data[i]['rews'] = reward
                        print(models_train_data)
                        models[i].learn_step(
                            obs=models_train_data[i]['obs'],
                            logs_probs=models_train_data[i]['logs_probs'],
                            acts=models_train_data[i]['acts'],
                            rews=models_train_data[i]['rews']
                        )
                    done = len(terminal_steps) > 0
                    if done:
                        print('end episode')

                    pred, logs_probs = models[i].get_action(state[0, :json_agent['agents'][i]['nbRay']])
                    models_train_data[i]['obs'] = state[0, :json_agent['agents'][i]['nbRay']]
                    models_train_data[i]['acts'] = pred
                    models_train_data[i]['logs_probs'] = logs_probs
                    print(f'action: {pred}')

                    action = ActionTuple()
                    continuous_action = np.array(
                        [pred],
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
    mlagent_controller()

if __name__ == "__main__":
    config = load_config('config.ini')

    json_path = config.get('DEFAULT', 'json_path')
    with open(json_path) as f:
        json_agent = json.load(f)
    print(json_agent)

    max_value = float(config.getfloat('normalization', 'ray_value_max'))
    min_value = float(config.getfloat('normalization', 'ray_value_min'))

    main()
