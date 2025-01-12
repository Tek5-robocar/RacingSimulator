import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import utils

config = utils.load_config('config.ini')
data = pd.read_csv(config.get('DEFAULT', 'csv_path'), skiprows=1)
max_value = 230
min_value = 20
data = data.to_numpy()
data_train = data[:, :10]
data_target = data[:, 10]
data_train = (data_train - min_value) / (max_value - min_value)
x_train, x_test, y_train, y_test = train_test_split(data_train, data_target, test_size=0.2, random_state=42)

rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(x_train, y_train)

y_pred = rf_model.predict(x_test)

# Evaluate the model
print("Accuracy:", accuracy_score(y_test, y_pred))
if accuracy_score(y_test, y_pred) > 0.7:
    import pickle
    with open('random_forest_model.pkl', 'wb') as f:
        pickle.dump(rf_model, f)

print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Feature importance
feature_importance = rf_model.feature_importances_
print("\nFeature Importances:")
for i, importance in enumerate(feature_importance):
    print(f"Ray {i+1}: {importance:.4f}")

if __name__ == '__main__':
    main()