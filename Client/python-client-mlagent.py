import socket
import threading

from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.base_env import ActionTuple
import numpy as np
from pynput import keyboard

from mlagents_envs.side_channel.engine_configuration_channel import EngineConfigurationChannel


def start_agents(host='127.0.0.1', port=12345):
    """Connect to TCP server and retrieve worker ID"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.send(bytes("NB_AGENT:2;FOV:155;NB_RAY:20", 'utf-8'))


def on_press(key):
    global current_speed
    global current_steer
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


def update_key_values():
    global current_speed
    global current_steer
    TCP_HOST = '0.0.0.0'
    TCP_PORT = 8085
    try:
        engine_config_channel = EngineConfigurationChannel()
        start_agents(TCP_HOST, TCP_PORT)
        env = UnityEnvironment(
            file_name=None,
            side_channels=[engine_config_channel],
            base_port=5004,
        )
        env.reset()

        # Get all behavior names (e.g., ['Agent0?team=0', 'Agent1?team=0'])
        behavior_names = list(env.behavior_specs.keys())
        print(f"Agent behaviors: {behavior_names}")

        try:
            while True:
                # Generate action based on keyboard input
                if keys['z']:
                    current_speed = max_speed
                elif keys['s']:
                    current_speed = 0
                else:
                    current_speed -= 1 if current_speed > 0 else 0

                if keys['q']:
                    current_steer -= 1 if current_steer > -max_steering else 0
                elif keys['d']:
                    current_steer += 1 if current_steer < max_steering else 0
                else:
                    current_steer = 0  # Reset steering when no key is pressed

                # Create the action tuple
                action = ActionTuple()
                continuous_action = np.array(
                    [[current_speed / 10, current_steer / 10]],
                    dtype=np.float32
                )
                action.add_continuous(continuous_action)

                # Send action to ALL agents across all behaviors
                for behavior_name in behavior_names:
                    # Get number of agents in this behavior group
                    decision_steps, _ = env.get_steps(behavior_name)
                    num_agents = len(decision_steps.agent_id)

                    # Repeat the action for all agents in this group
                    batch_action = ActionTuple()
                    batch_action.add_continuous(np.repeat(continuous_action, num_agents, axis=0))

                    env.set_actions(behavior_name, batch_action)

                env.step()

        except KeyboardInterrupt:
            print("Interrupted by user")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'env' in locals():
            env.close()
        print("Connection closed")

def main():
    update_thread = threading.Thread(target=update_key_values, daemon=True)
    update_thread.start()
    print("Connected to ML-Agents environment. Press:")
    print("- W to accelerate")
    print("- A/D to steer left/right")
    print("- ESC to exit")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


if __name__ == "__main__":
    keys = {
        'z': False,
        'q': False,
        's': False,
        'd': False
    }

    max_speed = 10
    max_steering = 10
    current_speed = 0.0
    current_steer = 0.0
    main()
