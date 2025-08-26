# Overview

This is the **AI** part of the *RacingSimulator* project.

The goal of this component is to provide an interface between a Python script (your AI or manual driver) and the Unity simulation.

---

## What Is This?

To interact with the Unity simulation, we use the `mlagents` and `mlagents_envs` libraries from Unity’s ML-Agents Toolkit.  
These libraries offer a fast, deterministic, and easy-to-use API for communicating with agents in the simulation.

The user must create a Python script that launches the Unity simulation and connects to it via ML-Agents.  
At every frame, the script is prompted to send a decision — either human-controlled or AI-generated.

There are two main interaction modes:

1. **Manual Driving** – You control the car using the keyboard (arrow keys), and the script relays these actions to the simulation. This mode is typically used to collect datasets.
2. **AI-Controlled Driving** – Your Python-based AI model decides what actions to take, and the script sends them to the simulation in real-time.

> 📘 To get started writing your own Python controller, follow the [AI Tutorial](Tutorial_AI.md).  
> 🔄 For details on how the simulation is structured, see the [Simulation Overview](Overview_Simulation.md).

---

## Glossary

<deflist>

<def title="AI">
Artificial Intelligence – algorithms and models that can make decisions, often trained via machine learning.
</def>

<def title="ML-Agents">
Unity's Machine Learning Agents Toolkit, which enables simulations to interface with external reinforcement learning or scripted agents.
</def>

<def title="Agent">
An entity within the Unity simulation that receives observations and performs actions.
</def>

<def title="Observation">
Data received from the simulation describing the environment, such as distance to lines or raycast results.
</def>

<def title="Action">
A response sent by the AI or human input to influence the agent — for example, steering or accelerating.
</def>

<def title="Environment">
The Unity-based simulation that the agent interacts with.
</def>

</deflist>