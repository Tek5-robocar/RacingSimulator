import pickle
import subprocess
import time
import numpy as np

from utils import load_config


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


def get_ray_cast(max_value: float, min_value: float) -> [float]:
    """
    Ask simulator for ray cast and preprocess it
    """
    result = send_command_to_unity("GET_INFOS_RAYCAST")
    result_splitted = result.split(';')
    if len(result_splitted) != 1:
        return None
    raycast = result_splitted[0]
    splitted_raycast = raycast.split(':')
    if len(splitted_raycast) != 12 or splitted_raycast[0] != 'OK' or splitted_raycast[1] != 'GET_INFOS_RAYCAST':
        return None
    return [(float(elem) - min_value) / (max_value - min_value) for elem in splitted_raycast[2:]]


def loop(rf_model):
    """
    Loop where we use the AI prediction to drive
    """
    max_value = float(config.get('normalization', 'ray_value_max'))
    min_value = float(config.get('normalization', 'ray_value_min'))

    for i in range(1000):
        float_arr = get_ray_cast(max_value, min_value)
        prediction = rf_model.predict(np.array([float_arr]))
        send_command_to_unity(f"SET_SPEED:{0.7};SET_STEERING:{get_numeric_steering(prediction)}")


def main():
    unity_process = subprocess.Popen([config.get('unity', 'env_path')])
    time.sleep(5)

    with open('random_forest_model3.pkl', 'rb') as f:
        rf_model = pickle.load(f)
    try:
        for _ in range(5):
            loop(rf_model)
            send_command_to_unity("SET_RANDOM_POSITION")
    except Exception as e:
        print(e)

    send_command_to_unity("END_SIMULATION")
    if unity_process:
        unity_process.terminate()


if __name__ == '__main__':
    config = load_config('config.ini')
    main()
