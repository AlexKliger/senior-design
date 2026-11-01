import numpy as np
from matplotlib.axes import Axes


def plot_iq(
    ax: Axes,
    samples: np.ndarray,
    sample_rate_hz: float,
) -> None:
    time_ms = np.arange(samples.size) / sample_rate_hz * 1_000

    ax.plot(time_ms, samples.real, label="I", linewidth=0.8)
    ax.plot(time_ms, samples.imag, label="Q", linewidth=0.8)

    ax.set_title("Received I/Q samples")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Amplitude (raw sample units)")
    ax.legend()
    ax.grid(True, alpha=0.3)

def plot_spectrum(
    ax: Axes,
    frequencies_hz: np.ndarray,
    magnitude_db: np.ndarray,
) -> None:
    ax.plot(frequencies_hz, magnitude_db, linewidth=0.8)
    ax.set_title("Received IQ spectrum")
    ax.set_xlabel("Frequency offset from RX center (kHz)")
    ax.set_ylabel("FFT magnitude (dB re 1 raw FFT unit)")
    ax.grid(True, alpha=0.3)
