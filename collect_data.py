import subprocess

from unity import send_command_to_unity
from pynput import keyboard
import pandas as pd
import time
import threading
import os


# Dictionary to store the values and activation state of keys pressed
key_map = {
    'z': {'value': 0.0, 'activated': 0, 'opposite': 's', 'increase': False},
    'q': {'value': 0.0, 'activated': 0, 'opposite': 'd', 'increase': False},
    's': {'value': 0.0, 'activated': 0, 'opposite': 'z', 'increase': False},
    'd': {'value': 0.0, 'activated': 0, 'opposite': 'q', 'increase': False}
}

# activated 0 // not pressed and free
# activated 1 // pressed and free
# activated 2 // pressed and not usable


offset = 0.05

csv_file = "lidar_data1.csv"
columns = [f"ray_cast_{i}" for i in range(1, 11)]  # Creating column names like lidar_1, lidar_2, ..., lidar_11
columns.append("speed")
columns.append("expected_speed")
columns.append("steering")
columns.append("expected_steering")

def initialize_csv():
    if not os.path.exists(csv_file):
        df = pd.DataFrame(columns=columns)
        df.to_csv(csv_file, mode='w', index=False)

it = 0

def get_value_for_key(key):
    if key_map[key]['activated'] == 1:
        return (key, key_map[key]['value'])
    elif key_map[key_map[key]['opposite']]['activated'] == 1:
        return (key_map[key]['opposite'], -key_map[key_map[key]['opposite']]['value'])
    if key_map[key]['value'] != 0:
        return (key, key_map[key]['value'])
    elif key_map[key_map[key]['opposite']]['value'] != 0:
        return (key_map[key]['opposite'], -key_map[key_map[key]['opposite']]['value'])
    else:
        return (key, key_map[key]['value'])

def get_infos_raycast(speed, expected_speed, steering, expected_steering):
    global it
    x = send_command_to_unity('GET_INFOS_RAYCAST')

    x_splitted = x.split(':')
    # print(x_splitted)
    if x_splitted[0] == 'KO':
        return
    x = [elem[:3] for elem in x_splitted[2:]]
    file_exists = os.path.exists(csv_file)
    file_empty = os.path.getsize(csv_file) == 0 if file_exists else True
    try:
        print(speed, expected_speed, steering, expected_steering)
        x.append(str("{:.3f}".format(speed)))
        x.append(str("{:.3f}".format(expected_speed)))
        x.append(str("{:.3f}".format(steering)))
        x.append(str("{:.3f}".format(expected_steering)))
        lidar_data = pd.DataFrame([x], columns=columns)
        if file_empty:
            lidar_data.to_csv(csv_file, mode='w', header=True, index=False)  # Write with header
        else:
            lidar_data.to_csv(csv_file, mode='a', header=False, index=False)  # Append without header

        it += 1
    except Exception as e:
        os.write(2, f"Error writing to CSV: {str(e)}\n".encode())


# Dictionary to store the start time of each key press
press_times = {}

# Function to handle key press event
def on_press(key):
    try:
        if hasattr(key, 'char') and key.char in key_map:
            if (key_map[key.char]['activated'] == 0 and key_map[key_map[key.char]['opposite']]['activated'] == 0):
                press_times[key.char] = time.time() # Record time when key is pressed
                key_map[key.char]['activated'] = 1  # Mark the key as pressed
                # print(key_map)
                # print(f"Key {key.char} pressed.")
            if (key_map[key.char]['activated'] == 0 and key_map[key_map[key.char]['opposite']]['activated'] == 1):
                press_times[key.char] = time.time() # Record time when key is pressed
                key_map[key.char]['activated'] = 1  # Mark the key as pressed
                key_map[key_map[key.char]['opposite']]['activated'] = 2
                # print(key_map)
                # print(f"Key {key.char} pressed. and opposite {key_map[key.char]['opposite']} is pressed.")
    except Exception as e:
        print(f"Error in on_press: {e}")

# Function to handle key release event
def on_release(key):
    try:
        if hasattr(key, 'char') and key.char in key_map:
            press_time = press_times.pop(key.char, None)
            if press_time and key_map[key.char]['activated'] == 1 or key_map[key.char]['activated'] == 2:
                duration = time.time() - press_time  # Calculate duration
                # print(f"Key {key.char} released. Duration: {duration:.4f} seconds, Value: {key_map[key.char]['value']:.1f}")
                key_map[key.char]['activated'] = 0  # Mark the key as not pressed
                key_map[key.char]['increase'] = False  # Mark the key as not pressed
                # key_map[key.char]['value'] = 0.0  # Reset the key value when released

        # Stop the listener when 'esc' is pressed
        if key == keyboard.Key.esc:
            return False
    except Exception as e:
        print(f"Error in on_release: {e}")

# Function to update key map values periodically
def update_key_values():
    try:
        last_time = time.time()

        while True:
            current_time = time.time()

            for key in key_map:
                if key_map[key]['activated'] == 1:
                    # Update the key's value by increasing it by 0.1 every 10 ms
                    key_map[key]['value'] = key_map[key]['value'] + offset
                    if key_map[key]['value'] > 1:
                        key_map[key]['value'] = 1
                    key_map[key]['increase'] = True
                if key_map[key]['activated'] == 0:
                    key_map[key]['value'] = key_map[key]['value'] - offset * 2
                    if key_map[key]['value'] < 0:
                        key_map[key]['value'] = 0
                    key_map[key]['increase'] = False
                    # if key_map[key]['value'] == 1.0:  # Max value when held for 1 second
                    #     send_command_to_unity(f"SET_{'SPEED' if key in ['z', 's'] else 'STEERING'}:{key_map[key]['value']:.1f}")

            # Periodically send commands to Unity based on key values
            if (key_map['z']['activated'] != 2 and key_map['z']['value'] != 0):
                send_command_to_unity(f"SET_SPEED:{key_map['z']['value']}")
            elif key_map['s']['activated'] != 2 and key_map['s']['value'] != 0:
                send_command_to_unity(f"SET_SPEED:{-key_map['s']['value']}")
            else:
                send_command_to_unity(f"SET_SPEED:0")

            if key_map['d']['activated'] != 2 and key_map['d']['value'] != 0:
                send_command_to_unity(f"SET_STEERING:{key_map['d']['value']}")
            elif key_map['q']['activated'] != 2 and key_map['q']['value'] != 0:
                send_command_to_unity(f"SET_STEERING:{-key_map['q']['value']}")
            else:
                send_command_to_unity(f"SET_STEERING:0")

            speed_input, speed_v = get_value_for_key('z')
            steering_input, steering_v = get_value_for_key('s')

            next_speed = speed_v
            next_steering = steering_v

            if key_map[speed_input]['increase'] == True and speed_v > 0 and speed_v < 1:
                next_speed+=offset
            elif key_map[speed_input]['increase'] == True and speed_v < 0 and speed_v > -1:
                next_speed-=offset * 2
            if key_map[steering_input]['increase'] == True and steering_v > 0 and steering_v < 1:
                next_steering+=offset
            elif key_map[steering_input]['increase'] == True and steering_v < 0 and steering_v > -1:
                next_steering-=offset * 2

            # if speed_v != next_speed or steering_v != next_steering:
            get_infos_raycast(key_map['z']['value'], key_map['s']['value'], key_map['q']['value'], key_map['d']['value'])

            if current_time - last_time >= 20:  # Check if 20 seconds have passed
                last_time = current_time
                send_command_to_unity(f"SET_RANDOM_POSITION")
                for key, data in key_map.items():
                    for sub_key, sub_value in data.items():
                        if sub_key == 'value':
                            data[sub_key] = 0  # Update the value directly in the dictionary
                time.sleep(1)

            time.sleep(0.01)  # Wait for 10ms before updating again

    except KeyboardInterrupt:
        print("Stopped.")

# Main function to start the listener
def start_listener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


UNITY_BUILD_PATH = os.path.join(os.getcwd(), '..', 'unity-simulator', 'UnityBuild2', 'RacingSimulator.x86_64')

# Start the program
if __name__ == "__main__":
    print("Press keys (z, q, s, d). Press 'Esc' to exit.")
    unity_process = subprocess.Popen([UNITY_BUILD_PATH])
    time.sleep(5)

    # Start a background thread to periodically update key map values
    update_thread = threading.Thread(target=update_key_values, daemon=True)
    update_thread.start()

    # Start the listener
    start_listener()

    # Print out the key map when you stop the program
    print("\nFinal key map values:")
    for key, value in key_map.items():
        print(f"Key {key}: {value['value']:.1f}")

    send_command_to_unity("END_SIMULATION")
    if unity_process:
        unity_process.terminate()
