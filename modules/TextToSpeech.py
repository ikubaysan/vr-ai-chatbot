from typing import Optional, List
import pyttsx3
import pyaudio
from modules.AudioDevice import AudioDevice
from modules.PyAudioWrapper import PyAudioWrapper
from modules.helpers.logging_helper import logger
import os
import wave


class TextToSpeech:
    def __init__(
        self,
        voice_id: Optional[str] = None,
        rate: Optional[int] = None,
        volume: Optional[float] = None,
    ):
        """
        Initialize the TextToSpeech object.

        Args:
            voice_id (str, optional): The ID of the voice to use for speech synthesis.
            rate (int, optional): The rate of speech (words per minute).
            volume (float, optional): The volume level (0.0 to 1.0).
        """
        self.engine = pyttsx3.init()
        if voice_id:
            self.set_voice(voice_id)
        if rate is not None:
            self.set_rate(rate)
        if volume is not None:
            self.set_volume(volume)

    def set_volume(self, volume: float) -> None:
        """
        Set the volume level (0.0 to 1.0).

        Args:
            volume (float): The volume level (0.0 to 1.0).
        """
        self.engine.setProperty("volume", volume)

    def set_rate(self, rate: int) -> None:
        """
        Set the rate of speech (words per minute).

        Args:
            rate (int): The rate of speech (words per minute).
        """
        self.engine.setProperty("rate", rate)

    def set_voice(self, voice_id: str) -> None:
        """
        Set the voice to use for speech synthesis.

        Args:
            voice_id (str): The ID of the voice to use for speech synthesis.
        """
        self.engine.setProperty("voice", voice_id)

    @staticmethod
    def get_available_voices() -> List:
        """
        Get a list of available voices for speech synthesis.

        Returns:
            List[pyttsx3.voice.Voice]: List of available voices.
        """
        return pyttsx3.init().getProperty("voices")

    def speak(self, text: str) -> None:
        """
        Synthesize and speak the given text.

        Args:
            text (str): The text to be spoken.
        """
        self.engine.say(text)
        self.engine.runAndWait()

    def speak_to_file(self, text: str, filepath: str) -> None:
        """
        Synthesize and save the given text to a file.

        Args:
            text (str): The text to be spoken.
            filepath (str): The path to the file to save the audio to. Must be wav or mp3.
        """
        self.engine.save_to_file(text, filepath)
        self.engine.runAndWait()

    def speak_on_device(self, text: str, audio_device: AudioDevice):
        """
        Synthesize and speak the given text using a specific audio device.

        Args:
            text (str): The text to be spoken.
            audio_device (AudioDevice): The audio device to use for speech synthesis.
        """
        # First save the synthesized speech to a temporary .wav file
        # Create the temp folder if it doesn't exist
        temp_folder = "./temp"
        if not os.path.exists(temp_folder):
            os.mkdir(temp_folder)

        filepath = os.path.join(temp_folder, "speak_on_device_temp_speech.wav")
        self.speak_to_file(text, filepath)

        # Now play the saved audio file using pyaudio
        p = pyaudio.PyAudio()

        # Read the .wav file
        wf = wave.open(filepath, 'rb')

        # Open a PyAudio stream
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        output_device_index=audio_device.device_index)

        # Read data chunk and play
        chunk = 1024
        data = wf.readframes(chunk)
        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(chunk)

        # Stop stream
        stream.stop_stream()
        stream.close()

        # Close PyAudio
        p.terminate()

if __name__ == "__main__":
    py_audio_wrapper = PyAudioWrapper()
    audio_devices = py_audio_wrapper.get_audio_devices()

    # Speak into the game (Cable A)
    audio_device = audio_devices.get_input_device_by_name("cable-a")

    text_to_speech = TextToSpeech()
    text_to_speech.speak_on_device("Hello, this is a test from my cable-a speaker.", audio_device)


