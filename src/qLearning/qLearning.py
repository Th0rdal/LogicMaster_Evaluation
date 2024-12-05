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

from src.exceptions.StopSignalSentException import StopSignalSentException
from src.factors.position_calculator import positionCalculator
from src.params import Params
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

    metadata = {}
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

    def decodeAction(self, encodedAction):
        """
        Decodes the action of the model. The action is defined as an integer, which is being decoded.
        @param encodedAction: The encoded action taken by the model
        @return: The decoded action (list of elements containing how each param should be adjusted)
        """
        params = []
        for _ in range(Params.totalParameter):
            params.append(self.bitsToState[encodedAction % 3])
            encodedAction //= 3
        return params

    def step(self, action):
        """
        This is a single step taken during training. A step is a single action taken by the AI.

        Each board give the model metadata["maxActionsPerBoard"] actions per board.
        Each board contains metadata["boardsPerEpoch"] boards per epoch.
        @param action: The action the model took (= changes to do to the params)
        @return: observation, reward, done, info (defined by the model)
        """

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
        logger.info(f"actual: {actualResult}")
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
        """
        Handles resetting all needed values to allow for a new training board.
        @param kwargs:
        @return:
        """
        Params.reset()

        self.episodeChangesDone = []
        self.inputChanges = {}
        self.stepChanges = {}

        self.loadNewInput()

        return np.concatenate((np.array(Params.params[:5]), np.array([self.current_error])))

    def loadNewInput(self):
        """
        Loads a new board during a training episode. Also creates a new inputChanges object to receive the results.
        @return: True if there is no new board and the episode is finished, else false
        """
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
        """
        Configures the inputProcessing object and loads the next board.
        @param boardType: training if it should load training. Testing if it should load teseting
        @return: None
        """
        self.inputProcessor.loadNextSet(boardType)
        self.inputGenerator = self.inputProcessor.getInputBoard()

    def startTraining(self):
        """
        Handles the training for a single episode. Results will be logged in the logger
        @return: None
        """
        logger.info("Starting training!")
        logger.info(f"Episode {self.inputProcessor.index}")


        ai.getInput("training")
        model.learn(total_timesteps=self.metadata["boardsPerEpoch"] * self.metadata["maxActionsPerBoard"],
                    callback = StopTrainingCallback(verbose=1))

    def startTesting(self):
        """
        Handles the testing for a single episode. Results will be logged in the logger.
        @return: None
        """
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

        logger.info(f"test results:")
        for element in results:
            logger.info(f"\t{element}")

    def loadEnvVars(self):
        """
        Loads metadata dict with the needed environment variables.
        @return:
        """
        try:
            self.metadata["threshold"] = float(os.getenv("THRESHOLD"))
            self.metadata["maxActionsPerBoard"] = int(os.getenv("MAX_ACTIONS_PER_BOARD"))
            self.metadata["boardsPerEpoch"] = int(os.getenv("BOARDS_PER_EPOCH"))
            self.metadata["learning_rate"] = float(os.getenv("LEARNING_RATE"))
        except ValueError as e:
            logger.error(f"Error: {e}")
        logging.info("Loaded env variables successfully!")

    def startLoop(self):
        """
        This is the main loop of the training/testing of the model
        @return: None
        """
        logger.info("Loading env variables")
        self.loadEnvVars()

        logger.info("Starting model loop!")
        try:
            self.startTraining()
            self.startTesting()
        except StopSignalSentException as e:
            logger.info(e)
        except Exception as e:
            logger.error(f"Error {e}")
            logger.info(f"Input: {ai.inputChanges}")
            logger.info(f"Episode: {ai.episodeChangesDone}")
        model.save(modelPath)
        with open("/app/model/ai.pkl", "wb") as f:
            ai.inputGenerator = None
            pickle.dump(ai, f)


if __name__ == '__main__':
    ai = None
    model = None
    modelPath = "/app/model/qlearning.zip"

    # configure logging. LOGGING_LEVEL env set to DEBUG will result in debug logging
    # logging level must be set to INFO at least for results to be printed
    level = logging.INFO
    if os.getenv("LOGGING_LEVEL") == "DEBUG":
        level = logging.DEBUG
    logging.basicConfig(level=level,
                        format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
                        handlers=[logging.StreamHandler(sys.stdout)])
    logger = logging.getLogger(__name__)

    #os.environ["THRESHOLD"] = "0.01"
    #os.environ["MAX_ACTIONS_PER_BOARD"] = "50"
    #os.environ["BOARDs_PER_EPOCH"] = "10"
    #os.environ["LEARNING_RATE"] = "0.001"

    # load model or create new one if no model has been created
    try:
        if os.path.exists(modelPath):
            with open("/app/model/ai.pkl", "rb") as f:
                ai = pickle.load(f)
            model = DQN.load(modelPath, env=ai)
            logger.info("Loaded model successfully!")
        else:
            logger.info("No model found. Creating new model!")
            ai = Qlearning(positionCalculator)
            model = DQN("MlpPolicy", ai, verbose=1)
            logger.info("Model created successfully!")
        ai.startLoop()

    except Exception as e:
        logger.error(f"Error {e}")


