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
        """Connect to the device and apply the radio configuration."""
        self._radio.connect()
        self._radio.configure_receiver(self._config)
        self._radio.configure_transmitter(self._config)

    def receive(self) -> np.ndarray:
        return self._radio.receive()

    def transmit(
        self,
        samples_chan0: np.ndarray,
        *,
        samples_chan1: np.ndarray | None = None,
        cyclic: bool = False,
    ) -> None:
        return self._radio.transmit(
            samples_chan0,
            samples_chan1=samples_chan1,
            cyclic=cyclic,
        )

    def stop_transmission(self) -> None:
        self._radio.stop_transmission()