# Overview

This is the AI part of the RacingSimulator project.

## What is product/service/concept

I chose to use the mlagent-envs lib to connect to the simulation for its performance, determinisme and easy to use.
The user as create a python script which use mlagent to open and connect to the simulation. Then frame by frame it will be asked to take a decision.
There are two type of decision:
1. the user is collecting a dataset and use the arrow to drive and so send those to the simualtion.
2. the user is using an AI and send its ouput

## Glossary

A definition list or a glossary:

AI
: Artificial Intelligence

ML Agent
: library used to connect to unity simulation