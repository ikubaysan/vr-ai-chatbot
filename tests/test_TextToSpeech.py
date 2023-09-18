import pytest
import TextToSpeech
import os

@pytest.fixture
def text_to_speech():
    return TextToSpeech.TextToSpeech()

def create_temp_folder() -> str:
    # Create a temporary folder to store audio files
    temporary_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
    if not os.path.exists(temporary_folder):
        os.mkdir(temporary_folder)
    return temporary_folder

def test_TextToSpeech_speak(text_to_speech: TextToSpeech.TextToSpeech):
    text_to_speech.speak("Hello, this is a test.")

def test_TextToSpeech_speak_to_file(text_to_speech: TextToSpeech.TextToSpeech):
    # Save to a .wav file in a temporary folder
    temporary_folder = create_temp_folder()
    filepath = os.path.join(temporary_folder, "test.wav")
    text_to_speech.speak_to_file("Hello, this is a test.", filepath)
    assert os.path.exists(filepath)

