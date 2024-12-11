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

level = logging.INFO
if os.getenv("LOGGING_LEVEL") == "DEBUG":
    level = logging.DEBUG
logging.basicConfig(level=level,
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


class aiBase(gym.Env):

    metadata = {}
    bitsToState = {0: -1, 1: 1}

    def __init__(self, parent, targetFunction):
        super(parent, self).__init__()

        # create actions space. Each variable can be slightly increased, stay the same or be slightly decreased. Each parameter can be changed in any of these 3 ways
        self.input = None
        self.currentActionCount = 0
        self.inputGenerator = None
        self.inputProcessor = InputProcessor()
        self.action_space = spaces.Discrete(2 ** 7 - 1)

        # create observation space. It defines the state space that the environment provides to the agent.
        # Each param is constrained between -10 and 10 with a possible error of -inf to inf.
        self.observation_space = spaces.Box(
            low = np.array([[-10] * Params.totalParameter + [-float('inf')]]),
            high = np.array([[10] * Params.totalParameter + [float('inf')]]),
            dtype = np.float64
        )

        self.target_function = targetFunction
        self.expected_output = 0
        self.current_error = float('inf')

        self.reward = 0
        self.actualReward = 0
        self.observation = None

        self.episodeChangesDone = []
        self.stepChanges = {}
        self.inputChanges = {}

    def decodeAction(self, encodedAction):
        """
        Decodes the action of the model. The action is defined as an integer, which is being decoded.

        An action is in the range of 0 and 2^7-1. The first 6 bits are an encoded form of the parameter to change.
        The last bit reflects the action to do with the selected param.
        @param encodedAction: The encoded action taken by the model
        @return: The decoded action (list of elements containing how each param should be adjusted)
        """
        params = [0] * Params.totalParameter
        param = encodedAction & (2 ** Params.totalParameter - 1) # get the first 6 bites which encode the parameter
        changeBit = (encodedAction >> Params.totalParameter) & 0b1
        if param < Params.totalParameter:
            params[param] = self.bitsToState[changeBit]
        return params

    def preStep(self, action):
        """
        This is a single step taken during training. A step is a single action taken by the AI.

        Each board give the model metadata["maxActionsPerBoard"] actions per board.
        Each board contains metadata["boardsPerEpoch"] boards per epoch.
        @param action: The action the model took (= changes to do to the params)
        @return: observation, reward, done, info (defined by the model)
        """

        self.stepChanges =  {}
        self.stepChanges = {"action": action}

        # run function and return actual and expected output
        self.actualResult = self.target_function(self.input)
        self.stepChanges["actualResult"] = self.actualResult


    def postStep(self):
        observation = np.concatenate([Params.params, np.array([self.current_error])])
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

        self.stepChanges = {}
        return observation, done, self.stepChanges


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

        return np.concatenate((Params.params, np.array([self.current_error])))

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
        #except Exception as e:
        #    logger.error(f"Error {e}")
        #    logger.info(f"Input: {ai.inputChanges}")
        #    logger.info(f"Episode: {ai.episodeChangesDone}")
        model.save(modelPath)
        with open("/app/model/ai.pkl", "wb") as f:
            ai.inputGenerator = None
            pickle.dump(ai, f)


