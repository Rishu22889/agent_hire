import random

class SandboxJobPortal:
    """
    A sandbox job portal API simulator.

    Accepted application format:
        {
            "job_id": str,
            "student_id": str,
            "content": dict
        }

    Usage:
        portal = SandboxJobPortal()
        result = portal.submit_application(application_dict)
    """
    def __init__(self):
        self._app_counter = 0

    def submit_application(self, application: dict) -> dict:
        # Validate required fields existence
        required_fields = ["job_id", "student_id", "content"]
        missing = [field for field in required_fields if field not in application]
        if missing:
            raise ValueError(f"Missing required application field(s): {missing}")

        # 5% random failure (reduced for better demo experience)
        FAILURE_RATE = 0.05
        if random.random() < FAILURE_RATE:
            raise RuntimeError("Submission failed due to random rejection (sandbox mode).")

        # Generate deterministic incremental receipt id (str for generality)
        self._app_counter += 1
        receipt_id = f"sandbox-{self._app_counter:06d}"

        return {
            "status": "submitted",
            "receipt_id": receipt_id
        }