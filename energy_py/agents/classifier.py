from collections import defaultdict, namedtuple
import logging
import operator

import numpy as np

from energy_py.agents.agent import BaseAgent

logger = logging.getLogger(__name__)

#  use a namedtuple for a single condition
ClassifierCondition = namedtuple('Condition', ['horizion', 'bin', 'operation'])


class ClassifierStragety(object):
    """
    A single rule for taking deterministic actions based on an observation

    args
        conditions (list) ClassifierConditions - which are named_tuples
        action (np.array) the action to take when all conditions are met
        no_op (np.array) the do nothing action
        obs_info (list) strings of the observation variable names
        name (str)
    """
    def __init__(self,
                 conditions,
                 action,
                 no_op,
                 observation_info,
                 name=None):

        self.conditions = conditions
        self.action = action
        self.no_op = no_op
        self.observation_info = observation_info
        self.name = name

        #  a dictionary for operators to allow different in/equalities
        self.operators = {'==': operator.eq,
                          '!=': operator.ne}

    def __repr__(self):
        string = '<ClassifierStragety {}: conditions {} action {} no_op {}>'

        return string.format(self.name,
                             self.conditions,
                             self.action,
                             self.no_op)

    def compare_condition(self, observation, condition):
        """
        Checks if a condition is true

        args
            observation (np.array)
            condition (namedtuple)

        returns
            (bool)

        Creates the string of the observation
        Predicition indexed using this string
        Returns operation of the prediction versus the condition
            i.e.
                prediction == 1
                prediction != 1
        """
        string = 'D_h_{}_Predicted_Price_Bin_{}'.format(condition.horizion,
                                                        condition.bin)
        #  get the index and the prediction
        idx = self.observation_info.index(string)
        prediciton = observation[0, idx]

        #  get the operation function from self.operators dict
        operation = self.operators[condition.operation]

        #  compare the prediciton verus 1
        return operation(prediciton, 1)

    def check_observation(self, observation):
        """
        Checks the observation versus all conditions

        args
            observation (np.array)

        returns
            action (np.array)

        Iterates over all the conditions in this ClassifierStragety
        """
        bools = [self.compare_condition(observation, cond)
                 for cond in self.conditions]

        if all(bools):
            return self.action

        else:
            return self.no_op


class ClassifierAgent(BaseAgent):
    """
    Flexes based on a prediction from a classifier.

    args
        obs_info (list) strings of the observation variable names
        strat_1 (dict) 'strat_1' : 'conditions': list,
                                   'action': np.array,
                                   'no_op': np.array}

    Can use mulitple strat dicts (i.e. strat_2, strat_some_name)
    The dict key needs to start with 'strat'

    The action is then determined based on the result of all the different
    strageties
    """

    def __init__(self,
                 obs_info,
                 no_op,
                 stop_action=None,
                 **kwargs):

        #  init the BaseAgent parent class
        super().__init__(**kwargs)
        self.no_op = no_op

        #  stop action could be a condition TODO
        self.stop_action = stop_action

        #  hack to get around env adding variables to the observation
        new_obs_info = self.env.env.observation_info[len(obs_info):]
        obs_info.extend(new_obs_info)
        logger.debug('obs_info {}'.format(obs_info))

        self.strageties = []
        for key, value in kwargs.items():
            if key[:5] == 'strat':
                stragety = ClassifierStragety(**value,
                                              observation_info=obs_info,
                                              name=key)
                logger.debug('{}, {}'.format(key, repr(stragety)))
                self.strageties.append(stragety)

    def _act(self, observation):
        """
        Takes an action by calling the stragety

        args
            observation (np.array)

        returns
            action (np.array)
        """
        #  get the actions reccomended by each of our strageties
        actions = [strat.check_observation(observation)
                   for strat in self.strageties]

        #  default action to do nothing
        action = self.no_op

        #  we reverse the list to make sure that the first action gets
        #  the highest priority
        #  alternative would be to have a voting system here
        for act in reversed(actions):
            if act == self.no_op:
                pass
            else:
                action = act

        if self.stop_action:
            #  if we are ending a settlement period, we stop the action
            min_0 = self.env.env.observation_info.index('D_min_0')
            min_0 = observation[0][min_0]

            min_55 = self.env.env.observation_info.index('D_min_55')
            min_55 = observation[0][min_55]

            if min_0 == 1 or min_55 == 1 and action != self.no_op:
                logger.debug('action stopped min0={} min55={}'.format(min_0, min_55))
                logger.debug('action was {} is now {}'.format(action, self.stop_action))
                action = self.stop_action
                logger.debug('action stopped at end of half hour')

        logger.debug('actions {}'.format(actions))
        logger.debug('action selected {}'.format(action))

        return action
