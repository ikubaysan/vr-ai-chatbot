import pytest
import PyAudioWrapper
import TextToSpeech
import SpeechToText

@pytest.fixture
def py_audio_wrapper():
    return PyAudioWrapper.PyAudioWrapper()

@pytest.fixture
def text_to_speech():
    return TextToSpeech.TextToSpeech()

@pytest.fixture
def speech_to_text():
    return SpeechToText.SpeechToText()