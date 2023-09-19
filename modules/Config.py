import configparser
import os

class Config:
    def __init__(self, config_file_path: str):
        self.config_file_path = config_file_path
        if not os.path.exists(self.config_file_path):
            raise Exception(f"Config file not found at {self.config_file_path}")
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file_path)

        # TODO: encryption instead of reading plaintext
        self.base_url = self.config['openai_api_client']['base_url']
        self.path = self.config['openai_api_client']['path']
        self.api_key = self.config['openai_api_client']['api_key']
        self.model = self.config['openai_api_client']['model']
        self.max_conversation_tokens = int(self.config['openai_api_client']['max_conversation_tokens'])
        self.max_response_tokens = int(self.config['openai_api_client']['max_response_tokens'])
        self.max_dialogues_per_conversation = int(self.config['openai_api_client']['max_dialogues_per_conversation'])
        self.conversation_prune_after_seconds = int(self.config['openai_api_client']['conversation_prune_after_seconds'])
        self.temperature = float(self.config['openai_api_client']['temperature'])
        self.max_prompt_chars = int(self.config['openai_api_client']['max_prompt_chars'])
        self.system_message = self.config['openai_api_client']['system_message'] if len(self.config['openai_api_client']['system_message']) > 0 else None
        self.forced_system_message = self.config['openai_api_client']['forced_system_message'] if len(self.config['openai_api_client']['forced_system_message']) > 0 else None
        if self.system_message and self.forced_system_message:
            raise Exception("Cannot have both system_message and forced_system_message set in config.ini")