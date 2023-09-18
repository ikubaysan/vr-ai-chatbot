from modules import PyAudioWrapper


def test_list_microphone_names(py_audio_wrapper: PyAudioWrapper.PyAudioWrapper):
    audio_devices = py_audio_wrapper.get_audio_devices()
    assert len(audio_devices.audio_devices) > 0