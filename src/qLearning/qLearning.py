import copy
import sys
import chess
import gym
from gym import spaces
import numpy as np
from stable_baselines3 import DQN
import logging

from src.factors.position_calculator import positionCalculator
from src.params import Params
from src.stockfish import getExpectedResult
from src.inputProcessing import InputProcessor
"""
import os


def print_directory_tree(start_path, level=0):
    try:
        # Print the current directory
        indent = " " * (level * 4)  # Indentation for subdirectories
        print(f"{indent}{os.path.basename(start_path)}/")

        # List all items in the current directory
        for entry in os.listdir(start_path):
            entry_path = os.path.join(start_path, entry)
            if os.path.isdir(entry_path):
                # Recurse into subdirectory
                print_directory_tree(entry_path, level + 1)
            else:
                # Print file with appropriate indentation
                print(f"{indent}    {entry}")
    except PermissionError:
        # Skip directories/files you don't have permissions for
        print(f"{indent}    [Permission Denied]")
    except FileNotFoundError:
        # Skip directories that might disappear during traversal
        print(f"{indent}    [File Not Found]")
    except Exception as e:
        # Catch all other errors
        print(f"{indent}    [Error: {e}]")


print_directory_tree("/app")"""

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger(__name__)


class Qlearning(gym.Env):

    metadata = {
        "threshold": 0.01,
        "maxActionsPerBoard" : 50,
        "boardsPerEpoch" : 1024,
        "learning_rate" : 0.001
    }
    stateToBits = {-1: 1, 0: 0, 1: 2}
    bitsToState = {1: -1, 0: 0, 2: 1}

    def __init__(self, targetFunction):
        super(Qlearning, self).__init__()

        # create actions space. Each variable can be slightly increased, stay the same or be slightly decreased. Each parameter can be changed in any of these 3 ways
        self.input = None
        self.currentActionCount = 0
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
        self.episodeChangesDone = []
        self.stepChanges = {}
        self.inputChanges = {}

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
        self.stepChanges = {}
        self.stepChanges = {"action": action}

        decodedAction = self.decodeAction(action)
        self.stepChanges["decodedAction"] = decodedAction
        delta = np.array(decodedAction) - 1
        self.stepChanges["paramChanges"] = []
        Params.params += (delta * self.metadata["learning_rate"])
        self.stepChanges["paramChanges"].append(delta * self.metadata["learning_rate"])

        # run function and return actual and expected output
        actualResult = self.target_function(self.input)
        logging.info(f"actual: {actualResult}")
        self.stepChanges["actualResult"] = actualResult

        #calculate error and reward
        self.current_error = abs(self.expected_output - actualResult)
        reward = -self.current_error

        self.stepChanges["error"] = self.current_error
        self.stepChanges["reward"] = reward

        observation = np.concatenate((np.array(Params.params[:5]), np.array([self.current_error])))
        self.stepChanges["observation"] = observation

        done = self.current_error < self.metadata["threshold"]

        self.stepChanges["currentActionCounter"] = self.currentActionCount
        self.currentActionCount += 1
        self.inputChanges["steps"].append(copy.deepcopy(self.stepChanges))
        if self.currentActionCount == self.metadata["maxActionsPerBoard"]:
            logger.info(f"Board {self.inputProcessor.boardCounter} ({self.inputProcessor.currentBoardType}) results: {self.inputChanges}")
            self.episodeChangesDone.append(copy.deepcopy(self.inputProcessor.boardCounter))
            done = self.loadNewInput()
            if done:
                self.episodeChangesDone.append(self.inputChanges)
                logger.info(f"Episode {self.inputProcessor.index} ({self.inputProcessor.currentBoardType}) results: {self.episodeChangesDone}")

            self.currentActionCount = 0

        return observation, reward, done, self.stepChanges

    def reset(self, **kwargs):
        for element in Params.params:
            element += np.random.uniform(-5, 5)

        self.episodeChangesDone = []
        self.inputChanges = {}
        self.stepChanges = {}

        self.loadNewInput()

        return np.concatenate((np.array(Params.params[:5]), np.array([self.current_error])))

    def loadNewInput(self):
        self.inputChanges = {}

        self.input = chess.Board(next(self.inputGenerator))
        if self.input is None:
            return True
        else:
            self.inputChanges["input"] = self.input
            self.expected_output = getExpectedResult(self.input)
            self.inputChanges["expectedResult"] = self.expected_output
            computed_value = self.target_function(self.input)
            self.current_error = abs(self.expected_output - computed_value)
            self.inputChanges["initialResult"] = computed_value
            self.inputChanges["initialError"] = self.current_error
            self.inputChanges["steps"] = []
        return False

    def getInput(self, boardType):
        self.inputProcessor.loadNextSet(boardType)
        self.inputGenerator = self.inputProcessor.getInputBoard()

    def startTraining(self):
        logger.info("Starting training!")
        logger.info(f"Episode {self.inputProcessor.index}")

        ai.getInput("training")
        model.learn(total_timesteps=self.metadata["boardsPerEpoch"] * self.metadata["maxActionsPerBoard"])

    def startTesting(self):
        logger.info("Starting testing!")
        logger.info(f"Episode {self.inputProcessor.index}")

        ai.getInput("testing")
        obs = ai.reset()
        done = False
        results = []
        while not done:
            #action, _states = model.predict(obs)
            #obs, reward, done, info = ai.step(action)
            #print(f"Observation: {obs}, Reward: {reward}, actual: {info["actual"]}, expected: {info["expected"]}")
            result = self.target_function()
            results.append(result)

if __name__ == '__main__':
    ai = Qlearning(positionCalculator)
    model = DQN("MlpPolicy", ai, verbose=1)
    print("WORKING")

    ai.startTraining()
    ai.startTesting()

