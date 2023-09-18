import speech_recognition as sr
import threading
from typing import Optional, List
import PyAudioWrapper


class SpeechToText:
    def __init__(self, device_index: Optional[int] = None):
        self.recognizer = sr.Recognizer()
        self.buffer = []  # To hold audio data
        self.transcription = []  # To hold transcribed text
        self.stop_capture = False  # Flag to control the capturing thread
        self.device_index = device_index  # Microphone device index

    def start_capture(self):
        """
        Start capturing audio from the selected microphone.
        """
        with sr.Microphone(device_index=self.device_index) as source:
            while not self.stop_capture:
                audio = self.recognizer.listen(source, timeout=5)
                self.buffer.append(audio)

    def start_transcription(self):
        """
        Start transcribing buffered audio.
        """
        while not self.stop_capture:
            if self.buffer:
                audio_chunk = self.buffer.pop(0)
                text = self._transcribe(audio_chunk)
                self.transcription.append(text)

    def transcribe_from_audio_file(self, filepath: str):
        """
        Transcribe speech from an audio file.

        Args:
            filepath (str): The path to the audio file.

        Returns:
            str: The transcribed text.
        """
        audio_source = sr.AudioFile(filepath)
        return self._transcribe(audio_source)

    def _transcribe(self, audio_source) -> str:
        try:
            with audio_source as source:
                audio = self.recognizer.listen(source)
            text = self.recognizer.recognize_sphinx(audio)
            return text
        except sr.UnknownValueError:
            return "Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Error: {e}"

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
    # Create a SpeechToText object
    stt = SpeechToText(device_index=1)  # Replace with the actual device index

    # Start capturing and transcribing
    stt.start()

    # Stop capturing and transcribing (for demonstration, you'll want to decide when to call this)
    # stt.stop()
