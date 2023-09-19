import time
import speech_recognition as sr
import threading
from typing import Optional, Tuple
from modules.PyAudioWrapper import PyAudioWrapper
from modules.helpers.logging_helper import logger
import json


class SpeechToText:
    def __init__(self, device_index: Optional[int] = None,
                 keyword_entries: Optional[list[Tuple]] = None,
                 credentials_json_file_path: Optional[str] = None):
        self.recognizer = sr.Recognizer()
        self.buffer = []  # To hold audio data
        self.transcription = []  # To hold transcribed text
        self.stop_capture = False  # Flag to control the capturing thread
        self.device_index = device_index  # Microphone device index
        self.keyword_entries = keyword_entries  # Keyword entries for keyword spotting
        self.engine = "sphinx"  # Default speech recognition engine
        self.credentials_json_file_path = credentials_json_file_path  # Google Cloud credentials JSON file
        self.latest_audio_chunk = None

    def set_engine(self, engine: str):
        """
        Set the speech recognition engine.

        Args:
            engine (str): The speech recognition engine to use.
        """
        if engine == "sphinx":
            self.engine = "sphinx"
        elif engine == "google":
            self.engine = "google"
        else:
            raise ValueError(f"Speech recognition engine '{engine}' not supported.")
        logger.info(f"Speech recognition engine set to '{self.engine}'")

    def start_capture(self):
        """
        Start capturing audio from the selected microphone.
        """
        with sr.Microphone(device_index=self.device_index) as source:
            while not self.stop_capture:
                audio = self.recognizer.listen(source)
                self.buffer.append(audio)
                logger.debug("Captured audio")
        logger.debug("End of start_capture()")

    def _transcribe_from_audio_data(self, audio_data) -> str:
        try:
            # Directly use the AudioData object for recognition
            if self.engine == "google":
                text = self.recognizer.recognize_google_cloud(audio_data=audio_data, credentials_json=self.credentials_json_file_path)
            elif self.engine == "sphinx":
                text = self.recognizer.recognize_sphinx(audio_data=audio_data, keyword_entries=self.keyword_entries)
            else:
                raise ValueError(f"Speech recognition engine '{self.engine}' not supported.")
            return text
        except sr.UnknownValueError:
            return "Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Error: {e}"

    def _transcribe_from_audio_source(self, audio_source: sr.AudioSource) -> str:
        try:
            with audio_source as source:
                audio = self.recognizer.listen(source)
            if self.engine == "google":
                text = self.recognizer.recognize_google_cloud(audio_data=audio, credentials_json=self.credentials_json_file_path)
            elif self.engine == "sphinx":
                text = self.recognizer.recognize_sphinx(audio_data=audio, keyword_entries=self.keyword_entries)
            else:
                raise ValueError(f"Speech recognition engine '{self.engine}' not supported.")
            return text
        except sr.UnknownValueError:
            return "Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Error: {e}"

    # Modify the start_transcription and transcribe_from_audio_file accordingly

    def start_transcription(self):
        """
        Start transcribing buffered audio.
        """
        while not self.stop_capture:
            if self.buffer:
                audio_chunk = self.buffer.pop(0)
                try:
                    text = self._transcribe_from_audio_data(audio_chunk)
                    self.transcription.append(text)
                except Exception as e:
                    logger.error(f"Error transcribing audio: {e}")
                self.latest_audio_chunk = audio_chunk
            time.sleep(0.001)

    def transcribe_from_audio_file(self, filepath: str):
        """
        Transcribe speech from an audio file.

        Args:
            filepath (str): The path to the audio file.

        Returns:
            str: The transcribed text.
        """
        audio_source = sr.AudioFile(filepath)
        return self._transcribe_from_audio_source(audio_source)

    def start(self):
        """
        Start capturing and transcribing audio.
        """
        capture_thread = threading.Thread(target=self.start_capture)
        transcribe_thread = threading.Thread(target=self.start_transcription)

        capture_thread.start()
        transcribe_thread.start()

    def stop(self):
        """
        Stop capturing and transcribing audio.
        """
        self.stop_capture = True



if __name__ == "__main__":
    py_audio_wrapper = PyAudioWrapper()
    audio_devices = py_audio_wrapper.get_audio_devices()
    #input_audio_device = audio_devices.get_input_device_by_name("mpow")

    # Listen to the game (Cable B)
    audio_device = audio_devices.get_input_device_by_name("cable-b")

    # Create a SpeechToText object
    stt = SpeechToText(device_index=audio_device.device_index)

    # Start capturing and transcribing
    stt.start()
    logger.debug("Listening for audio")

    # Stop capturing and transcribing (for demonstration, you'll want to decide when to call this)
    # stt.stop()
