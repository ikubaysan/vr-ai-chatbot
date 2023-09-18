import speech_recognition as sr


class SpeechToText:
    def __init__(self):
        """
        Initialize the SpeechToText object.
        """
        self.recognizer = sr.Recognizer()


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

    def _transcribe(self, audio_source: sr.AudioSource) -> str:
        """
        Transcribe speech from an audio source.

        Args:
            audio_source (sr.AudioSource): The audio source (e.g., from a microphone or audio file).

        Returns:
            str: The transcribed text.
        """
        with audio_source as source:
            audio = self.recognizer.listen(source)
        try:
            text = self.recognizer.recognize_sphinx(audio)
            return text
        except sr.UnknownValueError:
            return "Speech Recognition could not understand audio"
        except sr.RequestError as e:
            return f"Error: {e}"
