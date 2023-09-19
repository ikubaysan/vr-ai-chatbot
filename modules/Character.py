from abc import ABC, abstractmethod
from modules.Actions import Actions
from modules.helpers.logging_helper import logger


class State(ABC):

    @property
    @abstractmethod
    def is_wandering(self):
        return False

    @property
    @abstractmethod
    def is_conversing(self):
        return False

    @property
    @abstractmethod
    def is_performing_action(self):
        return False


class WanderingState(State):

    @property
    def is_wandering(self):
        return True

    # define other behaviors related to Wandering state
    def execute(self):
        logger.info("Wandering around...")


class ConversingState(State):

    @property
    def is_conversing(self):
        return True

    # define other behaviors related to Conversing state
    def execute(self):
        logger.info("Engaging in conversation...")


class PerformingActionState(State):

    @property
    def is_performing_action(self):
        return True

    # define other behaviors related to PerformingAction state
    def execute(self):
        logger.info("Performing an action...")


class Character:

    def __init__(self, name: str, window_title: str):
        self.state = None
        self.name = name
        self.conversation_uuid = None
        self.consecutive_confused_responses = 0
        self.actions = Actions(window_title=window_title)
        self.actions.start()
        logger.info(f"Character '{self.name}' targeting window '{window_title}' initialized.")
        self.set_state(WanderingState())

    def set_state(self, state):
        self.state = state

    def update(self):
        # Here you would usually call self.state.execute() or something similar
        # to run the logic associated with the current state.
        pass