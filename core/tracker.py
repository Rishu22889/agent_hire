import os
import threading
import time
from typing import Optional, Dict, Any

class ApplicationTracker:
    """
    Tracks job application attempts, statuses, and logs them to a file.
    """

    LOG_DIR = "logs"
    LOG_FILE = "applications.log"
    STATUSES = {"queued", "skipped", "submitted", "failed", "retried"}

    def __init__(self):
        self.lock = threading.Lock()
        self.applications = []  # List[Dict]
        os.makedirs(self.LOG_DIR, exist_ok=True)
        self.logpath = os.path.join(self.LOG_DIR, self.LOG_FILE)

    def track(
        self,
        job_id: str,
        status: str,
        reason: Optional[str] = None,
        receipt_id: Optional[str] = None,
        timestamp: Optional[float] = None
    ):
        """
        Record an application attempt.

        Args:
            job_id (str): Identifier for the job.
            status (str): One of "queued", "skipped", "submitted", "failed", "retried".
            reason (Optional[str]): Why it was skipped or failed.
            receipt_id (Optional[str]): If submitted, the receipt id.
            timestamp (Optional[float]): Timestamp, defaults to now.
        """

        if status not in self.STATUSES:
            raise ValueError(f"Invalid status '{status}'. Allowed: {self.STATUSES}")

        entry = {
            "job_id": job_id,
            "status": status,
            "reason": reason if status in {"skipped", "failed"} else None,
            "receipt_id": receipt_id if status == "submitted" else None,
            "timestamp": timestamp if timestamp is not None else time.time()
        }

        # Clear irrelevant fields for readability
        if entry["reason"] is None:
            entry.pop("reason")
        if entry["receipt_id"] is None:
            entry.pop("receipt_id")

        with self.lock:
            self.applications.append(entry)
            self._append_log(entry)

    def _append_log(self, entry: Dict[str, Any]):
        # Deterministic readable log entry in TSV (tab-separated, one line per event)
        t_struct = time.gmtime(entry["timestamp"])
        tstr = time.strftime('%Y-%m-%d %H:%M:%S UTC', t_struct)
        log_parts = [
            f"job_id={entry['job_id']}",
            f"status={entry['status']}",
            f"time='{tstr}'"
        ]
        if "reason" in entry:
            log_parts.append(f"reason='{entry['reason']}'")
        if "receipt_id" in entry:
            log_parts.append(f"receipt_id='{entry['receipt_id']}'")

        log_line = "\t".join(log_parts) + "\n"
        with open(self.logpath, "a", encoding='utf-8') as f:
            f.write(log_line)

    def get_applications(self):
        """
        Return a snapshot of all tracked application entries.
        """
        with self.lock:
            return list(self.applications)
