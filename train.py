import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset
from Agent import Agent
from utils import split_data, load_config, normalize
import numpy as np


class CustomDataset(Dataset):
    def __init__(self, inputs, targets, augment=False):
        self.inputs = torch.tensor(inputs, dtype=torch.float32)
        self.targets = (torch.tensor(targets, dtype=torch.float32) + 1) / 2
        self.augment = augment

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, idx):
        inputs = self.inputs[idx]
        targets = self.targets[idx]

        if self.augment:
            inputs = self.augment_data(inputs)

        return inputs, targets

    def augment_data(self, inputs):
        # Convert tensor to numpy for augmentation
        inputs = inputs.numpy()

        # LIDAR rays augmentation (first 10 features)
        noise = np.random.normal(0, 0.05, size=3)  # Gaussian noise
        inputs[:3] += noise

        # Random dropout of LIDAR rays
        dropout_mask = np.random.choice([0, 1], size=3, p=[0.1, 0.9])  # 10% dropout
        inputs[:3] *= dropout_mask

        # Speed augmentation (11th feature)
        inputs[3] *= np.random.uniform(0.9, 1.1)  # Scale speed by 90-110%

        # Steering augmentation (12th feature)
        inputs[4] += np.random.normal(0, 0.02)  # Add small noise to steering

        # Convert back to tensor
        return torch.tensor(inputs, dtype=torch.float32)


def main():
    data = pd.read_csv(config.get('DEFAULT', 'csv_path'))
    normalized_data = normalize(data.to_numpy(), config)
    train_data, train_target, validation_data, validation_target, test_data, test_target = split_data(normalized_data, config)

    # Enable augmentation only for the training dataset
    train_dataset = CustomDataset(train_data, train_target, augment=True)
    val_dataset = CustomDataset(validation_data, validation_target, augment=False)
    test_dataset = CustomDataset(test_data, test_target, augment=False)

    batch_size = int(config.get('hyperparameters', 'batch_size'))

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    agent = Agent(config, 'cuda')

    agent.train(train_loader, val_loader, int(config.get('DEFAULT', 'epoch')))
    agent.save()

    agent.eval(test_loader)


if __name__ == '__main__':
    config = load_config('config.ini')
    main()