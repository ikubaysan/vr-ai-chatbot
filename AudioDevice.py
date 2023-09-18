class AudioDevice:
    def __init__(self, device_name: str, device_index: int, is_input: bool):
        self.device_name = device_name
        self.device_index = device_index
        self.is_input = is_input
        return

    def __str__(self):
        return f"{self.device_name} ({self.device_index}) Is input: {self.is_input}"
