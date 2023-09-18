import pyaudio
from typing import List
from modules.AudioDevice import AudioDevice
from modules.AudioDeviceCollection import AudioDeviceCollection

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
            device_name = device_info.get("name")
            max_input_channels = device_info.get("maxInputChannels")
            max_output_channels = device_info.get("maxOutputChannels")

            # For virtual cables, I can't go by input/output channels and I have to go by name.
            if "output" in device_name.lower():
                audio_devices.append(AudioDevice(device_name=device_name, device_index=i, is_input=False))
            elif "input" in device_name.lower():
                audio_devices.append(AudioDevice(device_name=device_name, device_index=i, is_input=True))
            elif max_input_channels > 0:
                audio_devices.append(AudioDevice(device_name=device_name, device_index=i, is_input=True))
            elif max_output_channels > 0:
                audio_devices.append(AudioDevice(device_name=device_name, device_index=i, is_input=False))

        # self.audio.terminate()
        return AudioDeviceCollection(audio_devices=audio_devices)