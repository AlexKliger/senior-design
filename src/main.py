import matplotlib.pyplot as plt

from src.controller import RadioController
from src.radio.config import RadioConfig
from src.radio.error import RadioError
from src.signal_processing import compute_spectrum, compute_average_power
from src.visualization import plot_iq, plot_spectrum
from src.waveforms import generate_tone

def main() -> None:
    config = RadioConfig()
    controller = RadioController(config)

    try:
        controller.connect()
        print(f"Connection to radio at {controller.config.uri}.")
        print("Receiving continuously. Press Ctrl+C to stop.")

        samples_outgoing_chan0 = generate_tone(
            frequency_hz=0,
            sample_rate_hz=config.sample_rate_hz,
            sample_count=16_000,
            amplitude=8_000,
        )

        samples_outgoing_chan1 = generate_tone(
            frequency_hz=0,
            sample_rate_hz=config.sample_rate_hz,
            sample_count=16_000,
            amplitude=8_000,
        )

        controller.transmit(
            samples_outgoing_chan0,
            samples_chan1=samples_outgoing_chan1,
            cyclic=True,
        )

        total_squared_magnitude = 0.0
        total_sample_count = 0

        for _ in range(1000):
            samples_incoming = controller.receive()

            total_squared_magnitude += (
                compute_average_power(samples_incoming) * samples_incoming.size
            )
            total_sample_count += samples_incoming.size

        average_power = total_squared_magnitude / total_sample_count
        print(f"Average power: {average_power}", flush=True)


        frequencies_hz, magnitude_db = compute_spectrum(
            samples=samples_incoming,
            sample_rate_hz=config.sample_rate_hz,
        )

        fig, ax = plt.subplots(figsize=(12, 5))

        plot_spectrum(
            ax=ax,
            frequencies_hz=frequencies_hz,
            magnitude_db=magnitude_db,
        )

        spectrum_line = ax.lines[0]
        ax.set_ylim(-20, 160)
        fig.tight_layout()
        plt.show(block=False)

        set_of_samples = []
        samples_count = 0

        while plt.fignum_exists(fig.number):
            samples = controller.receive()
            _, magnitude_db = compute_spectrum(
                samples=samples,
                sample_rate_hz=config.sample_rate_hz,
            )

            spectrum_line.set_ydata(magnitude_db)
            fig.canvas.draw_idle()
            plt.pause(0.001)

    except KeyboardInterrupt:
        print("\nReception stopped.")
    except RadioError as exc:
        print(f"Radio operation failed: {exc}")
        raise SystemExit(1)
    finally:
        plt.close("all")

if __name__ == "__main__":
    main()
