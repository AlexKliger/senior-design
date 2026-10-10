class RadioError(RuntimeError):
    """Base class for application-defined radio errors."""

class RadioConnectionError(RadioError):
    """Raised when a connection to the radio cannot be established."""

class RadioNotConnectedError(RadioError):
    """Raised when an operation requires an existing connection and none exists."""

class RadioReceiverNotConfiguredError(RadioError):
    """Raised when an operation requires the receiver to be configured and it is not."""

class RadioConfigurationError(RadioError):
    "Raised when receiver settings cannot be applied."

class RadioReceiveError(RadioError):
    """Raised when receiving samples fails."""