from app.dao.orders_dao import OrderDAO
from app.dto.order_dto import OrderRequest


class OrderService:
    def __init__(self):
        self._order_dao = OrderDAO()

    def add_new_order(self, order_form: OrderRequest):

        # double check if total amount is correct
        calculated_total = sum(item.quantity * item.unit_price for item in order_form.order_items)
        if calculated_total != order_form.total_amount:
            raise ValueError("Total amount mismatch")
        

        

        result = self._order_dao.save_order(order_form)
        return result
    
    def get_order(self, request_id: str):
        return self._order_dao.get_order(request_id)