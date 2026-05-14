from app.dto.order_dto import OrderRequest
from app.dto.order_dto import OrderUpdate
from app.services.order_service import OrderService
from fastapi import APIRouter

router = APIRouter(prefix="/api/order", tags=["Order"])

_order_service = OrderService()

@router.get("/")
def home():
    return {"message": "Order Management API Working"}

@router.put("/update-order/{id}")
def update_order(id: int, order_update: OrderUpdate):
    return _order_service.update_order(id, order_update)


@router.post("/add-order")
def create_order(order_form: OrderRequest):
    return _order_service.add_new_order(order_form)

