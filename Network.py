import torch.nn as nn

class Network(nn.Module):
    def __init__(self, input_size: int, output_size: int):
        super(Network, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, output_size),
            nn.Tanh()
        )

    def forward(self, x):
        return self.model(x)