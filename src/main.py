import os
import logging
import threading
import docker
from datetime import datetime

import chess.engine
from dotenv import dotenv_values

from src.globals import LOG_PATH, AI_LOGGING_PATH

# Initialize the Docker client
client = docker.from_env()
if not os.path.exists(LOG_PATH):
    os.makedirs(os.path.dirname(LOG_PATH))
for ai in ["qlearning/", "ppo/", "ddpg/"]:
    if not os.path.exists(AI_LOGGING_PATH+ai):
        os.makedirs(os.path.dirname(AI_LOGGING_PATH+ai))

currentTime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')  # Format the timestamp
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
                    handlers=[logging.FileHandler(LOG_PATH+"logfile_"+str(currentTime)+".txt"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

def runContainer(imageName, container_name, loggingBase):
    client = docker.from_env()

    save_folder = os.path.abspath("../resources/models/" + imageName)
    loggingPath = loggingBase + imageName + "/" + imageName + "_logs_" + str(currentTime) + ".txt"

    # Run the container
    container = client.containers.run(
        image=imageName,
        name=container_name,
        detach=True,
        volumes={
            host_folder: {
                'bind': container_folder,
                'mode': 'ro'  # Can be 'ro' for read-only or 'rw' for read-write
            },
            save_folder: {
                'bind': "/app/model/",
                'mode': "rw"
            }
        },
        environment=dotenv_values("../.env")
    )

    with open(loggingPath, "w", encoding="utf-8") as file:
        file.write(f"Container {container_name} started with ID {container.id}")

        # Stream logs
        try:
            for log_line in container.logs(stream=True):
                file.write(f"[{container_name}] {log_line.decode('utf-8')}")
        finally:
            # Stop and remove the container
            file.write(f"\nStopping and removing {container_name}...")
            container.stop()
            container.remove()
            file.write(f"Container {container_name} stopped and removed.")

def runPreprocessing():
    loggingPath = LOG_PATH + "/" + "preprocessing/preprocessing_logs_" + str(currentTime) + ".txt"
    container_name = "preprocessing"

    container = client.containers.run(
        container_name,
        detach=True,  # Run container in detached mode
        volumes={
            host_folder : {
                'bind': container_folder,
                'mode': 'rw'  # Can be 'ro' for read-only or 'rw' for read-write
            },
        },
        environment=dotenv_values("../.env")
    )

    with open(loggingPath, "w", encoding="utf-8") as file:
        file.write(f"Container {container_name} started with ID {container.id}")

        # Stream logs
        try:
            for log_line in container.logs(stream=True):
                file.write(f"[{container_name}] {log_line.decode('utf-8')}")
        finally:
            # Stop and remove the container
            file.write(f"\nStopping and removing {container_name}...")
            container.stop()
            container.remove()
            file.write(f"Container {container_name} stopped and removed.")

if __name__ == "__main__":
    fen = "r1bqkbnr/pppppppp/n7/8/8/5N2/PPPPPPPP/RNBQKB1R w KQkq - 0 1"  # Example position
    board = chess.Board(fen)

    host_folder = os.path.abspath("../resources/inputData")

    container_folder = "/app/resources/"


    thread1 = threading.Thread(target=runContainer, args=("qlearning", "qlearning", AI_LOGGING_PATH))
    thread2 = threading.Thread(target=runContainer, args=("ppo", "ppo", AI_LOGGING_PATH))
    thread3 = threading.Thread(target=runContainer, args=("ddpg", "ddpg", AI_LOGGING_PATH))
    thread4 = threading.Thread(target=runPreprocessing)

    # Start the threads
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()


    # docker build -t ai_base -f .\dockerfile_ai_base .
    # docker build -t qlearning -f dockerfile_qlearning .
