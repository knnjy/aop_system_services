from app.dto.order_dto import OrderRequest, OrderUpdate 
from app.services.order_service import OrderService
from fastapi import APIRouter

router = APIRouter(prefix="/api/orders", tags=["Order"])

_order_service = OrderService()

@router.get("/")
def home():
    return {"message": "Order Management API Working"}

@router.post("/add-order")
def create_order(order_form: OrderRequest):
    return _order_service.add_new_order(order_form)

@router.get("/get-order/{id}")
def get_order(id: str):
    return _order_service.get_order(id)

@router.put("/update-order/{id}")
def update_order(id: str, order_update: OrderUpdate):
    return _order_service.update_order(id, order_update)

@router.delete("/{id}")
def cancel_order(id: str):
    return _order_service.cancel_order(id)

