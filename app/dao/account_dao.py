from typing import Optional

import pandas as pd

from app.utils.csv_loader import load_csv


class AccountDAO:
    def __init__(self) -> None:
        self._accounts = load_csv("registered_account_data.csv")

    def find_by_username(self, username: str) -> pd.DataFrame:
        return self._accounts[self._accounts["Username"] == username]

    def validate_credentials(self, username: str, password: str) -> Optional[pd.Series]:
        matches = self.find_by_username(username)
        if matches.empty:
            return None

        for _, row in matches.iterrows():
            if password == row["password_hash"]:
                return row

        return None
