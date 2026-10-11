class RadioError(RuntimeError):
    """Base class for application-defined radio errors."""

class RadioConnectionError(RadioError):
    """Raised when a connection to the radio cannot be established."""

class RadioNotConnectedError(RadioError):
    """Raised when an operation requires an existing connection and none exists."""

class RadioReceiverNotConfiguredError(RadioError):
    """Raised when an operation requires the receiver configuration that has not been applied."""

class RadioConfigurationError(RadioError):
    "Raised when radio settings cannot be applied."

class RadioReceiveError(RadioError):
    """Raised when receiving samples fails."""

class RadioTransmitterNotConfiguredError(RadioError):
    """Raised when an operation requires the transmitter configuration that has not been applied."""

class RadioTransmitError(RadioError):
        """Raised when receiving samples fails."""