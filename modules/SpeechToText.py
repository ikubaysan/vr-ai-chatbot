import time
import speech_recognition as sr
import threading
from typing import Optional, Tuple
from modules.PyAudioWrapper import PyAudioWrapper
from modules.helpers.logging_helper import logger


class SpeechToText:
    def __init__(self, device_index: Optional[int] = None, keyword_entries: Optional[list[Tuple]] = None):
        self.recognizer = sr.Recognizer()
        self.buffer = []  # To hold audio data
        self.transcription = []  # To hold transcribed text
        self.stop_capture = False  # Flag to control the capturing thread
        self.device_index = device_index  # Microphone device index
        self.keyword_entries = keyword_entries  # Keyword entries for keyword spotting


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
            text = self.recognizer.recognize_sphinx(audio_data)
            return text
        except sr.UnknownValueError:
            return "Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Error: {e}"

    def _transcribe_from_audio_source(self, audio_source: sr.AudioSource) -> str:
        try:
            with audio_source as source:
                audio = self.recognizer.listen(source)
            text = self.recognizer.recognize_sphinx(audio, keyword_entries=self.keyword_entries)
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
