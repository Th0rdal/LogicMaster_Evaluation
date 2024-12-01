import chess
import gym
import time
from gym import spaces
import numpy as np
from stable_baselines3 import DQN

from src.factors.position_calculator import positionCalculator
from src.params import Params
from src.stockfish import getExpectedResult
from src.inputProcessing import InputProcessor

"""
for x in range(10):
    print(x, flush=True)
    time.sleep(1)
"""

class Qlearning(gym.Env):

    metadata_threshold = 0.01
    metadata_maxActionsPerBoard = 50
    metadata_boardsPerEpoch = 1024
    metadata_learning_rate = 0.001
    stateToBits = {-1: 1, 0: 0, 1: 2}
    bitsToState = {1: -1, 0: 0, 2: 1}

    def __init__(self, targetFunction):
        super(Qlearning, self).__init__()

        # create actions space. Each variable can be slightly increased, stay the same or be slightly decreased. Each parameter can be changed in any of these 3 ways
        self.input = None
        self.currentActionCount = None
        self.inputGenerator = None
        self.inputProcessor = InputProcessor()
        self.action_space = spaces.Discrete(3 ** 5)

        # create observation space. It defines the state space that the environment provides to the agent.
        # Each param is constrained between -10 and 10 with a possible error of -inf to inf.
        self.observation_space = spaces.Box(
            low = np.array([[-10] * 5 + [-float('inf')]]),
            high = np.array([[10] * 5 + [float('inf')]]),
            dtype = np.float32
        )

        self.target_function = targetFunction
        self.expected_output = 0
        self.current_error = float('inf')

    def encodeAction(self):
        actionIndex = 0
        for i, p in enumerate(Params.params):
            actionIndex += self.stateToBits[p.value] * (3 ** i)
        return actionIndex

    def decodeAction(self, encodedAction):
        params = []
        for _ in range(Params.totalParameter):
            params.append(self.bitsToState[encodedAction % 3])
            encodedAction //= 3
        return params

    def step(self, action):

        decodedAction = self.decodeAction(action)
        delta = np.array(decodedAction) - 1
        for element in Params.params:
            element += delta * self.metadata_learning_rate

        # run function and return actual and expected output
        actualResult = self.target_function(self.input)
        self.current_error = getExpectedResult(self.input)

        #calculate error and reward
        self.current_error = abs(self.expected_output - actualResult)
        reward = -self.current_error

        observation = np.array(Params.params[:5] + [self.current_error])

        done = self.current_error < self.metadata_threshold

        self.currentActionCount += 1
        if self.currentActionCount == self.metadata_maxActionsPerBoard:
            done = True
        return observation, reward, done, {}

    def reset(self, **kwargs):
        for element in Params.params:
            element += np.random.uniform(-5, 5)
        self.input = chess.Board(next(self.inputGenerator))
        if self.input is None:
            raise StopIteration("Episode completed. Input is None!")
        self.expected_output = getExpectedResult(self.input)
        computed_value = self.target_function(self.input)
        self.current_error = abs(self.expected_output - computed_value)

        self.currentActionCount = 0

        return Params.params[:5] + [self.current_error]

    def getInput(self, boardType):
        self.inputProcessor.loadNextSet(boardType)
        self.inputGenerator = self.inputProcessor.getInputBoard()

if __name__ == '__main__':
    ai = Qlearning(positionCalculator)
    model = DQN("MlpPolicy", ai, verbose=1)

    ai.getInput("training")
    model.learn(total_timesteps=ai.metadata_boardsPerEpoch * ai.metadata_maxActionsPerBoard)

    obs = ai.reset()
    done = False
    while not done:
        action, _states = model.predict(obs)
        obs, reward, done, info = ai.step(action)
        print(f"Observation: {obs}, Reward: {reward}")
