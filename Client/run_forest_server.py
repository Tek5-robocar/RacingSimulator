import pickle
import socket
import subprocess
import time
import numpy as np

from utils import load_config


def send_command_to_unity(client, command: str):
    """Send a command to the Unity server."""
    print(f'sending: {command}')
    sent = client.send(bytes(command + ";", 'utf-8'))
    recv = client.recv(1024)
    return str(recv, 'utf-8')


def get_numeric_steering(prediction: str) -> float:
    """
    Convert str prediction to numeric value for steering
    """
    print('get_numeric_steering')
    print(steering_map[prediction[0]])
    steering = sum(steering_map[prediction[0]]) / 2
    print(steering)
    return steering


def get_ray_cast(max_value: float, min_value: float, client) -> [float]:
    """
    Ask simulator for ray cast and preprocess it
    """
    result = send_command_to_unity(client, "GET_INFOS_RAYCAST")
    result_splitted = [result.split(';')[0]]
    if len(result_splitted) != 1:
        return None
    raycast = result_splitted[0]
    splitted_raycast = raycast.split(':')
    if len(splitted_raycast) != 12 or splitted_raycast[0] != 'OK' or splitted_raycast[1] != 'GET_INFOS_RAYCAST':
        return None
    return [(float(elem) - min_value) / (max_value - min_value) for elem in splitted_raycast[2:]]


def loop(rf_model, client):
    """
    Loop where we use the AI prediction to drive
    """
    max_value = float(config.get('normalization', 'ray_value_max'))
    min_value = float(config.get('normalization', 'ray_value_min'))

    for i in range(1000):
        float_arr = get_ray_cast(max_value, min_value, client)
        prediction = rf_model.predict(np.array([float_arr]))
        print(f'pred: {prediction}')
        send_command_to_unity(client, f"SET_SPEED:{0.7};SET_STEERING:{get_numeric_steering(prediction)}")


def main():
    unity_process = subprocess.Popen([config.get('unity', 'env_path')])
    time.sleep(10)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((HOST, PORT))
        print('Connexion vers ' + HOST + ':' + str(PORT) + ' réussie.')
        with open('random_forest_model1.pkl', 'rb') as f:
            rf_model = pickle.load(f)
        loop(rf_model, client)

    except Exception as e:
        print("Erreur lors de la connexion ou de l'envoi: ", e)
    finally:
        print('Déconnexion.')
        client.close()
    if unity_process:
        unity_process.terminate()


if __name__ == '__main__':
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

    config = load_config('config.ini')
    HOST = '0.0.0.0'  # Server IP
    PORT = 8085  # Server Port
    csv_file = config.get('DEFAULT', 'csv_path')
    main()
