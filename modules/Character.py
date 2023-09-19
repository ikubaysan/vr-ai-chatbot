from abc import ABC, abstractmethod
from modules.Actions import Actions
from modules.helpers.logging_helper import logger
from modules.SpeechToText import SpeechToText
from modules.TextToSpeech import TextToSpeech
from modules.AudioDevice import AudioDevice
from modules.enums.ActionEnum import ActionEnum
from uuid import uuid4
import time

class State(ABC):

    @property
    def is_wandering(self):
        return False

    @property
    def is_conversing(self):
        return False

    @property
    def is_performing_action(self):
        return False


class WanderingState(State):
    MINIMUM_TIME_BETWEEN_ACTIONS = 10.0
    def __init__(self):
        self.last_action_time = 0
        return

    @property
    def is_wandering(self):
        return True

    # define other behaviors related to Wandering state
    def execute(self):
        logger.info("Wandering around...")

    def update_last_action_time(self):
        self.last_action_time = time.time()

    def is_time_to_act(self):
        current_time = time.time()
        time_since_last_action = current_time - self.last_action_time
        return time_since_last_action >= self.MINIMUM_TIME_BETWEEN_ACTIONS


class ConversingState(State):
    def __init__(self):
        return

    @property
    def is_conversing(self):
        return True

    # define other behaviors related to Conversing state
    def execute(self):
        logger.info("Engaging in conversation...")


class PerformingActionState(State):
    def __init__(self):
        return

    @property
    def is_performing_action(self):
        return True

    # define other behaviors related to PerformingAction state
    def execute(self):
        logger.info("Performing an action...")


class Character:

    def __init__(self, name: str, window_title: str,
                 text_to_speech: TextToSpeech,
                 speech_to_text: SpeechToText,
                 speaking_device: AudioDevice,
                 listening_device: AudioDevice
                 ):

        self.speaking_device = speaking_device
        self.listening_device = listening_device
        self.text_to_speech = text_to_speech
        self.speech_to_text = speech_to_text
        self.name = name

        self.state = None
        self.previous_state = None
        self.conversation_uuid = None
        self.consecutive_confused_responses = 0
        self.actions = Actions(window_title=window_title)
        self.actions.start()
        logger.info(f"Character '{self.name}' targeting window '{window_title}' initialized.")
        self.set_state(WanderingState())

    def start_conversation(self):
        self.conversation_uuid = str(uuid4())
        self.set_state(ConversingState())
        # We want to transcribe the latest audio chunk using Google's speech-to-text engine
        # because it's more accurate than Sphinx.
        # Set the speech-to-text engine to Google
        self.speech_to_text.set_engine("google")
        self.actions.enqueue_action(ActionEnum.NOD_HEAD)

    def end_conversation(self):
        self.conversation_uuid = None
        self.consecutive_confused_responses = 0
        self.text_to_speech.speak_on_device("Goodbye", self.speaking_device)
        # Revert to less accurate, but local and free speech recognition engine.
        self.speech_to_text.set_engine("sphinx")
        self.set_state(WanderingState())

    def set_state(self, state: State):
        self.previous_state = self.state
        self.state = state
        logger.info(f"Character '{self.name}' state set to '{type(state).__name__}'")

    def update(self):
        self.state.execute()

        if self.state.is_wandering and self.state.is_time_to_act() and self.actions.window_is_focused and not self.actions.action_is_ongoing:
            logger.info(f"Character '{self.name}' is wandering and it's time to act.")
            self.actions.enqueue_random_action()
            self.state.update_last_action_time()