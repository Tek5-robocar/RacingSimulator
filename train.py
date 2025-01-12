import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset

import utils
from Agent import Agent
from utils import split_data, load_config, normalize
import numpy as np


class CustomDataset(Dataset):
    def __init__(self, inputs, targets):
        self.inputs = torch.tensor(inputs, dtype=torch.float32)
        if targets is not None:
            self.targets = (torch.tensor(targets, dtype=torch.float32) + 1) / 2

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, idx):
        inputs = self.inputs[idx]
        targets = self.targets[idx]

        return inputs, targets

def augment_data(inputs):
    augmented_inputs = inputs.copy()
    # Convert tensor to numpy for augmentation
    if type(augmented_inputs) != np.ndarray:
        augmented_inputs = augmented_inputs.to_numpy()
    # LIDAR rays augmentation (first 10 features)
    noise = np.random.normal(0, 0.1, size=10)  # Gaussian noise
    augmented_inputs[:10] += noise

    # Random dropout of LIDAR rays
    dropout_mask = np.random.choice([0, 1], size=10, p=[0.2, 0.8])  # 10% dropout
    augmented_inputs[:10] *= dropout_mask
    #
    # # # Speed augmentation (11th feature)
    # augmented_inputs[:,10] *= np.random.uniform(0.7, 1.3)  # Scale speed by 90-110%
    # # #
    # # # # Steering augmentation (12th feature)
    # augmented_inputs[:,12] += np.random.normal(0, 0.1)  # Add small noise to steering

    # Convert back to tensor
    return torch.tensor(augmented_inputs, dtype=torch.float32)


def main():
    data = pd.read_csv(config.get('DEFAULT', 'csv_path'), skiprows=1).apply(pd.to_numeric)
    extremum = [(data[column].min(), data[column].max()) for column in data]

    # data = np.apply_along_axis(augment_data, axis=1, arr=data)

    normalized_data = utils.preprocess_and_normalize(pd.DataFrame(data))

    train_data, train_target, validation_data, validation_target, test_data, test_target = split_data(normalized_data.to_numpy(), config)

    # Enable augmentation only for the training dataset
    train_dataset = CustomDataset(train_data, train_target)
    val_dataset = CustomDataset(validation_data, validation_target)
    test_dataset = CustomDataset(test_data, test_target)

    batch_size = int(config.get('hyperparameters', 'batch_size'))

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    agent = Agent(config, 'cuda')
    print(train_data.shape)
    print(train_target.shape)
    print(validation_data.shape)
    print(validation_target.shape)
    print(test_data.shape)
    print(test_target.shape)
    agent.train(train_loader, val_loader, int(config.get('DEFAULT', 'epoch')), int(config.get('hyperparameters', 'patience')))
    agent.save(extremum)

    agent.eval(test_loader)


if __name__ == '__main__':
    config = load_config('config.ini')
    main()