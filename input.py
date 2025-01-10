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


csv_file = "lidar_data.csv"
columns = [f"lidar_{i}" for i in range(1, 11)]  # Creating column names like lidar_1, lidar_2, ..., lidar_11
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
    return (key_map[key]['opposite'], -key_map[key_map[key]['opposite']]['value'])

def get_infos_raycast(speed, expected_speed, steering, expected_steering):
    global it
    x = send_command_to_unity('GET_INFOS_RAYCAST')
    x_splitted = x.split(':')
    # print(x_splitted)
    if x_splitted[0] == 'KO':
        return
    x = [elem[:3] for elem in x_splitted[2:]]
    # print(x)
    try:
        x.append(str(speed)[:3])
        x.append(str(expected_speed)[:3])
        x.append(str(steering)[:3])
        x.append(str(expected_steering)[:3])
        # print(x)
        lidar_data = pd.DataFrame([x], columns=columns)
        if not os.path.exists(csv_file) and it == 0:
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
                key_map[key.char]['value'] = 0.0  # Reset the key value when released

                # Send stop commands to Unity based on the key
                if key.char == 'z':
                    send_command_to_unity(f"SET_SPEED:0")
                if key.char == 's':
                    send_command_to_unity(f"SET_SPEED:0")
                if key.char == 'd':
                    send_command_to_unity(f"SET_STEERING:0")
                if key.char == 'q':
                    send_command_to_unity(f"SET_STEERING:0")

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
                    key_map[key]['value'] = min(1.0, key_map[key]['value'] + 0.1)
                    key_map[key]['increase'] = True
                    # if key_map[key]['value'] == 1.0:  # Max value when held for 1 second
                    #     send_command_to_unity(f"SET_{'SPEED' if key in ['z', 's'] else 'STEERING'}:{key_map[key]['value']:.1f}")

            # Periodically send commands to Unity based on key values
            # print(key_map['z']['value'])
            if key_map['z']['activated'] == 1 and key_map['z']['value'] > 0:
                send_command_to_unity(f"SET_SPEED:{key_map['z']['value']}")
            if key_map['s']['activated'] == 1 and key_map['s']['value'] > 0:
                send_command_to_unity(f"SET_SPEED:{-key_map['s']['value']}")
            if key_map['d']['activated'] == 1 and key_map['d']['value'] > 0:
                send_command_to_unity(f"SET_STEERING:{key_map['d']['value']}")
            if key_map['q']['activated'] == 1 and key_map['q']['value'] > 0:
                send_command_to_unity(f"SET_STEERING:{-key_map['q']['value']}")

            speed_input, speed_v = get_value_for_key('z')
            steering_input, steering_v = get_value_for_key('s')

            next_speed = speed_v
            next_steering = steering_v

            if key_map[speed_input]['increase'] == True and speed_v > 0 and speed_v < 1:
                next_speed+=0.1
            if key_map[speed_input]['increase'] == True and speed_v < 0 and speed_v > -1:
                next_speed-=0.1


            if key_map[steering_input]['increase'] == True and steering_v > 0 and steering_v < 1:
                next_steering+=0.1
            elif key_map[steering_input]['increase'] == True and steering_v < 0 and steering_v > -1:
                next_steering-=0.1

            get_infos_raycast(speed_v, next_speed, steering_v, next_steering)

            if current_time - last_time >= 20:  # Check if 20 seconds have passed
                last_time = current_time
                send_command_to_unity(f"SET_RANDOM_POSITION")
                for key, data in key_map.items():
                    for sub_key, sub_value in data.items():
                        if sub_key == 'value':
                            data[sub_key] = 0  # Update the value directly in the dictionary
                            sub_value = 0  # Update the local variable as well (optional for printing purposes)
                        if sub_key == 'activated':
                            data[sub_key] = 0  # Update the activated value directly in the dictionary
                            sub_value = 0  # Update the local variable as well (optional for printing purposes)

            time.sleep(0.01)  # Wait for 10ms before updating again

    except KeyboardInterrupt:
        print("Stopped.")

# Main function to start the listener
def start_listener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# Start the program
if __name__ == "__main__":
    print("Press keys (z, q, s, d). Press 'Esc' to exit.")
    
    # Start a background thread to periodically update key map values
    update_thread = threading.Thread(target=update_key_values, daemon=True)
    update_thread.start()

    # Start the listener
    start_listener()

    # Print out the key map when you stop the program
    print("\nFinal key map values:")
    for key, value in key_map.items():
        print(f"Key {key}: {value['value']:.1f}")
