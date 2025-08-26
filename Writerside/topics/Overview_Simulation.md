# Overview

This page introduces the **simulation** component of the RacingSimulator project.  
It is built in **Unity** and is designed to train AI agents to drive between two parallel lines with increasing autonomy and efficiency.

---

## What Is This?

This simulation was developed using **Unity** to generate training data and experiment with custom AI models.

Unity was chosen for its ease of use, extensive documentation, built-in car physics, and its support for the **ML-Agents** toolkit, which makes it easy to connect external AI agents to the environment.

By using **ML-Agents**, the simulation can host "dummy" agents that wait for external input — for example, from Python scripts.  
It’s also possible to use Unity's own learning system via config files and adjust hyperparameters for built-in training.

> 📘 If you want to try it yourself, follow the step-by-step setup in the [tutorial](Tutorial_Simulation.md).
> 🔄 To understand how the AI connects and interacts with the simulation, check out the [AI Overview](Overview_AI.md).

---

## Glossary

<deflist>
  <def title="Unity">
    A widely-used real-time 3D development engine for games and simulations.  
    It offers tools for physics, animation, rendering, and scripting — ideal for building custom training environments.
  </def>

  <def title="ML-Agents">
    Unity's Machine Learning Agents Toolkit.  
    It enables communication between Unity simulations and external machine learning frameworks such as PyTorch.
  </def>

  <def title="Agent">
    An entity in the simulation that perceives observations and takes actions.  
    In this project, the agent represents the car you're training.
  </def>

  <def title="Environment">
    The Unity simulation in which the agent operates. Includes visuals, physics, obstacles, tracks, etc.
  </def>

  <def title="Observation">
    The information sent from the simulation to the agent — such as sensor values, raycasts, or positional data.
  </def>

  <def title="Action">
    A response returned by the agent, such as turning, accelerating, or braking.
  </def>

  <def title="Reward">
    A numerical value that tells the agent how well it performed — for example, staying between lines or completing laps.
  </def>
</deflist>
