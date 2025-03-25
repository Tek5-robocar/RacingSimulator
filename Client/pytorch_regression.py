import numpy as np
import pandas as pd
import torch
from IPython.core.display_functions import display
from matplotlib import pyplot as plt, colors

from Client.utils import load_config


class Regression(torch.nn.Module):
    def __init__(self, nb_input, nb_output):
        super(Regression, self).__init__()

        self.model = torch.nn.Sequential(
            torch.nn.Linear(nb_input, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64, nb_output),
        )

    def forward(self, x):
        # print(f'Input dtype: {x.dtype}')
        x = self.model(x)
        # print(f'Output dtype: {x.dtype}')
        return x


def show_distribution(data: pd.DataFrame, column: str):
    data[column].hist()

    plt.xlabel(column)
    plt.ylabel('rows')
    plt.title(f'Distribution of {column}')

    plt.show()


def load_data():
    global min_value
    global max_value
    data = pd.read_csv(csv_path)

    data.drop(columns=['steering_discrete'], axis=1, inplace=True)

    min_value = min(data.iloc[0:, :10].min())
    max_value = max(data.iloc[0:, :10].max())

    print(f'min_value = {min_value}, max_value = {max_value}')

    show_distribution(data, 'steering_continuous')
    show_correlation(data)
    mask = np.random.rand(len(data)) < 1.0 - config.getfloat('normalization', 'test_proportion')

    train = data[mask]
    train_x = (train.iloc[:, :10] - min_value) / (max_value - min_value)
    train_y = train.iloc[:, 10]

    test = data[~mask]
    test_x = (test.iloc[:, :10] - min_value) / (max_value - min_value)
    test_y = test.iloc[:, 10]

    return (torch.tensor(train_x.values, dtype=torch.float32).to(device),
            torch.tensor(train_y.values, dtype=torch.float32).to(device),
            torch.tensor(test_x.values, dtype=torch.float32).to(device),
            torch.tensor(test_y.values, dtype=torch.float32).to(device))


def show_correlation(data: pd.DataFrame):
    corr = data.corr()

    fig, ax = plt.subplots(figsize=(10, 8))

    cmap = colors.LinearSegmentedColormap.from_list(
        'custom', ['#1f77b4', '#ffffff', '#d62728'], N=256)

    norm = colors.Normalize(vmin=-1, vmax=1)

    cax = ax.matshow(corr, cmap=cmap, norm=norm)

    cbar = fig.colorbar(cax, fraction=0.046, pad=0.04)
    cbar.set_label('Correlation Strength', rotation=270, labelpad=15)

    for i in range(len(corr.columns)):
        for j in range(len(corr.columns)):
            ax.text(j, i, f'{corr.iloc[i, j]:.2f}',
                    ha='center', va='center',
                    color='black' if abs(corr.iloc[i, j]) < 0.7 else 'white',
                    fontsize=8)

    ax.set_xticks(np.arange(len(corr.columns)))
    ax.set_yticks(np.arange(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45, ha='left')
    ax.set_yticklabels(corr.columns)

    plt.tight_layout()
    plt.title('Correlation Matrix', pad=20)
    plt.show()


def main():
    torch.set_default_dtype(torch.float32)

    train_x, train_y, test_x, test_y = load_data()

    model = Regression(10, 1).cuda()

    loss = torch.nn.MSELoss().to(device)
    optimizers = torch.optim.Adam(params=model.parameters(), lr=config.getfloat('hyperparameters', 'learning_rate'))
    nb_epochs = config.getint('hyperparameters', 'nb_epochs')

    losses = []

    early_stop = config.getint('hyperparameters', 'early_stop')

    for i in range(nb_epochs):
        optimizers.zero_grad()

        with torch.autocast(device_type=device):
            train_y_predictions = model(train_x).to(device)
            loss_value = loss(train_y_predictions.squeeze(), train_y.squeeze())
        loss_value.backward()
        optimizers.step()

        if len(losses) > 0 and loss_value > losses[-1]:
            early_stop -= 1
        else:
            early_stop = config.getint('hyperparameters', 'early_stop')

        losses.append(loss_value)

        if early_stop == 0:
            break

    torch.save(model.state_dict(), config.get('DEFAULT', 'model_save_path'))

    plt.plot([i for i in range(len(losses))], [loss_value.cpu().detach().numpy() for loss_value in losses])
    plt.title('loss over epochs')
    plt.show()


if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    config = load_config('config_regression.ini')

    csv_path = config.get('DEFAULT', 'csv_path')

    min_value = None
    max_value = None

    main()
