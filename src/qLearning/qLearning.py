
import os.path
import pickle
import sys
from gym import spaces
from stable_baselines3 import DQN
import logging

from src.baseEnvironment import BaseEnvironment
from src.exceptions.StopSignalSentException import StopSignalSentException

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
            ai.configModelAndAI(model, modelPath)
            logger.info("Loaded model successfully!")
        else:
            logger.info("No model found. Creating new model!")
            ai = BaseEnvironment(spaces.Discrete(2 * BaseEnvironment.amountOfOptions))
            model = DQN("MlpPolicy", ai, verbose=1)
            ai.configModelAndAI(model, modelPath)
            logger.info("Model created successfully!")
        ai.startLoop()

    except StopSignalSentException as e:
        logger.error(f"Error {e}")


