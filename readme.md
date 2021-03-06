# energy_py

**reinforcement learning for energy systems**

energy_py provides an agent, energy environments and experiment tools.  The aim is to prove that reinforcement learning can be used to solve energy problems.

energy_py is built and maintained by Adam Green  [adam.green@adgefficiency.com](adam.green@adgefficiency.com).  
- [introductory blog post](http://adgefficiency.com/energy_py-reinforcement-learning-for-energy-systems/)
- [DQN debugging](http://adgefficiency.com/dqn-debugging/)
- [DDQN hyperparameter tuning](http://adgefficiency.com/dqn-tuning/)
- [introductory Jupyter notebook](https://github.com/ADGEfficiency/energy_py/blob/master/notebooks/examples/Q_learning_battery.ipynb)

## Basic usage

Environments and agents are created and used in a style that will be familiar to users of Open AI gym

```python
import energy_py

TOTAL_STEPS = 100000

env = energy_py.make_env(env_id='battery')

agent = energy_py.make_agent(
    agent_id='dqn',
    env=env
    total_steps=TOTAL_STEPS
    )

observation = env.reset()
while not done:
    action = agent.act(observation)
    next_observation, reward, done, info = env.step(action)
    training_info = agent.learn()
    observation = next_observation
```

The higher level energy_py API allows running of experiments from [config dictionaries](https://github.com/ADGEfficiency/energy_py/blob/master/energy_py/experiments/dict_expt.py) or from [config.ini files](https://github.com/ADGEfficiency/energy_py/blob/master/energy_py/experiments/config_expt.py).

Single call using the experiment function

```python
agent_config = {
    'agent_id': 'dqn',
    'double_q': True
                }

energy_py.experiment(
    agent_config,
    env_config,
    total_steps,
    paths=energy_py.make_paths('path/to/results')
    )

```
Running a config dictionary experiment from a Terminal.  The experiment will be called 'example_expt' and will use the
'example' dataset.

```bash
$ cd energy_py/energy_py/experiments

$ python config_expt.py example_expt 
```

## Installation

To install energy_py using Anaconda

```bash
$ conda create --name energy_py python=3.5.2

$ activate energy_py (windows)
or
$ source activate energy_py (unix)

$ git clone https://github.com/ADGEfficiency/energy_py.git

$ cd energy_py

$ python setup.py install (using package)
or
$ python setup.py develop (developing package)

$ pip install --ignore-installed -r requirements.txt

```
## Project 

The aim of energy_py is to provide 
- high quality implementations of agents suited to solving energy problems
- mutiple energy environments
- tools to run experiments

The design philosophies of energy_py
- simple class heirarchy structure (maximum of two levels (i.e. parent child)
- utilize Python standard library (deques, namedtuples etc) where possible
- utilize TensorFlow & TensorBoard
- provide sensible defaults for args

### Agents
Agents are the learners and decision makers.  energy_py supports simpler heuristic (i.e. fully random) agents, which are
often environment specific.  Focus in the library is on building a high quality implementation of DQN and it's
extensions.

The reason for choosing to focus on DQN the that the current energy_py environments have low dimensional action spaces.
Agents which use an argmax across the action space require a discrete action space.

A good summary of DQN variants is given in [Hessel et. al (2017) Rainbow: Combining Improvements in Deep Reinforcement
Learning](https://arxiv.org/pdf/1710.02298.pdf).
- DQN - target network & experience replay
- prioritized experience replay
- DDQN
- dueling architecture

Also implemented are simpler agents such as RandomAgent or agents based on determinsitic rules (usually handcrafted for
a specific environment).

### Environments

#### energy environments
The unique contrbition of energy_py are energy focused environments.  Reinforcement learning has the potential to optimize the operation energy systems.  These environments allow experimentation with energy problems by simulation.

[**Electric battery storage**](https://github.com/ADGEfficiency/energy_py/blob/master/energy_py/envs/battery)

Dispatch of a battery arbitraging wholesale prices.  Battery is defined by a capacity and a maximum rate to charge and
discharge, with a round trip efficieny applied on storage.

[**Flex-v0**](https://github.com/ADGEfficiency/energy_py/tree/master/energy_py/envs/flex)

Model of a flexibility (i.e. demand side response) asset.  Agent can operate two cycles.  Cycle is a fixed length.
1. flex_up/flex_down/relax
2. flex_down/flex_up/relax

[**Flex-v1**](https://github.com/ADGEfficiency/energy_py/tree/master/energy_py/envs/flex)

Agent can operate a flex_down/flex_up/relax cycle.  Agent can choose to stop the flex_down period.

#### Open AI environments

Also included are wrappers around the Open AI gym environments [CartPole-v0](https://gym.openai.com/envs/CartPole-v0/), [Pendulum-v0](https://github.com/openai/gym/wiki/Pendulum-v0) and [MountainCar-v0](https://github.com/openai/gym/wiki/MountainCar-v0). 

These wrappers are implemented in the [energy_py environment
register](https://github.com/ADGEfficiency/energy_py/blob/master/energy_py/envs/register.py).

### Tools to run experiments

In addition to the agents and environments energy_py also provides tools to run experiments.  Visualization of experiment results is done using TensorBoard.
