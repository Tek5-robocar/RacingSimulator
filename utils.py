import math
from configparser import ConfigParser

import numpy as np
import pandas as pd


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
    print(normalized_data.shape)
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

    sum_data_train = np.array(
        [train_data[:, :4].sum(axis=1) / 4, train_data[:, 4:6].sum(axis=1) / 2, train_data[:, 6:10].sum(axis=1) / 4]).T
        # [train_data[:, :4].sum(axis=1) / 4, train_data[:, 4:6].sum(axis=1) / 2, train_data[:, 6:10].sum(axis=1) / 4, train_data[:, 10], train_data[:, 12]]).T
    sum_target_train = np.array([train_data[:, 11]]).T
    # sum_target_train = np.array([train_data[:, 11], train_data[:, 13]]).T

    sum_data_test = np.array(
        [test_data[:, :4].sum(axis=1) / 4, test_data[:, 4:6].sum(axis=1) / 2, test_data[:, 6:10].sum(axis=1) / 4]).T
        # [test_data[:, :4].sum(axis=1) / 4, test_data[:, 4:6].sum(axis=1) / 2, test_data[:, 6:10].sum(axis=1) / 4, test_data[:, 10], test_data[:, 12]]).T
    sum_target_test = np.array([test_data[:, 11]]).T
    # sum_target_test = np.array([test_data[:, 11], test_data[:, 13]]).T

    sum_data_validation = np.array([validation_data[:, :4].sum(axis=1) / 4, validation_data[:, 4:6].sum(axis=1) / 2,
                                    validation_data[:, 6:10].sum(axis=1) / 4]).T
    # sum_data_validation = np.array([validation_data[:, :4].sum(axis=1) / 4, validation_data[:, 4:6].sum(axis=1) / 2,
    #                                 validation_data[:, 6:10].sum(axis=1) / 4, validation_data[:, 10],
    #                                 validation_data[:, 12]]).T
    sum_target_validation = np.array([validation_data[:, 11]]).T
    # sum_target_validation = np.array([validation_data[:, 11], validation_data[:, 13]]).T
    return (
        train_data[:, list(range(10)) + [train_data[:, 0] + train_data[:, 9]]], np.array([train_data[:, 13]]).T, validation_data[:, list(range(10)) + [validation_data[:, 0] + validation_data[:, 9]]], np.array([validation_data[:, 13]]).T, test_data[:, list(range(10)) + [test_data[:, 0] + test_data[:, 9]]], np.array([test_data[:, 13]]).T
        # sum_data_train, sum_target_train, sum_data_validation, sum_target_validation, sum_data_test, sum_target_test
    )


def preprocess_and_normalize(df):
    """
    Preprocess the DataFrame by converting all rows except the first to float,
    and normalize all numeric columns between their two largest values.

    Parameters:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: A DataFrame with normalized numeric columns.
    """
    normalized_df = df.copy()
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            max_val = df[col].max()
            min_val = df[col].min()
            if min_val >= max_val:  # Avoid division by zero
                print(f"Warning: Column '{col}' has identical largest values.")
                normalized_df[col] = 0  # Set all values to 0 if normalization is invalid
            else:
                normalized_df[col] = (df[col] - min_val) / (max_val - min_val)
    return normalized_df
