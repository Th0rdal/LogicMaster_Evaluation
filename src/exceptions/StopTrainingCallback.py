from stable_baselines3.common.callbacks import BaseCallback


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
