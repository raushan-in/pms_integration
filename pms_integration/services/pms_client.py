import json
from pathlib import Path
from typing import Dict, List

from pms_integration.exceptions import PMSConnectionError


class PMSClient:
    """
    Simulates an external PMS API by loading mock data from a JSON file.
    """

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def fetch_bookings(self) -> List[Dict]:
        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise PMSConnectionError(f"Mock PMS data file not found: {self.file_path}")
        except json.JSONDecodeError as e:
            raise PMSConnectionError(f"Invalid JSON format in PMS file: {e}")
