from dataclasses import dataclass

@dataclass(frozen=True)
class RadioConfig:
    uri: str = "ip:192.168.2.1"