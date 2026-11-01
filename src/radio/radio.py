import adi
import numpy as np

from src.radio.error import (
    RadioConnectionError,
    RadioNotConnectedError,
    RadioReceiverNotConfiguredError,
    RadioConfigurationError,
    RadioReceiveError,
    RadioTransmitterNotConfiguredError,
    RadioTransmitError
)
from src.radio.config import RadioConfig

class Radio:
    def __init__(self, uri: str) -> None:
        self.uri = uri
        self._device: adi.ad9361 | None = None
        self._receiver_configured = False
        self._transmitter_configured = False

    @property
    def is_connected(self) -> bool:
        """Wether a device connection has been created. Does not verify that the hardware is still reachable."""
        return self._device is not None

    def connect(self) -> None:
        if self.is_connected:
            return

        try:
            self._device = adi.ad9361(uri=self.uri)
        except Exception as exc:
            raise RadioConnectionError(
                f"Could not connect to radio at {self.uri}: {exc}"
            ) from exc

    def configure_receiver(self, config: RadioConfig) -> None:
        """Apply receiver settings using the existing connection."""
        self._receiver_configured = False
        
        device = self._device

        if device is None:
            raise RadioNotConnectedError(
                "Connect to the radio before configuring receiver."
            )

        try:
            device.rx_enabled_channels = [0]
            device.rx_lo = config.rx_center_frequency_hz
            device.rx_rf_bandwidth = config.rx_bandwidth_hz
            device.rx_buffer_size = config.rx_buffer_size
            device.sample_rate = config.sample_rate_hz

            ###
            device.gain_control_mode_chan0 = "manual"
            device.rx_hardwaregain_chan0 = 10.0
            ###
        except Exception as exc:
            raise RadioConfigurationError(
                f"Could not configure receiver at {self.uri}: {exc}"
            ) from exc

        self._receiver_configured = True

    def receive(self) -> np.ndarray:
        """Receive one buffer using the existing connection."""

        device = self._device

        if device is None:
            raise RadioNotConnectedError(
                "Connect to the radio before receiving samples."
            )

        if not self._receiver_configured:
            raise RadioReceiverNotConfiguredError(
                "Configure the receiver before receiving samples."
            )

        try:
            return device.rx()
        except Exception as exc:
            raise RadioReceiveError(
                f"Could not receive sample from radio at {self.uri}: {exc}"
            )

    def configure_transmitter(self, config: RadioConfig) -> None:
        """Apply transmitter settings using the existing connection."""
        self._transmitter_configured = False

        device = self._device

        if device is None:
            raise RadioNotConnectedError(
                f"Could not configure transmitter at {self.uri}."
            )

        try:
            device.tx_lo = config.tx_center_frequency_hz
            device.tx_rf_bandwidth = config.tx_bandwidth_hz
            device.tx_hardwaregain_chan0 = config.tx_hardware_gain_db
            device.tx_hardwaregain_chan1 = config.tx_hardware_gain_db
            device.sample_rate = config.sample_rate_hz
        except Exception as exc:
            raise RadioConfigurationError(
                f"Could not configure transmitter at {self.uri}: {exc}"
            ) from exc

        self._transmitter_configured = True

    def transmit(
        self,
        samples_chan0: np.ndarray,
        *,
        samples_chan1: np.ndarray | None = None,
        cyclic: bool = False
    ) -> None:
        """Transmit IQ samples, optionally repeating them continuously."""
        device = self._device

        if device is None:
            raise RadioNotConnectedError(
                "Connect to the radio before transmitting samples."
            )

        if not self._transmitter_configured:
            raise RadioTransmitterNotConfiguredError(
                "Configure the transmitter before transmitting samples."
            )

        channels = [0]
        waveforms = [samples_chan0]

        if samples_chan1 is not None:
            channels.append(1)
            waveforms.append(samples_chan1)

        # TODO: TypeError and ValueError validation.

        # TODO: Amplitude check to protect signed 16-bit sample representation.

        try:
            device.tx_destroy_buffer()
            device.tx_enabled_channels = channels
            device.tx_cyclic_buffer = cyclic

            if samples_chan1 is None:
                device.tx(samples_chan0)
            else:
                device.tx(waveforms)
        except Exception as exc:
            raise RadioTransmitError(
                f"Could not transmit samples to radio at {self.uri}: {exc}"
            ) from exc

    def stop_transmission(self) -> None:
        """Stop transmission by releasing the TX buffer."""
        device = self._device

        if device is None:
            return

        try:
            device.tx_destroy_buffer()
        except Exception as exc:
            raise RadioTransmitError(
                f"Could not stop transmission at {self.uri}: {exc}"
            ) from exc