from typing import Any, Dict, Optional

from app.utils.csv_loader import load_csv


class StudentDAO:
    def __init__(self) -> None:
        self._students = load_csv("student_raw_data.csv")

    def get_profile_by_student_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        # Normalize both DataFrame values and input
        match = self._students[self._students["Student ID"].astype(str).str.strip() == student_id.strip()]
        if match.empty:
            return None
        return match.iloc[0].to_dict()



