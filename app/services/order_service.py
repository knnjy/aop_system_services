from app.dao.orders_dao import OrderDAO
from app.dto.order_dto import OrderRequest


class OrderService:
    def __init__(self):
        self._order_dao = OrderDAO()

    def add_new_order(self, order_form: OrderRequest):
        pass