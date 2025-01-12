import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load dataset
data = pd.read_csv('lidar_data1.csv')
data['left-right-diff'] = data.iloc[:, 0] + data.iloc[:, 9]
# Correlation matrix
corr_matrix = data.corr()

# Visualize correlations
plt.figure(figsize=(13, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation Matrix')
plt.show()

# Scatter plot for a specific ray
sns.scatterplot(x=data['steering'], y=data['ray_cast_1'])
plt.title('Steering vs Ray Cast 1')
plt.xlabel('Steering')
plt.ylabel('Ray Cast 1')
plt.show()
