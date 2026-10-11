import numpy as np

def compute_spectrum(
        samples: np.ndarray,
        sample_rate_hz: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Return frequency offsets in Hz and unnormalized FFT magnitudes in dB.

    Magnitudes use one raw FFT unit as the dB reference and depend on the
    sample amplitude, sample count, and Hann window.
    """

    #TODO: Value error validation.

    window = np.hanning(samples.size)
    spectrum = np.fft.fftshift(np.fft.fft(samples * window))

    frequencies_hz = np.fft.fftshift(
        np.fft.fftfreq(samples.size, d=1 / sample_rate_hz)
    )

    magnitude = np.abs(spectrum)
    # Floor magnitudes at 1e-6 raw FFT units to avoid log10(0).
    magnitude_db = 20 * np.log10(
        np.maximum(magnitude, 1e-6)
    )

    return frequencies_hz, magnitude_db

def compute_average_power(samples: np.ndarray) -> float:
    iq = np.asarray(samples, dtype=np.complex128)
    return float(np.mean(np.abs(iq)**2))
