import logging
import time
from modules.helpers.logging_helper import logger
from modules.OpenAIAPIClient import APIClient, ConversationContainer, Conversation, Dialogue, get_num_tokens_from_string
from modules.SpeechToText import SpeechToText
from modules.TextToSpeech import TextToSpeech
from modules.PyAudioWrapper import PyAudioWrapper


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

    while True:
        if speech_to_text.transcription:
            transcribed_message = speech_to_text.transcription.pop(0)
            logger.info(f"Transcribed message: {transcribed_message}")
            text_to_speech.speak_on_device(transcribed_message, speaking_device)
        time.sleep(0.001)

    pass