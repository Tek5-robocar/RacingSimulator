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
    steering = 0
    if prediction == 'left':
        steering = -1
    if prediction == 'diagonal left':
        steering = -0.5
    if prediction == 'right':
        steering = 1
    if prediction == 'diagonal right':
        steering = 0.5
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
    time.sleep(5)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((HOST, PORT))
        print('Connexion vers ' + HOST + ':' + str(PORT) + ' réussie.')
        with open('random_forest_model2.pkl', 'rb') as f:
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
    config = load_config('config.ini')
    HOST = '0.0.0.0'  # Server IP
    PORT = 8085  # Server Port
    csv_file = config.get('DEFAULT', 'csv_path')
    main()
