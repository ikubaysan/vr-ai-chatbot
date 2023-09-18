from modules import PyAudioWrapper, TextToSpeech
import os

def create_temp_folder() -> str:
    # Create a temporary folder to store audio files
    temporary_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
    if not os.path.exists(temporary_folder):
        os.mkdir(temporary_folder)
    return temporary_folder

def test_speak(text_to_speech: TextToSpeech.TextToSpeech):
    text_to_speech.speak("Hello, this is a test.")

def test_speak_to_file(text_to_speech: TextToSpeech.TextToSpeech):
    # Save to a .wav file in a temporary folder
    temporary_folder = create_temp_folder()
    filepath = os.path.join(temporary_folder, "test.wav")
    text_to_speech.speak_to_file("Hello, this is a test.", filepath)
    assert os.path.exists(filepath)

def test_speak_on_output_device(text_to_speech: TextToSpeech.TextToSpeech, py_audio_wrapper: PyAudioWrapper.PyAudioWrapper):
    audio_devices = py_audio_wrapper.get_audio_devices()
    assert len(audio_devices.audio_devices) > 0
    asus_speaker = audio_devices.get_output_device_by_name("asus")
    text_to_speech.speak_on_device("Hello, this is a test from my asus speaker.", asus_speaker)

    realtek_speaker = audio_devices.get_output_device_by_name("realtek")
    text_to_speech.speak_on_device("Hello, this is a test from my realtek speaker", realtek_speaker)


# I'll need to make a virtual loopback input device for this:

# def test_speak_on_input_device(text_to_speech: TextToSpeech.TextToSpeech, py_audio_wrapper: PyAudioWrapper.PyAudioWrapper):
#     audio_devices = py_audio_wrapper.get_audio_devices()
#     assert len(audio_devices.audio_devices) > 0
#     #asus_mic = audio_devices.get_input_device_by_name("intel")
#
#     for i in range(10):
#         for id in [4, 14, 27]:
#             mic = audio_devices.get_audio_device_by_index(id)
#             text_to_speech.speak_on_device("Hello, this is a test from my intel mic.", mic)
