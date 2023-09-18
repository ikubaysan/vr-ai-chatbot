import pytest
import TextToSpeech
import SpeechToText
import os

def create_temp_folder() -> str:
    # Create a temporary folder to store audio files
    temporary_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
    if not os.path.exists(temporary_folder):
        os.mkdir(temporary_folder)
    return temporary_folder

def test_SpeechToText_transcribe_from_audio_file(text_to_speech: TextToSpeech.TextToSpeech, speech_to_text: SpeechToText.SpeechToText):
    # Save to a .wav file in a temporary folder
    temporary_folder = create_temp_folder()
    filepath = os.path.join(temporary_folder, "test.wav")
    text_to_speech.speak_to_file("Hello, this is a test.", filepath)
    assert os.path.exists(filepath)
    transcription = speech_to_text.transcribe_from_audio_file(filepath)
    assert transcription == "hello this is a test"

