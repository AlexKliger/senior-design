import numpy as np

from src.radio.config import RadioConfig
from src.radio.radio import Radio

class RadioController():
    def __init__(self, config: RadioConfig) -> None:
        self._config = config
        self._radio = Radio(uri=config.uri)

    @property
    def is_connected(self) -> bool:
        return self._radio.is_connected

    @property
    def config(self) -> RadioConfig:
        return self._config

    def connect(self) -> None:
        """Connect and apply the receiver configuration."""
        self._radio.connect()
        self._radio.configure_receiver(self._config)

    def receive(self) -> np.ndarray:
        return self._radio.receive()