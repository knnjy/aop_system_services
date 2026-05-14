from app.dao.orders_dao import OrderDAO
from app.dto.order_dto import OrderRequest
from app.dto.order_dto import OrderUpdate
from app.utils.helpers import get_current_timestamp


class OrderService:
    def __init__(self):
        self._order_dao = OrderDAO()

def update_order(self, id: int, order_update: OrderUpdate):
    order = self._order_dao.get_order_by_id(id)
    if not order:
        return {"error": "Order not found"}

    for key, value in order_update.dict(exclude_unset=True).items():
        setattr(order, key, value)

    order.date_updated = get_current_timestamp()
    self._order_dao.save_order(order)
    return {"message": f"Order {id} updated successfully"}

    def add_new_order(self, order_form: OrderRequest):
        pass
