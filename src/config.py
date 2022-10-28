from dataclasses import dataclass

import yaml


@dataclass(init=False)
class Config:
    telegram_token: str
    log_path: str

    def load(self, filepath: str):
        with open(filepath) as f:
            config = yaml.load(f, yaml.FullLoader)
        self.init(config)

    def init(self, config: dict):
        self.log_path = config.get("log_path", "log.txt")
        self.telegram_token = config.get("telegram_token", "")
        if not self.telegram_token:
            raise Exception("No telegram token")


config: Config = Config()


def load(filepath):
    config.load(filepath)
