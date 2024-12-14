import copy
import os.path
import pickle
import logging

import chess
import gym
from gym import spaces
import numpy as np
from src.exceptions.StopSignalSentException import StopSignalSentException
from src.exceptions.StopTrainingCallback import StopTrainingCallback
from src.inputProcessing import InputProcessor

logger = logging.getLogger(__name__)

class BaseEnvironment(gym.Env):

    metadata = {}
    bitsToState = {0: -1, 1: 1}
    amountOfOptions = 10 ** 3

    def __init__(self, actionSpace):
        super(BaseEnvironment, self).__init__()

        # create actions space. Each variable can be slightly increased, stay the same or be slightly decreased. Each parameter can be changed in any of these 3 ways
        self.input = None
        self.currentActionCount = 0
        self.inputGenerator = None
        self.inputProcessor = InputProcessor()
        self.action_space = actionSpace

        # create observation space. It defines the state space that the environment provides to the agent.
        # Each param is constrained between -10 and 10 with a possible error of -inf to inf.
        self.observation_space = spaces.Box(
            low = np.array([-10] * 2 + [-float('inf')] + [0] * 8),
            high = np.array([10] * 2 + [float('inf')] + [2 ** 63] * 8),
            dtype = np.float64
        )

        self.expected_output = 0
        self.current_error = float('inf')
        self.episodeChangesDone = []
        self.stepChanges = {}
        self.inputChanges = {}

        self.ai = None
        self.model = None
        self.modelPath = ""

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

        if type(action) == np.ndarray:
            action = action[0]

        delta = (action - self.amountOfOptions)
        actualResult = delta * self.metadata["learning_rate"]
        self.stepChanges["actualResult"] = actualResult

        #calculate error and reward
        self.current_error = abs(self.expected_output - actualResult)
        reward = -self.current_error

        self.stepChanges["error"] = self.current_error
        self.stepChanges["reward"] = reward

        observation = np.array(
            [actualResult, self.expected_output, self.current_error,
             self.input.occupied_co[chess.WHITE],
             self.input.occupied_co[chess.BLACK],
             self.input.pawns,
             self.input.knights,
             self.input.bishops,
             self.input.rooks,
             self.input.queens,
             self.input.kings
        ])
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

        self.episodeChangesDone = []
        self.inputChanges = {}
        self.stepChanges = {}

        self.loadNewInput()

        return np.array([0] * 11)

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
        computed_value = 2#self.target_function(self.input)
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


        self.getInput("training")
        self.model.learn(total_timesteps=self.metadata["boardsPerEpoch"] * self.metadata["maxActionsPerBoard"],
                    callback = StopTrainingCallback(verbose=1))

    def startTesting(self):
        """
        Handles the testing for a single episode. Results will be logged in the logger.
        @return: None
        """
        logger.info("Starting testing!")
        logger.info(f"Episode {self.inputProcessor.index}")

        self.ai.getInput("testing")
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
            result = 4#self.target_function(self.input)
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
        while True:
            try:
                self.startTraining()
                self.startTesting()
            except StopSignalSentException as e:
                logger.info(e)
                break
            #except Exception as e:
                #logger.error(f"Error {e}")
                #logger.info(f"Input: {self.ai.inputChanges}")
                #logger.info(f"Episode: {self.ai.episodeChangesDone}")
                #break
        self.model.save(self.modelPath)
        with open("/app/model/ai.pkl", "wb") as f:
            self.inputGenerator = None
            self.ai = None
            self.model = None
            self.modelPath = None
            pickle.dump(self, f)

    def configModelAndAI(self, model, modelPath):
        self.ai = self
        self.model = model
        self.modelPath = modelPath