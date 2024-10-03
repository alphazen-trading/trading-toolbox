import msgspec
from typing import Optional


class ExchangeConfig(msgspec.Struct):
    enableRateLimit: bool
    apiKey: Optional[str] = ""
    secret: Optional[str] = ""
    password: Optional[str] = ""
    uid: Optional[str] = None
    newUpdates: Optional[bool] = None
    options: dict = {}

    @classmethod
    def create(cls, config_file_path):
        with open(config_file_path, "rb") as f:
            config = msgspec.json.decode(f.read())
        return cls(**config)
