import math
from configparser import ConfigParser

import numpy as np


def load_config(config_path: str) -> ConfigParser:
    configuration = ConfigParser()
    configuration.read(config_path)
    return configuration


def normalize(numpy_csv: np.ndarray, config) -> np.ndarray:
    if numpy_csv.ndim == 1:
        numpy_csv = np.expand_dims(numpy_csv, axis=0)
    ray_min = float(config.get('normalization', 'ray_value_min'))
    ray_max = float(config.get('normalization', 'ray_value_max'))
    numpy_csv[:, :12] = (numpy_csv[:, :12] - ray_min) / (ray_max - ray_min)

    if numpy_csv.shape[1] == 14:
        speed_min = float(config.get('normalization', 'speed_value_min'))
        speed_max = float(config.get('normalization', 'speed_value_max'))
        numpy_csv[:, 12] = (numpy_csv[:, 12] - speed_min) / (speed_max - speed_min)

        steering_min = float(config.get('normalization', 'steering_value_min'))
        steering_max = float(config.get('normalization', 'steering_value_max'))
        numpy_csv[:, 13] = (numpy_csv[:, 13] - steering_min) / (steering_max - steering_min)
    return numpy_csv


def split_data(normalized_data: np.ndarray, config):
    train_proportion = float(config.get('DEFAULT', 'train_proportion'))
    test_proportion = float(config.get('DEFAULT', 'test_proportion'))
    validation_proportion = float(config.get('DEFAULT', 'validation_proportion'))
    if train_proportion + test_proportion + validation_proportion != 1.0:
        print(
            f'Invalid proportion, sum equal {train_proportion + test_proportion + validation_proportion}, should be equal to 1.0')
        return None
    train_data = normalized_data[:math.floor(len(normalized_data) * train_proportion)]
    test_data = normalized_data[math.floor(len(normalized_data) * train_proportion):math.floor(
        len(normalized_data) * train_proportion + len(normalized_data) * test_proportion)]
    validation_data = normalized_data[math.floor(len(normalized_data) * -validation_proportion):]

    sum_train = np.array([train_data[:, :3].sum(axis=1)/3, train_data[:, 3:6].sum(axis=1)/3, train_data[:, 6:9].sum(axis=1)/3, train_data[:, 10], train_data[:, 12]]).T
    sum_target = np.array([train_data[:, 11], train_data[:, 13]]).T

    sum_train = np.array([train_data[:, :3].sum(axis=1) / 3, train_data[:, 3:6].sum(axis=1) / 3, train_data[:, 6:9].sum(axis=1) / 3, train_data[:, 10], train_data[:, 12]]).T
    sum_target = np.array([train_data[:, 11], train_data[:, 13]]).T

    sum_train = np.array([train_data[:, :3].sum(axis=1) / 3, train_data[:, 3:6].sum(axis=1) / 3, train_data[:, 6:9].sum(axis=1) / 3,train_data[:, 10], train_data[:, 12]]).T
    sum_target = np.array([train_data[:, 11], train_data[:, 13]]).T

    return (
        train_data[:, :12],
        train_data[:, 12:],
        validation_data[:, :12],
        validation_data[:, 12:],
        test_data[:,:12],
        test_data[:,12:]
    )