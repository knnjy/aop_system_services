

from app.utils.csv_loader import load_csv


class OrderDAO:
    def __init__(self) -> None:
        self._orders = load_csv("")