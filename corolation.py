import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from utils import load_config


def direction_to_numeric(data: pd.DataFrame) -> pd.DataFrame:
    """
    Takes in a pandas Dataframe filled with random forest ray cast data
    Replace the value of the steering column as we need numeric values to compute the correlations
    """
    mapping = {
        'center': 0,
        'left': -1,
        'diagonal left': -0.5,
        'right': 1,
        'diagonal right': 0.5
    }
    data['steering'] = data['steering'].replace(mapping)
    return data


def show_correlation(data: pd.DataFrame) -> None:
    """
    Computes and display the correlation matrix
    """
    corr_matrix = data.corr()
    plt.figure(figsize=(13, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
    plt.title('Correlation Matrix')
    plt.show()


def main():
    config = load_config('config.ini')
    data = pd.read_csv(config.get('DEFAULT', 'csv_path'))
    data = direction_to_numeric(data)
    show_correlation(data)


if __name__ == '__main__':
    main()
