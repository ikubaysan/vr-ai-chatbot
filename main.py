import logging
import time
from modules.helpers.logging_helper import logger
from modules.OpenAIAPIClient import APIClient, ConversationContainer, Conversation, Dialogue, get_num_tokens_from_string
from modules.SpeechToText import SpeechToText
from modules.TextToSpeech import TextToSpeech
from modules.PyAudioWrapper import PyAudioWrapper
from modules.OpenAIAPIClient import APIClient
from modules.enums.ActionEnum import ActionEnum
from modules.Config import Config
from modules.Actions import Actions
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
    #keyword_entries = [(bot_name, 0.95)]
    keyword_entries = None
    speech_to_text = SpeechToText(device_index=listening_device.device_index,
                                  keyword_entries=keyword_entries,
                                  credentials_json_file_path='google_cloud_credentials.json'
                                  )
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
                     system_message=config.system_message,
                     forced_system_message=config.forced_system_message
                     )


    conversation_uuid = None
    consecutive_confused_responses = 0
    speech_to_text.set_engine("sphinx")

    actions = Actions(window_title="NeosVR")
    actions.start()

    while True:
        # Check if the transcription queue has any messages
        if speech_to_text.transcription:
            transcribed_message = speech_to_text.transcription.pop(0)
            transcribed_message = transcribed_message.strip().lower()
            logger.info(f"Transcribed message: {transcribed_message}")

            if not conversation_uuid and bot_name in transcribed_message.lower():
                logger.info("Starting new conversation")
                # We want to transcribe the latest audio chunk using Google's speech-to-text engine
                # because it's more accurate than Sphinx.

                # Set the speech-to-text engine to Google
                speech_to_text.set_engine("google")

                try:
                    transcribed_message = speech_to_text._transcribe_from_audio_data(speech_to_text.latest_audio_chunk)
                except Exception as e:
                    logger.error(f"Error transcribing audio with Google Cloud: {e} - using Sphinx transcription instead")
                    transcribed_message = None

                logger.info(f"New transcribed message: {transcribed_message}")
                conversation_uuid = str(uuid4())
                logger.info(f"New conversation UUID: {conversation_uuid}")
                actions.enqueue_action(ActionEnum.NOD_HEAD)

            end_keywords = ["bye", "goodbye", "quit", "exit"]
            transcribed_message_words = transcribed_message.split()
            if any(end_keyword in transcribed_message_words for end_keyword in end_keywords):
                conversation_uuid = None
                logger.info(f"Ending conversation due to goodbye: {conversation_uuid}")
                text_to_speech.speak_on_device("Goodbye", speaking_device)
                continue

            if conversation_uuid is None:
                continue

            openai_response = openai_api_client.send_prompt(
                prompt=transcribed_message,
                conversation_id=conversation_uuid
            )

            logger.info(f"OpenAI response: {openai_response}")
            end_conversation = False

            if "TYPE_ENDING" in openai_response:
                openai_response = openai_response.replace("TYPE_ENDING", "")
                logger.info(f"Ending conversation due to TYPE_ENDING: {conversation_uuid}")
                end_conversation = True
            elif "TYPE_CONFUSED" in openai_response:
                openai_response = openai_response.replace("TYPE_CONFUSED", "")
                consecutive_confused_responses += 1
                if consecutive_confused_responses > 3:
                    logger.info(f"Ending conversation due to consecutive TYPE_CONFUSED responses: {conversation_uuid}")
                    end_conversation = True
            elif "TYPE_NORMAL" in openai_response:
                openai_response = openai_response.replace("TYPE_NORMAL", "")
                consecutive_confused_responses = 0
            elif "TYPE_YES" in openai_response:
                openai_response = openai_response.replace("TYPE_YES", "")
                actions.enqueue_action(ActionEnum.NOD_HEAD)
                actions.enqueue_action(ActionEnum.NOD_HEAD)
            elif "TYPE_NO" in openai_response:
                openai_response = openai_response.replace("TYPE_NO", "")
                actions.enqueue_action(ActionEnum.SHAKE_HEAD)

            text_to_speech.speak_on_device(openai_response, speaking_device)

            if end_conversation:
                conversation_uuid = None
                consecutive_confused_responses = 0
                text_to_speech.speak_on_device("Ended conversation", speaking_device)
                speech_to_text.set_engine("sphinx")

        time.sleep(0.001)

    pass