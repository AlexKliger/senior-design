import adi
import numpy as np

from src.config import RadioConfig

class Radio:
    def __init__(self, uri: str) -> None:
        self.uri = uri
        self._device: adi.Pluto | None = None
        self._receiver_configured = False

    @property
    def is_connected(self) -> bool:
        return self._device is not None

    def connect(self) -> None:
        """Receive one buffer using the existing connection."""

        if self.is_connected:
            return

        try:
            self._device = adi.Pluto(uri=self.uri)
        except Exception as exc:
            raise RadioConnectionError(
                f"Could not connect to radio at {self.uri}: {exc}"
            ) from exc

    def configure_receiver(self, config: RadioConfig) -> None:
        self._receiver_configured = False
        device = self._device

        if device is None:
            raise RuntimeError("Connect to the radio before configuring receiver.")

        device.rx_lo = config.rx_center_frequency_hz
        device.rx_rf_bandwidth = config.rx_bandwidth_hz
        device.rx_buffer_size = config.rx_buffer_size
        device.sample_rate = config.sample_rate_hz

        self._receiver_configured = True

    def receive(self) -> np.ndarray:
        device = self._device

        if device is None:
            raise RuntimeError("Connect to the radio before receiving samples.")

        if not self._receiver_configured:
            raise RuntimeError("Configure the receiver before receiving samples.")

        return device.rx()
    
class RadioConnectionError(RuntimeError):
    """Raised when a connection to the radio cannot be established."""