import pandas as pd
import utils

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score


def preprocess_data(data):
    """
    Normalize and preprocess data, then split it between train and test
    """
    max_value = float(config.get('normalization', 'ray_value_max'))
    min_value = float(config.get('normalization', 'ray_value_min'))
    data = data.to_numpy()
    data_train = data[:, :10]
    data_target = data[:, 10]
    data_train = (data_train - min_value) / (max_value - min_value)
    return train_test_split(data_train, data_target, test_size=float(config.get('normalization', 'test_proportion')),random_state=42)


def evaluate(rf_model, x_test, y_test):
    """
    Compute accuracy and show importance of each feature
    """
    y_pred = rf_model.predict(x_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    if accuracy_score(y_test, y_pred) > 0.7:
        import pickle
        with open('random_forest_model.pkl', 'wb') as f:
            pickle.dump(rf_model, f)
    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    feature_importance = rf_model.feature_importances_
    print("\nFeature Importances:")
    for i, importance in enumerate(feature_importance):
        print(f"Ray {i + 1}: {importance:.4f}")


def main():
    data = pd.read_csv(config.get('DEFAULT', 'csv_path'), skiprows=1)
    x_train, x_test, y_train, y_test = preprocess_data(data)
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(x_train, y_train)
    evaluate(rf_model, x_test, y_test)


if __name__ == '__main__':
    config = utils.load_config('config.ini')
    main()
