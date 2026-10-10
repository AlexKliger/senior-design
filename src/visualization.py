import numpy as np
from matplotlib.axes import Axes


def plot_iq(
    ax: Axes,
    samples: np.ndarray,
    sample_rate_hz: float,
) -> None:
    """Plot one buffer of complex I/Q samples against time."""
    time_ms = np.arange(samples.size) / sample_rate_hz * 1_000

    ax.plot(time_ms, samples.real, label="I", linewidth=0.8)
    ax.plot(time_ms, samples.imag, label="Q", linewidth=0.8)

    ax.set_title("Received I/Q samples")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Amplitude (raw sample units)")
    ax.legend()
    ax.grid(True, alpha=0.3)