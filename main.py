import logging
import time
from modules.helpers.logging_helper import logger
from modules.OpenAIAPIClient import APIClient, ConversationContainer, Conversation, Dialogue, get_num_tokens_from_string
from modules.SpeechToText import SpeechToText
from modules.TextToSpeech import TextToSpeech
from modules.PyAudioWrapper import PyAudioWrapper
from modules.OpenAIAPIClient import APIClient
from modules.Config import Config
from uuid import uuid4
import os


if __name__ == "__main__":

    py_audio_wrapper = PyAudioWrapper()
    audio_devices = py_audio_wrapper.get_audio_devices()
    # Speak into the game (Cable A)
    speaking_device = audio_devices.get_input_device_by_name("cable-a")

    # Listen to the game (Cable B)
    listening_device = audio_devices.get_output_device_by_name("cable-b")

    logger.info(f"Speaking device: {speaking_device}")
    logger.info(f"Listening device: {listening_device}")

    bot_name = "ringo"
    logger.info(f"Bot name: {bot_name}")

    # Create a SpeechToText object
    keyword_entries = [(bot_name, 0.9)]
    speech_to_text = SpeechToText(device_index=listening_device.device_index, keyword_entries=keyword_entries)
    speech_to_text.start()
    logger.info("Listening for audio")

    # Create a TextToSpeech object
    text_to_speech = TextToSpeech()

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
                     system_message=config.system_message
                     )


    conversation_uuid = None
    consecutive_confused_responses = 0
    #conversation_uuid = str(uuid4())

    while True:
        if speech_to_text.transcription:
            transcribed_message = speech_to_text.transcription.pop(0)
            logger.info(f"Transcribed message: {transcribed_message}")

            if "ringo" in transcribed_message:
                conversation_uuid = str(uuid4())
                logger.info(f"New conversation: {conversation_uuid}")

            if conversation_uuid is None:
                continue

            openai_response = openai_api_client.send_prompt(
                prompt=transcribed_message,
                conversation_id=conversation_uuid
            )

            logger.info(f"OpenAI response: {openai_response}")
            text_to_speech.speak_on_device(openai_response, speaking_device)

            if "ENDING" in openai_response:
                conversation_uuid = None
                logger.info(f"Ending conversation due to ENDING: {conversation_uuid}")
                text_to_speech.speak_on_device("Ended conversation", speaking_device)

            if "CONFUSED" in openai_response:
                consecutive_confused_responses += 1
                if consecutive_confused_responses > 3:
                    conversation_uuid = None
                    consecutive_confused_responses = 0
                    logger.info(f"Ending conversation due to consecutive CONFUSED responses: {conversation_uuid}")
                    text_to_speech.speak_on_device("Ended conversation", speaking_device)

        time.sleep(0.001)

    pass