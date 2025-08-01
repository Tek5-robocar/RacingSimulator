# Tutorial

This tutorial is for those who wants to do the RacingSimulator project or simply to learn how to use mlagent in python.
You need to know about python, only lib specific notion will be explained.

Provide a short outline for the tutorial.
In this tutorial, you will learn how to:
* use ml agent lib
* create a supervised agent

## Before you start

List the prerequisites that are required or recommended.

Make sure that:
- python
- installed the requirements.txt using (pip install -r requirements.txt)
- have the build of the simulation (see here if not)

## Part 1

First thing we are gonna use mlagent to open and connect to the simulation.
You need to give it a json file looking to:

```json
{
  "agents": [
    {
      "fov": 180,
      "nbRay": 10
    },
    {
      "fov": 100,
      "nbRay": 20
    }
  ]
}
```
here 2 agents will be created with the specified instructions. changing fov and nbRay will affect the result of your AIs
```python
env = UnityEnvironment(
    file_name='simulation_path',
    additional_args=['--config-path', 'json_config_path'],
    base_port=5004,
)
```

Then reset the simulation

```python
env.reset()
```

Then get the list of behavior names

```python
behavior_names = list(env.behavior_specs.keys())
```

Each behavior name correspond to one agent, you will use its name to be sure to send the information about the right one

Now at each frame you can get the step:

```python
decision_steps, terminal_steps = env.get_steps(behavior_name)
```

you get the decision step which is of DecisionSteps type and terminal step which is of TerminalSteps type
A DecisionSteps NamedTuple containing the observations, the rewards, the agent ids and the action masks for the Agents of the specified behavior. These Agents need an action this step.
A TerminalSteps NamedTuple containing the observations, rewards, agent ids and interrupted flags of the agents that had their episode terminated last step.

using that you can feed the observations to 
your AI and gets its output, then you send it like this:

```python
batch_action = ActionTuple()
batch_action.add_continuous(np.repeat(continuous_action, num_agents, axis=0))
env.set_actions(behavior_name, batch_action)
```

doing this you create an action tuple, then you add the continuous actions of all the agents linked to this specific bahavior name and then set it as actions.
you need to do that for each behavior name
then you advance the step:

```python
env.step()
```

## Part 2

Now lets talk about AI.
The easiest way to do is to use a supervised model (what is it ?).
For that you need to collect a dataset using your input and then make your AI learn.

We will start by creating an AI controlling the steering with a fix speed.
First thing first, create a script which use a joystic (from a controler or using the mouse) to control the car.
Then save into a dataframe the raycast values associated to the decision you took (the direction of the joystic) for each frame.
ps: i recommand using the track 2 for that

when you have about 1000 lines, save the dataframe as a .csv file.
we now do a little EDA to make sure our data is correct
now we will create the AI model.

to start easy, we will use a simple Linear regression, here is a simple example:

```python
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
        x = self.model(x)
        return x
```

we need to load the previously saved .csv, normalize the data, split between train, validation and test then train and test

```python
def load_data():
    nb_raycast = 10
    data = pd.read_csv(csv_path)

    data.drop(columns=['ai_prediction'], axis=1, inplace=True)

    min_value = min(data.iloc[0:, :nb_raycast].min())
    max_value = max(data.iloc[0:, :nb_raycast].max())

    mask = np.random.rand(len(data)) < 1.0 - 0.2

    train = data[mask]
    train_x = (train.iloc[:, :nb_raycast] - min_value) / (max_value - min_value)
    train_y = train.iloc[:, nb_raycast]

    test = data[~mask]
    test_x = (test.iloc[:, :nb_raycast] - min_value) / (max_value - min_value)
    test_y = test.iloc[:, nb_raycast]

    return (torch.tensor(train_x.values, dtype=torch.float32).to(device),
            torch.tensor(train_y.values, dtype=torch.float32).to(device),
            torch.tensor(test_x.values, dtype=torch.float32).to(device),
            torch.tensor(test_y.values, dtype=torch.float32).to(device))
```

```python
    train_x, train_y, test_x, test_y = load_data()

    model = Regression(nb_raycast, 1).cuda()

    loss = torch.nn.MSELoss().to(device)
    optimizers = torch.optim.Adam(params=model.parameters(), lr=0.0001)
    nb_epochs = 10

    scaler = torch.amp.GradScaler('cuda')

    for i in range(nb_epochs):
        optimizers.zero_grad()

        with torch.amp.autocast('cuda', dtype=torch.float16):
            train_y_predictions = model(train_x).to(device)
            loss_value = loss(train_y_predictions.squeeze(), train_y.squeeze())

        scaler.scale(loss_value).backward()
        scaler.step(optimizers)
        scaler.update()

    torch.save(model.state_dict(), 'model.pth')
```

now we have a trained model on our dataset, we need to use it

using the same code than previously to control the car but using the model, you need to load it, normalize the observations you get from mlagent (it is important to normalize using the same borne as for the training) and then give the output to the simulation

## Going further

If you want to go further and do more interesting things you can do some RL. For that you first need to go the the simulation and add a reward system (see here).
Then implement your RL algorithm in python and replace the supervised model by it.
ps: don't hesitate to use multiple agents