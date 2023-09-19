import time
from modules.helpers.logging_helper import logger
from modules.SpeechToText import SpeechToText
from modules.TextToSpeech import TextToSpeech
from modules.PyAudioWrapper import PyAudioWrapper
from modules.OpenAIAPIClient import APIClient
from modules.enums.ActionEnum import ActionEnum
from modules.Character import Character
from modules.Config import Config
from uuid import uuid4
import os
from typing import List, Optional, Tuple, Union
from modules.AudioDevice import AudioDevice

def get_audio_devices(speaking_device_name: str, listening_device_name: str) -> Tuple[AudioDevice, AudioDevice]:
    py_audio_wrapper = PyAudioWrapper()
    audio_devices = py_audio_wrapper.get_audio_devices()
    # Speak into the game (Cable A)
    speaking_device = audio_devices.get_input_device_by_name("cable-a")
    # Listen to the game (Cable B)
    listening_device = audio_devices.get_output_device_by_name("cable-b")

    return speaking_device, listening_device


if __name__ == "__main__":

    speaking_device, listening_device = get_audio_devices(speaking_device_name="cable-a", listening_device_name="cable-b")
    logger.info(f"Speaking device: {speaking_device}")
    logger.info(f"Listening device: {listening_device}")

    # Create a TextToSpeech object
    text_to_speech = TextToSpeech()
    # Create a SpeechToText object
    speech_to_text = SpeechToText(device_index=listening_device.device_index,
                                  credentials_json_file_path='google_cloud_credentials.json')
    speech_to_text.start()
    speech_to_text.set_engine("sphinx")
    logger.info("Listening for audio")

    character = Character(name="ringo",
                          window_title="NeosVR",
                          text_to_speech=text_to_speech,
                          speech_to_text=speech_to_text,
                          speaking_device=speaking_device,
                          listening_device=listening_device)
    logger.info(f"Bot name: {character.name}")

    config = Config(os.path.join('config.ini'))
    openai_api_client = APIClient(base_url=config.base_url,
                     path=config.path,
                     api_key=config.api_key,
                     model=config.model,
                     max_conversation_tokens=config.max_conversation_tokens,
                     max_response_tokens=config.max_response_tokens,
                     temperature=config.temperature,
                     conversation_prune_after_seconds=config.conversation_prune_after_seconds,
                     max_dialogues_per_conversation=config.max_dialogues_per_conversation,
                     system_message=config.system_message,
                     forced_system_message=config.forced_system_message
                     )

    while True:
        # Check if the transcription queue has any messages
        if speech_to_text.transcription:
            transcribed_message = speech_to_text.transcription.pop(0)
            transcribed_message = transcribed_message.strip().lower()
            logger.info(f"Transcribed message: {transcribed_message}")

            if character.state.is_wandering and character.name in transcribed_message.lower():
                logger.info("Starting new conversation")
                character.start_conversation()
                try:
                    transcribed_message = speech_to_text._transcribe_from_audio_data(speech_to_text.latest_audio_chunk)
                except Exception as e:
                    logger.error(f"Error transcribing audio with Google Cloud: {e} - using original Sphinx transcription instead")
                logger.info(f"More accurate transcription using Google Cloud: {transcribed_message}")

            end_keywords = ["bye", "quit", "exit"]
            transcribed_message_words = transcribed_message.split()
            if character.state.is_conversing and any(end_keyword in transcribed_message_words for end_keyword in end_keywords):
                logger.info(f"Ending conversation due to goodbye.")
                character.end_conversation()
                continue

            stop_action_keywords = ["stop", "wait", "hold", "pause"]
            if character.state.is_performing_action and any(stop_action_keyword in transcribed_message_words for stop_action_keyword in stop_action_keywords):
                logger.info(f"Stopping action due to stop keyword.")
                character.actions.stop_flag = True
                character.set_state(character.previous_state)
                continue

            if not character.state.is_conversing:
                continue

            openai_response = openai_api_client.send_prompt(
                prompt=transcribed_message,
                conversation_id=character.conversation_uuid
            )

            logger.info(f"OpenAI response: {openai_response}")

            if openai_response.startswith("TYPE_NORMAL"):
                # Remove the TYPE_NORMAL prefix
                openai_response = openai_response.replace("TYPE_NORMAL", "")
                character.consecutive_confused_responses = 0
            elif openai_response.startswith("TYPE_ENDING"):
                openai_response = openai_response.replace("TYPE_ENDING", "")
                logger.info(f"Ending conversation due to TYPE_ENDING: {character.conversation_uuid}")
            elif openai_response.startswith("TYPE_CONFUSED"):
                openai_response = openai_response.replace("TYPE_CONFUSED", "")
                character.consecutive_confused_responses += 1
                if character.consecutive_confused_responses > 3:
                    logger.info(f"Ending conversation due to consecutive TYPE_CONFUSED responses: {character.conversation_uuid}")
            elif openai_response.startswith("TYPE_YES"):
                openai_response = openai_response.replace("TYPE_YES", "")
                character.actions.enqueue_action(ActionEnum.NOD_HEAD_TWICE)
            elif openai_response.startswith("TYPE_NO"):
                openai_response = openai_response.replace("TYPE_NO", "")
                character.actions.enqueue_action(ActionEnum.SHAKE_HEAD)
            elif openai_response.startswith("TYPE_CMD_TURN"):
                left_turn_keywords = ["left", "counter"]
                if any(left_turn_keyword in transcribed_message_words for left_turn_keyword in left_turn_keywords):
                    character.actions.enqueue_action(ActionEnum.TURN_LEFT_UNTIL_STOP_FLAG)
                else:
                    character.actions.enqueue_action(ActionEnum.TURN_RIGHT_UNTIL_STOP_FLAG)
            elif openai_response.startswith("TYPE_CMD_FORWARD"):
                character.actions.enqueue_action(ActionEnum.MOVE_FORWARD_UNTIL_STOP_FLAG)
            elif openai_response.startswith("TYPE_CMD_BACK"):
                character.actions.enqueue_action(ActionEnum.MOVE_BACK_UNTIL_STOP_FLAG)

            text_to_speech.speak_on_device(openai_response, speaking_device)

            if "TYPE_ENDING" in openai_response or character.consecutive_confused_responses > 3:
                logger.info(f"Ending conversation: {character.conversation_uuid}")
                character.end_conversation()

        time.sleep(0.001)

    pass