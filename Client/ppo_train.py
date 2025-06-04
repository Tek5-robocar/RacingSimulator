import json
import threading

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.base_env import ActionTuple
import numpy as np

from utils import load_config




def mlagent_controller():
    try:
        additional_args = ["--config-path", json_path]
        print(additional_args)
        env = UnityEnvironment(
            # file_name=config.get('unity', 'env_path'),
            # additional_args=additional_args,
            file_name=None,
            base_port=5004,
        )
        env.reset()

        agent = ppo_agent()

        behavior_names = list(env.behavior_specs.keys())
        print(f"Agent behaviors: {behavior_names}")
        try:
            while True:
                for i in range(len(behavior_names)):
                    behavior_name = behavior_names[i]

                    decision_steps, terminal_steps = env.get_steps(behavior_name)
                    if len(decision_steps.obs) == 0:
                        break
                    state = decision_steps.obs[0]
                    reward = decision_steps.reward[0]
                    print(reward)
                    done = len(terminal_steps) > 0
                    if done:
                        print('end episode')

                    chosen_speed, chosen_steer = agent.predict(state)

                    action = ActionTuple()
                    continuous_action = np.array(
                        [[chosen_speed, chosen_steer]],
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
    i = 0
    for agent in json_agent['agents']:
        headers.append([f'raycast_{i}' for i in range(agent['nbRay'])] + ['steering_discrete', 'steering_continuous'])
        i += 1

    print(headers)

    update_thread = threading.Thread(target=mlagent_controller, daemon=True)
    update_thread.start()


if __name__ == "__main__":
    MAX_SPEED = 10
    MAX_STEERING = 10
    STEERING_OFFSET = 7

    config = load_config('config.ini')

    json_path = config.get('DEFAULT', 'json_path')
    with open(json_path) as f:
        json_agent = json.load(f)
    print(json_agent)

    headers = []

    max_value = float(config.getfloat('normalization', 'ray_value_max'))
    min_value = float(config.getfloat('normalization', 'ray_value_min'))

    main()
