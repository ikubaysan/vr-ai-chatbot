from modules.AudioDevice import AudioDevice
from typing import List

class AudioDeviceCollection:
    def __init__(self, audio_devices: List[AudioDevice]):
        self.audio_devices = audio_devices
        self.input_devices = [audio_device for audio_device in audio_devices if audio_device.is_input]
        self.output_devices = [audio_device for audio_device in audio_devices if not audio_device.is_input]
        return

    def get_audio_device_by_index(self, device_index: int) -> AudioDevice:
        for audio_device in self.audio_devices:
            if audio_device.device_index == device_index:
                return audio_device
        raise ValueError(f"Audio device with index '{device_index}' not found.")

    def get_input_device_by_name(self, device_name: str) -> AudioDevice:
        # Use case-insensitive and contains matching
        for audio_device in self.input_devices:
            if device_name.lower() in audio_device.device_name.lower():
                return audio_device
        raise ValueError(f"Input device with name '{device_name}' not found.")

    def get_output_device_by_name(self, device_name: str) -> AudioDevice:
        # Use case-insensitive and contains matching
        for audio_device in self.output_devices:
            if device_name.lower() in audio_device.device_name.lower():
                return audio_device
        raise ValueError(f"Output device with name '{device_name}' not found.")