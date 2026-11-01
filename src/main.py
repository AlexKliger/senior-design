import argparse
import time

import matplotlib.pyplot as plt
import numpy as np

from src.controller import RadioController
from src.radio.config import RadioConfig
from src.radio.error import RadioError
from src.signal_processing import compute_average_power
from src.waveforms import generate_tone

def main() -> None:
    args = parse_args()

    config = RadioConfig()
    controller = RadioController(config)

    phases_deg = list(range(0, 361, 10))
    completed_sweeps = []
    subplot_count = 6
    total_sweeps = subplot_count * args.sweeps

    buffers_to_discard = 8
    buffers_to_average = 10

    try:
        controller.connect()
        print(f"Connection to radio at {controller.config.uri}.")
        print(
            f"Running {total_sweeps} phase sweeps: "
            f"{subplot_count} groups of {args.sweeps}. Press Ctrl+C to stop."
        )

        samples_outgoing_chan0 = generate_tone(
            frequency_hz=100_000,
            sample_rate_hz=config.sample_rate_hz,
            sample_count=16_000,
            amplitude=8_000,
        )

        # Measure one reference with only TX channel 0 enabled.
        controller.transmit(
            samples_chan0=samples_outgoing_chan0,
            cyclic=True,
        )
        time.sleep(0.05)
        for _ in range(buffers_to_discard):
            controller.receive()

        total_reference_power = 0.0
        for _ in range(buffers_to_average):
            samples = controller.receive()
            total_reference_power += compute_average_power(samples)

        single_antenna_power = total_reference_power / buffers_to_average
        if not np.isfinite(single_antenna_power) or single_antenna_power <= 0:
            raise RadioError("Single-antenna reference power must be finite and positive.")
        print(
            f"TX0-only average received power: {single_antenna_power:.6g} "
            "raw sample units squared (0 dB reference).",
            flush=True,
        )

        for sweep_index in range(total_sweeps):
            group_index, run_index = divmod(sweep_index, args.sweeps)
            sweep_powers = []

            for phase_deg in phases_deg:
                samples_outgoing_chan1 = generate_tone(
                    frequency_hz=100_000,
                    sample_rate_hz=config.sample_rate_hz,
                    sample_count=16_000,
                    amplitude=8_000,
                    phase_shift_deg=phase_deg,
                )

                controller.transmit(
                    samples_chan0=samples_outgoing_chan0,
                    samples_chan1=samples_outgoing_chan1,
                    cyclic=True,
                )

                # Allow the new transmission to settle.
                time.sleep(0.05)

                # Drain samples that may belong to the previous phase.
                for _ in range(buffers_to_discard):
                    controller.receive()

                total_power = 0.0
                for _ in range(buffers_to_average):
                    samples = controller.receive()
                    total_power += compute_average_power(samples)

                # Keep linear power for averaging across sweeps.
                average_power = total_power / buffers_to_average
                sweep_powers.append(average_power)
                power_db = float(
                    10 * np.log10(
                        max(average_power, 1e-12) / single_antenna_power
                    )
                )

                print(
                    f"Group {group_index + 1}/{subplot_count} | "
                    f"Run {run_index + 1}/{args.sweeps} | "
                    f"Phase: {phase_deg:3d}° | "
                    f"Received power: {power_db:.2f} dB relative to TX0 only",
                    flush=True,
                )

            # Include only complete sweeps so every phase has equal weight.
            completed_sweeps.append(sweep_powers)

        # samples_outgoing_chan0 = generate_tone(
        #     frequency_hz=args.frequency0,
        #     sample_rate_hz=config.sample_rate_hz,
        #     sample_count=16_000,
        #     amplitude=args.amplitude0,
        #     phase_shift_deg=args.phase0,
        # )

        # samples_outgoing_chan1 = generate_tone(
        #     frequency_hz=args.frequency1,
        #     sample_rate_hz=config.sample_rate_hz,
        #     sample_count=16_000,
        #     amplitude=args.amplitude1,
        #     phase_shift_deg=args.phase1,
        # )

        # controller.transmit(
        #     samples_outgoing_chan0,
        #     samples_chan1=samples_outgoing_chan1,
        #     cyclic=True,
        # )

        # samples_incoming = controller.receive()

        # total_squared_magnitude = 0.0
        # total_sample_count = 0

        # for _ in range(1000):
        #     samples_incoming = controller.receive()

        #     total_squared_magnitude += (
        #         compute_average_power(samples_incoming) * samples_incoming.size
        #     )
        #     total_sample_count += samples_incoming.size

        # average_power = total_squared_magnitude / total_sample_count
        # print(f"Average power: {average_power}", flush=True)


        # frequencies_hz, magnitude_db = compute_spectrum(
        #     samples=samples_incoming,
        #     sample_rate_hz=config.sample_rate_hz,
        # )

        # fig, ax = plt.subplots(figsize=(12, 5))

        # plot_spectrum(
        #     ax=ax,
        #     frequencies_hz=frequencies_hz,
        #     magnitude_db=magnitude_db,
        # )

        # spectrum_line = ax.lines[0]
        # ax.set_ylim(-20, 160)
        # fig.tight_layout()
        # plt.show(block=False)

        set_of_samples = []
        samples_count = 0

        # while plt.fignum_exists(fig.number):
        #     samples = controller.receive()
        #     _, magnitude_db = compute_spectrum(
        #         samples=samples,
        #         sample_rate_hz=config.sample_rate_hz,
        #     )

        #     spectrum_line.set_ydata(magnitude_db)
        #     fig.canvas.draw_idle()
        #     plt.pause(0.001)

    except KeyboardInterrupt:
        print("\nSweep interrupted. Only complete groups will be plotted.")
    except RadioError as exc:
        print(f"Radio operation failed: {exc}")
        raise SystemExit(1)
    finally:
        # Stop cyclic transmission even if the sweep fails.
        try:
            controller.stop_transmission()
        except RadioError as exc:
            print(f"Could not stop transmission: {exc}")

    complete_groups = len(completed_sweeps) // args.sweeps
    if complete_groups == 0:
        print(f"No complete groups of {args.sweeps} sweeps to average.")
        return

    fig, axes = plt.subplots(
        2, 3, figsize=(15, 8), sharex=True, sharey=True
    )

    for group_index, ax in enumerate(axes.flat):
        if group_index >= complete_groups:
            ax.set_title(f"Group {group_index + 1}: incomplete")
            ax.set_axis_off()
            continue

        # Each subplot uses its own group of consecutive, complete sweeps.
        start = group_index * args.sweeps
        group_sweeps = completed_sweeps[start:start + args.sweeps]
        average_powers = np.mean(group_sweeps, axis=0)
        # Convert the ratio of averaged powers, rather than averaging dB values.
        powers_db = 10 * np.log10(
            np.maximum(average_powers, 1e-12) / single_antenna_power
        )

        best_index = int(np.argmax(powers_db))
        best_phase = phases_deg[best_index]
        print(
            f"Group {group_index + 1} ({args.sweeps} sweeps averaged): "
            f"best measured phase {best_phase}° "
            f"({powers_db[best_index]:.2f} dB relative to TX0 only)"
        )

        ax.plot(phases_deg, powers_db, marker="o", markersize=3)
        ax.axhline(0, color="gray", linestyle="--", linewidth=1)
        ax.set_title(
            f"Group {group_index + 1}: {args.sweeps} runs averaged\n"
            f"Best measured phase: {best_phase}°"
        )
        ax.grid(True)

    fig.supxlabel("Channel 1 phase relative to channel 0 (degrees)")
    fig.supylabel("Mean received power relative to TX0 only (dB)")
    fig.suptitle(
        f"Received power versus transmit phase: "
        f"{args.sweeps} runs per subplot"
    )
    fig.tight_layout()
    plt.show()

    # except KeyboardInterrupt:
    #     print("\nReception stopped.")
    # except RadioError as exc:
    #     print(f"Radio operation failed: {exc}")
    #     raise SystemExit(1)
    # finally:
    #     plt.close("all")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transmit two tones with independent phase shifts."
    )

    parser.add_argument(
        "--sweeps",
        type=int,
        default=5,
        help="Number of phase sweeps to average per subplot (default: 5).",
    )

    parser.add_argument(
        "--amplitude0",
        type=float,
        default = 8_000,
        help="Amplitude for channel 0 in UNKNOWN (default: 8000).",
    )

    parser.add_argument(
        "--amplitude1",
        type=float,
        default = 8_000,
        help="Amplitude for channel 1 in UNKNOWN (default: 8000).",
    )

    parser.add_argument(
        "--frequency0",
        type=float,
        default=100_000,
        help="Frequency for channel 0 in Hz (default: 100 KHz).",
    )

    parser.add_argument(
        "--frequency1",
        type=float,
        default=100_000,
        help="Frequency for channel 1 in Hz (default: 100 KHz).",
    )

    parser.add_argument(
        "--phase0",
        type=float,
        default=0.0,
        help="Phase shift for channel 0 in degrees (default: 0).",
    )

    parser.add_argument(
        "--phase1",
        type=float,
        default=0.0,
        help="Phase shift for channel 1 in degrees (default: 1).",
    )

    args = parser.parse_args()
    if args.sweeps < 1:
        parser.error("--sweeps must be at least 1")
    return args

if __name__ == "__main__":
    main()
