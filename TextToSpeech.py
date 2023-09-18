from typing import Optional, List
import pyttsx3


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