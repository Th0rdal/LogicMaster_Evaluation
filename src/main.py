import os
import logging
import threading
import docker
from datetime import datetime

import chess.engine
from src.globals import LOG_PATH, AI_LOGGING_PATH

# Initialize the Docker client
client = docker.from_env()
if not os.path.exists(LOG_PATH):
    os.makedirs(os.path.dirname(LOG_PATH))
for ai in ["qlearning/", "ppo/", "ddgp/"]:
    if not os.path.exists(AI_LOGGING_PATH+ai):
        os.makedirs(os.path.dirname(AI_LOGGING_PATH+ai))

currentTime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')  # Format the timestamp
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
                    handlers=[logging.FileHandler(LOG_PATH+"logfile_"+str(currentTime)+".txt"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

def runContainer(imageName, container_name, loggingBase):
    client = docker.from_env()

    loggingPath = loggingBase + imageName + "/" + imageName + "_logs_" + str(currentTime) + ".txt"

    # Run the container
    container = client.containers.run(
        image=imageName,
        name=container_name,
        detach=True,
    )

    with open(loggingPath, "w") as file:
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
    logger.info("TEST")

    thread1 = threading.Thread(target=runContainer, args=("qlearning", "container-instance-1", AI_LOGGING_PATH))
    #thread2 = threading.Thread(target=run_container_and_stream_logs, args=("testimage", "container-instance-2"))

    # Start the threads
    thread1.start()
    #thread2.start()
    #docker build -t testimage -f dockerfile_qlearning .
