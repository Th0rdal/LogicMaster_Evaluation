import copy
import os.path
import pickle
import sys
import chess
import gym
from gym import spaces
import numpy as np
from stable_baselines3 import DQN
import logging

from stable_baselines3.common.callbacks import BaseCallback

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

class StopTrainingCallback(BaseCallback):
    def _on_step(self) -> bool:
        # Check if a new episode has started
        if self.locals.get("dones") is not None and any(self.locals["dones"]):
            print(f"Episode done!")
            return False  # Returning False stops training
        return True

    def __init__(self, verbose=0):
        super(StopTrainingCallback, self).__init__(verbose)
        self.episodeCount = 0


class Qlearning(gym.Env):

    metadata = {
        "threshold": 0.01,
        "maxActionsPerBoard" : 50,
        "boardsPerEpoch" : 10,
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

        try:
            line = next(self.inputGenerator).split(":")
        except StopIteration:
            return True

        self.input = chess.Board(line[0])
        self.expected_output = float(line[1])
        self.inputChanges["input"] = self.input
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

    def startTraining(self, skipIndex=0):
        logger.info("Starting training!")
        logger.info(f"Episode {self.inputProcessor.index}")


        ai.getInput("training")
        for _ in range(skipIndex):
            next(self.inputGenerator)
        model.learn(total_timesteps=self.metadata["boardsPerEpoch"] * self.metadata["maxActionsPerBoard"],
                    callback = StopTrainingCallback(verbose=1))

    def startTesting(self):
        logger.info("Starting testing!")
        logger.info(f"Episode {self.inputProcessor.index}")

        ai.getInput("testing")
        results = []
        self.input = None

        while True:
            testInfo = {}
            try:
                line = next(self.inputGenerator).split(":")
            except StopIteration:
                break

            self.input = chess.Board(line[0])
            self.expected_output = float(line[1])
            result = self.target_function(self.input)
            testInfo["actualResult"] = result
            results.append(testInfo)

        logging.info(f"test results:")
        for element in results:
            logging.info(f"\t{element}")

if __name__ == '__main__':
    ai = None
    model = None
    modelPath = "/app/model/qlearning.zip"

    try:

        if os.path.exists(modelPath):
            with open("/app/model/ai.pkl", "rb") as f:
                ai = pickle.load(f)
            model = DQN.load(modelPath, env=ai)
        else:
            ai = Qlearning(positionCalculator)
            model = DQN("MlpPolicy", ai, verbose=1)
        print("WORKING")

        ai.startTraining()
        ai.startTesting()

    except Exception as e:
        logger.info(f"Error {e}")
        logger.info(f"Input: {ai.inputChanges}")
        logger.info(f"Episode: {ai.episodeChangesDone}")
    model.save(modelPath)
    with open("/app/model/ai.pkl", "wb") as f:
        ai.inputGenerator = None
        pickle.dump(ai, f)


