import os
import numpy as np
import torch
from torch import nn
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

from Network import Network


class Agent:
    def __init__(self, config, device):
        torch.device(device)
        self.device = device
        self.model = Network(5, 1).to(device)
        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(),
                                          lr=float(config.get('hyperparameters', 'learning_rate')))
        self.save_path = config.get('DEFAULT', 'model_save_path')
        self.load_path = config.get('DEFAULT', 'model_load_path')

        self.load()

    def save(self):
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, self.save_path)
        print(f"Model saved to {self.save_path}")

    def load(self):
        if os.path.isfile(self.load_path):
            checkpoint = torch.load(self.load_path, map_location=self.device, weights_only=False)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            print(f"Model loaded from {self.load_path}")
        else:
            print(f"No checkpoint found at {self.load_path}")

    def eval(self, test_loader):
        self.model.eval()
        test_loss = 0.0
        all_predictions = []
        all_targets = []

        with torch.no_grad():
            for test_inputs, test_targets in test_loader:
                test_outputs = self.model(test_inputs.to(self.device))
                test_loss += self.criterion(test_outputs, test_targets.to(self.device)).item()
                all_predictions.append(test_outputs.cpu().numpy())
                all_targets.append(test_targets.cpu().numpy())

        all_predictions = np.vstack(all_predictions)
        all_targets = np.vstack(all_targets)
        test_loss = test_loss / len(test_loader)

        # Print loss
        print(f"Test Loss (MSE): {test_loss}")

        # Calculate additional metrics
        self.calculate_metrics(all_targets, all_predictions)

        # Generate visualizations
        self.visualize_results(all_targets, all_predictions)

    def train(self, train_loader, val_loader, epochs):
        for epoch in range(epochs):
            self.model.train()
            running_loss = 0.0
            for batch_inputs, batch_targets in train_loader:
                self.optimizer.zero_grad()
                outputs = self.model(batch_inputs.to(self.device))
                loss = self.criterion(outputs, batch_targets.to(self.device))
                loss.backward()
                self.optimizer.step()
                running_loss += loss.item()

            # Validation
            self.model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for val_inputs, val_targets in val_loader:
                    val_outputs = self.model(val_inputs.to(self.device))
                    val_loss += self.criterion(val_outputs, val_targets.to(self.device)).item()

            print(
                f"Epoch {epoch + 1}/{epochs}, Train Loss: {running_loss / len(train_loader)}, Val Loss: {val_loss / len(val_loader)}")

    def predict(self, input_data):
        self.model.eval()
        if isinstance(input_data, np.ndarray):
            input_data = torch.tensor(input_data, dtype=torch.float32)
        input_data = input_data.to(self.device)
        with torch.no_grad():
            predictions = self.model(input_data)
        return predictions.cpu().numpy()

    def calculate_metrics(self, targets, predictions):
        mse = mean_squared_error(targets, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(targets, predictions)
        r2 = r2_score(targets, predictions)

        print(f"Mean Absolute Error (MAE): {mae}")
        print(f"Root Mean Squared Error (RMSE): {rmse}")
        print(f"R² Score: {r2}")

    def visualize_results(self, targets, predictions):
        import matplotlib.pyplot as plt

        num_outputs = targets.shape[1]
        residuals = targets - predictions

        # Create a grid of subplots (4 rows, num_outputs columns)
        fig, axes = plt.subplots(4, num_outputs, figsize=(5 * num_outputs, 20))
        axes = axes.flatten()

        for i in range(num_outputs):
            # Scatter Plot
            ax = axes[i]
            ax.scatter(targets[:, i], predictions[:, i], alpha=0.7)
            ax.plot([targets[:, i].min(), targets[:, i].max()],
                    [targets[:, i].min(), targets[:, i].max()], 'r--')
            ax.set_title(f'Scatter Plot for Output {i + 1}')
            ax.set_xlabel('True Values')
            ax.set_ylabel('Predicted Values')
            ax.grid()

            # Residual Analysis
            ax = axes[num_outputs + i]
            ax.scatter(predictions[:, i], residuals[:, i], alpha=0.7)
            ax.axhline(0, color='r', linestyle='--')
            ax.set_title(f'Residual Analysis for Output {i + 1}')
            ax.set_xlabel('Predicted Values')
            ax.set_ylabel('Residuals')
            ax.grid()

            # Histogram of Residuals
            ax = axes[2 * num_outputs + i]
            ax.hist(residuals[:, i], bins=30, alpha=0.7)
            ax.set_title(f'Residual Histogram for Output {i + 1}')
            ax.set_xlabel('Residual')
            ax.set_ylabel('Frequency')
            ax.grid()

        # Error Heatmap (if applicable)
        if num_outputs == 2:  # Assuming outputs are spatial
            errors = np.linalg.norm(targets - predictions, axis=1)
            ax = axes[3 * num_outputs]
            scatter = ax.scatter(targets[:, 0], targets[:, 1], c=errors, cmap='viridis', alpha=0.7)
            fig.colorbar(scatter, ax=ax, label='Error Magnitude')
            ax.set_title('Error Heatmap')
            ax.set_xlabel('Output 1')
            ax.set_ylabel('Output 2')
            ax.grid()

        # Adjust layout
        plt.tight_layout()
        plt.savefig('plot.png')
        plt.show()
