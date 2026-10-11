from dataclasses import dataclass

@dataclass(frozen=True)
class RadioConfig:
    uri: str = "ip:192.168.2.1"
    sample_rate_hz: int = 4_000_000
    # Reception
    rx_center_frequency_hz: int = 2_400_000_000
    rx_bandwidth_hz: int = 2_000_000
    rx_buffer_size: int = 2**14
    #Transmission
    tx_center_frequency_hz: int = 2_400_000_000
    tx_bandwidth_hz: int = 2_000_000
    tx_hardware_gain_db: float = -30.0