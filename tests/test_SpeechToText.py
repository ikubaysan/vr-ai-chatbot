from modules import SpeechToText, TextToSpeech
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
    text_to_speech.speak_to_file("Hello, this is a test", filepath)
    assert os.path.exists(filepath)
    transcription = speech_to_text.transcribe_from_audio_file(filepath)
    assert transcription == "hello this is a test"


def test_SpeechToText_transcribe_from_audio_file_google(text_to_speech: TextToSpeech.TextToSpeech, speech_to_text: SpeechToText.SpeechToText):
    # Save to a .wav file in a temporary folder
    temporary_folder = create_temp_folder()
    filepath = os.path.join(temporary_folder, "test.wav")
    text_to_speech.speak_to_file("Hello, this is a test, using Google", filepath)
    assert os.path.exists(filepath)

    speech_to_text.credentials_json_file_path = "../google_cloud_credentials.json"
    speech_to_text.set_engine("google")
    transcription = speech_to_text.transcribe_from_audio_file(filepath)
    assert transcription.lower().strip() == "hello this is a test using google"
