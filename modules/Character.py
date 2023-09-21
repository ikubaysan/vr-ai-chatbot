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
        self.latest_action_epoch = 0
        return

    @property
    def is_wandering(self):
        return True

    # define other behaviors related to Wandering state
    def execute(self):
        #logger.info("Wandering around...")
        return

    def update_latest_action_epoch(self):
        self.latest_action_epoch = time.time()

    def is_time_to_act(self):
        time_since_last_action = time.time() - self.latest_action_epoch
        return time_since_last_action >= self.MINIMUM_TIME_BETWEEN_ACTIONS


class ConversingState(State):
    CONVERSATION_MAX_INACTIVITY_SECONDS = 60
    def __init__(self):
        self.latest_speech_start_epoch = 0
        self.is_speaking = False
        return

    @property
    def is_conversing(self):
        return True

    def speak(self, text_to_speech: TextToSpeech, text: str, speaking_device: AudioDevice):
        self.latest_speech_start_epoch = time.time()
        self.is_speaking = True
        text_to_speech.speak_on_device(text, speaking_device)
        logger.info(f"Speaking: {text}")
        self.is_speaking = False

    def is_time_to_end_conversation(self):
        time_since_last_speech = time.time() - self.latest_speech_start_epoch
        return self.latest_speech_start_epoch != 0 and time_since_last_speech >= self.CONVERSATION_MAX_INACTIVITY_SECONDS

    # define other behaviors related to Conversing state
    def execute(self):
        #logger.info("Engaging in conversation...")
        return


class PerformingActionState(State):
    def __init__(self):
        self.latest_action_epoch = 0
        return

    @property
    def is_performing_action(self):
        return True

    # define other behaviors related to PerformingAction state
    def execute(self):
        #logger.info("Performing an action...")
        return


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
        self.name = name.lower()

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
        self.actions.enqueue_action(ActionEnum.NOD_HEAD)

    def end_conversation(self):
        self.conversation_uuid = None
        self.consecutive_confused_responses = 0
        self.text_to_speech.speak_on_device("Goodbye", self.speaking_device)
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
            self.state.update_latest_action_epoch()

        if self.state.is_conversing and self.state.is_time_to_end_conversation():
            logger.info(f"Character '{self.name}' is conversing and it's time to end the conversation.")
            self.end_conversation()

        if self.state.is_conversing:
            pass