from app.dao.orders_dao import OrderDAO
from app.dto.order_dto import OrderRequest, OrderUpdate


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
    
    def update_order(self, id: int, order_update: OrderUpdate):
        #Fetch existing order
        order = self._order_dao.get_order(id)
        if not order:
            return {"error": "Order not found"}

        #Apply only allowed updates (status, approved_by)
        if order_update.status is not None:
            order.status = order_update.status
        if order_update.approved_by is not None:
            order.approved_by = order_update.approved_by

        #Save updated order via DAO
        self._order_dao.update_order(id, order)

        #Return success message
        return {"message": f"Order {id} updated successfully"}
        pass

    def cancel_order(self, order_id: str):
     return self._order_dao.cancel_order(order_id)
