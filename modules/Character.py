from abc import ABC, abstractmethod
from modules.Actions import Actions
from modules.helpers.logging_helper import logger
from modules.SpeechToText import SpeechToText
from modules.TextToSpeech import TextToSpeech
from modules.AudioDevice import AudioDevice
from modules.enums.ActionEnum import ActionEnum
from uuid import uuid4

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