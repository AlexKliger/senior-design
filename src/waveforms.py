import numpy as np

def generate_tone(
    *,
    frequency_hz: int,
    sample_rate_hz: int,
    sample_count: int,
    amplitude: float = 8_000,
    phase_shift_deg: float = 0.0
) -> np.ndarray:
    """Generate complex IQ samples for a tone in raw sample units."""

    #TODO: Value and Type error validation.

    sample_indices = np.arange(sample_count)
    phase = 2 * np.pi * frequency_hz * sample_indices / sample_rate_hz + np.deg2rad(phase_shift_deg)

    return amplitude * np.exp(1j * phase)