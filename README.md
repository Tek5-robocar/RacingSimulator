# RacingSimulator# Unity Racing Simulator by AI

## 1. Introduction

This project uses a Unity-based racing simulator in combination with Python to develop, train, and control AI agents. All AI processes, including data collection, model training, and decision-making, are performed externally in Python. The Unity simulator serves as the environment for data generation and testing. Python scripts gather data such as speed, steering, and sensor inputs, which are then used to train machine learning models. Once trained, the AI models communicate with the Unity simulator via a network, sending only the necessary commands (e.g., steering, throttle) to control the car in real-time.


## 2. Features

- Data collection from Unity simulation (e.g., speed, steering, sensors)
- Machine learning model training in Python
- Real-time communication with Unity via network
- Autonomous driving control in Unity, perform with a AI model.

## 3. Technologies and Requirements

- Unity Simulation
- Python
- PyTorch for model training and to use the build model
- pynput for keyboard input collection
- pandas for data collection in a file

## 4. Installation and Setup

```
git clone git@github.com:Tek5-robocar/RacingSimulator.git
cd RacingSimulator
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## How to Use
1. **Running the Unity Simulator**:
    
    To run the Unity Simulator, you have two options:


   - Direct Launch via Terminal: You can launch the Unity simulator directly from the terminal using the following command:
        ```
        ./UnityBuild/RacingSimulator.x86_64
        ```
    -   Using Python: Alternatively, you can launch the simulator programmatically from Python using the subprocess module. Here is an example code snippet:

        ```python
        import subprocess

        UNITY_BUILD_PATH = './UnityBuild/RacingSimulator.x86_64'
        unity_process = subprocess.Popen([UNITY_BUILD_PATH])
        ```




2. **Data Collection**:
   - Run the Python script `collect_data.py` to gather simulation data (speed, steering, sensors).
   - Data will be saved to a CSV file named simulation_data.csv for later use in training.

<!-- 3. **Model Training**:
   - Use the collected data to train a machine learning model.
   - Run `train.py` to train the AI with the collected data.

4. **Real-Time AI Control**:
   - Run `run.py` to control the car autonomously using the trained model.
   - This script sends control signals (e.g., throttle, steering) to Unity via the network. -->