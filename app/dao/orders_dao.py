from app.utils.csv_loader import load_csv

class OrderDAO:
    def __init__(self) -> None:
        self._orders = load_csv("orders.csv")

    def get_order_by_id(self, id: int):
        for order in self._orders:
            if order.id == id:
                return order
        return None

    def save_order(self, order):
        for idx, existing_order in enumerate(self._orders):
            if existing_order.id == order.id:
                self._orders[idx] = order
                break
        self._write_to_csv()

    def _write_to_csv(self):

        pass

