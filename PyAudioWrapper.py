import pyaudio
from typing import List
from AudioDevice import AudioDevice
from AudioDeviceCollection import AudioDeviceCollection

class PyAudioWrapper:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        return

    def get_audio_devices(self) -> AudioDeviceCollection:
        """
        List the available audio devices - both input and output.
        :return:
        """
        audio_devices = []
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info.get("maxInputChannels") > 0:
                audio_devices.append(AudioDevice(device_name=device_info.get("name"), device_index=i, is_input=True))
            elif device_info.get("maxOutputChannels") > 0:
                audio_devices.append(AudioDevice(device_name=device_info.get("name"), device_index=i, is_input=False))
        # self.audio.terminate()
        return AudioDeviceCollection(audio_devices=audio_devices)