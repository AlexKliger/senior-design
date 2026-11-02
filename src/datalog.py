import csv
from datetime import datetime, timezone


class DataLogger:
    FIELDS = (
        "timestamp_utc",
        "group_index",
        "sweep_index",
        "commanded_phase_deg",
        "rx_power_raw_sq",
        "tx0_reference_power_raw_sq",
        "relative_power_db",
        "noise_power_raw_sq",
        "snr_db",
    )

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        # Create a new file; refuse to overwrite an existing experiment.
        self.file = open(
            self.path, "x", newline="", encoding="utf-8"
        )
        try:
            self.writer = csv.DictWriter(
                self.file, fieldnames=self.FIELDS
            )
            self.writer.writeheader()
            self.file.flush()
        except BaseException:
            self.file.close()
            raise
        return self

    def log(
        self,
        *,
        group_index,
        sweep_index,
        commanded_phase_deg,
        rx_power_raw_sq,
        tx0_reference_power_raw_sq,
        relative_power_db,
        noise_power_raw_sq=None,
        snr_db=None,
    ):
        self.writer.writerow({
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "group_index": group_index,
            "sweep_index": sweep_index,
            "commanded_phase_deg": commanded_phase_deg,
            "rx_power_raw_sq": rx_power_raw_sq,
            "tx0_reference_power_raw_sq": tx0_reference_power_raw_sq,
            "relative_power_db": relative_power_db,
            "noise_power_raw_sq": noise_power_raw_sq,
            "snr_db": snr_db,
        })
        self.file.flush()

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()