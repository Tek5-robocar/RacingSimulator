import os
import socket
import subprocess
import time
import asyncio

import pandas as pd
from pynput import keyboard
from threading import Thread  # To run pynput in a separate thread

from unity import send_command_to_unity

# Connect to Unity server
host = "127.0.0.1"
port = 5000
last_click = time.time()

speed = 0
speed_count = 0
steering = 0
steering_count = 0
stop = False
active_keys = set()

csv_file = "lidar_data.csv"
columns = [f"lidar_{i}" for i in range(1, 11)]  # Creating column names like lidar_1, lidar_2, ..., lidar_32
columns.append("speed")
columns.append("steering")


def initialize_csv():
    if not os.path.exists(csv_file):
        df = pd.DataFrame(columns=columns)
        df.to_csv(csv_file, mode='w', index=False)


it = 0


def get_infos_raycast():
    global it
    x = send_command_to_unity('GET_INFOS_RAYCAST')
    x_splitted = x.split(':')
    if x_splitted[0] == 'KO':
        return
    x = [elem[:3] for elem in x_splitted[1:]]
    try:
        x.append(str(speed)[:3])
        x.append(str(steering)[:3])
        lidar_data = pd.DataFrame([x], columns=columns)
        if it == 0:
            lidar_data.to_csv(csv_file, mode='a', header=True, index=False)
        else:
            lidar_data.to_csv(csv_file, mode='a', header=False, index=False)
        it += 1
    except Exception as e:
        os.write(2, f"Error writing to CSV: {str(e)}\n".encode())


def on_press(key):
    """Handle key press events."""
    global last_click, speed, speed_count, steering, steering_count, active_key, stop
    try:
        active_keys.add(key)

        if keyboard.KeyCode.from_char('z') in active_keys:
            get_infos_raycast()
            speed_count += 1
            last_click = time.time()
            if speed_count >= 10:
                speed_count = 0
                answer = send_command_to_unity('GET_SPEED')
                if answer.split(':')[0] == 'OK':
                    speed = float(answer.split(':')[1]) + 0.1
            else:
                speed += 0.1
            if speed < 0:
                speed = 0
            if speed > 1:
                speed = 1
            print(f"up = {speed}]")
            send_command_to_unity(f"SET_SPEED:{speed}")
        if keyboard.KeyCode.from_char('s') in active_keys:
            get_infos_raycast()
            speed_count += 1
            last_click = time.time()
            if speed_count >= 10:
                speed_count = 0
                answer = send_command_to_unity('GET_SPEED')
                if answer.split(':')[0] == 'OK':
                    speed = float(answer.split(':')[1]) - 0.1
            else:
                speed -= 0.1
            if speed > 0:
                speed = 0
            if speed < -1:
                speed = -1
            print(f"down = {speed}")
            send_command_to_unity(f"SET_SPEED:{speed}")
        if keyboard.KeyCode.from_char('d') in active_keys:
            get_infos_raycast()
            steering_count += 1
            last_click = time.time()
            if steering_count >= 10:
                steering_count = 0
                answer = send_command_to_unity('GET_STEERING')
                if answer.split(':')[0] == 'OK':
                    steering = float(steering.split(':')[1]) + 0.1
            else:
                steering += 0.1
            if steering < 0:
                steering = 0
            if steering > 1:
                steering = 1
            print(f"right = {steering}")
            send_command_to_unity(f"SET_STEERING:{steering}")
        if keyboard.KeyCode.from_char('q') in active_keys:
            get_infos_raycast()
            steering_count += 1
            last_click = time.time()
            if steering_count >= 10:
                steering_count = 0
                answer = send_command_to_unity('GET_STEERING')
                if answer.split(':')[0] == 'OK':
                    steering = float(answer.split(':')[1]) - 0.1
            else:
                steering -= 0.1
            if steering > 0:
                steering = 0
            if steering < -1:
                steering = -1
            print(f"left = {steering}")
            send_command_to_unity(f"SET_STEERING:{steering}")
        if key.char == 'r':
            send_command_to_unity("SET_RANDOM_POSITION")

        # Proper handling of special keys (esc, etc.)
        if key == keyboard.Key.esc:
            stop = True
            print("Exiting...")
            active_keys.clear()  # Clear active keys when exiting
            return False  # Stop the listener

    except AttributeError:
        # If we get an AttributeError, it's likely a special key (esc, etc.)
        pass  # Do nothing; just continue the program


def on_release(key):
    """Handle key release events (optional)."""
    global active_keys
    active_keys.discard(key)  # Remove the key from active_keys when released
    pass


def start_keyboard_listener():
    """Run the keyboard listener in a separate thread."""
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


async def control_loop():
    """Run the control loop asynchronously."""
    global last_click, stop
    random_position_last_sent = time.time()  # Initialize a timestamp for the last random position command

    while stop != True:
        current_time = time.time()

        # Check if 5 seconds have passed since the last random position command
        if current_time - random_position_last_sent > 5:
            send_command_to_unity("SET_RANDOM_POSITION")
            random_position_last_sent = current_time  # Update the timestamp of when the last random position was sent

        # Sleep for a short time to avoid blocking the main thread
        await asyncio.sleep(0.1)


UNITY_BUILD_PATH = os.path.join(os.getcwd(), '..', 'unity-simulator', 'UnityBuild', 'RacingSimulator.x86_64')


async def main():
    """Run the control loop and keyboard listener together."""
    unity_process = subprocess.Popen([UNITY_BUILD_PATH])
    time.sleep(5)
    initialize_csv()

    listener_thread = Thread(target=start_keyboard_listener, daemon=True)
    listener_thread.start()

    # Run the control loop
    await control_loop()
    send_command_to_unity("END_SIMULATION")
    if unity_process:
        unity_process.terminate()


if __name__ == "__main__":
    asyncio.run(main())
