import adi

class Radio:
    def __init__(self, uri: str) -> None:
        self.uri = uri
        self._device: adi.Pluto | None = None

    @property
    def is_connected(self) -> bool:
        return self._device is not None

    def connect(self) -> None:
        if self.is_connected:
            return

        try:
            self._device = adi.Pluto(uri=self.uri)
        except Exception as exc:
            raise RadioConnectionError(
                f"Could not connect to radio at {self.uri}: {exc}"
            ) from exc

class RadioConnectionError(RuntimeError):
    """Raised when a connection to the radio cannot be established."""
