from app.dto.order_dto import OrderRequest
from app.services.order_service import OrderService
from fastapi import APIRouter

router = APIRouter(prefix="/api/order", tags=["Order"])

_order_service = OrderService()

@router.get("/")
def home():
    return {"message": "Order Management API Working"}

@router.post("/add-order")
def create_order(order_form: OrderRequest):
    return _order_service.add_new_order(order_form)