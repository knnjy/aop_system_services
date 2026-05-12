from app.services.order_service import OrderService
from fastapi import APIRouter

router = APIRouter(prefix="/api/order", tags=["Order"])

_order_service = OrderService()

@router.get("/")
def home():
    return {"message": "Order Management API Working"}


@router.post("/add-order")
def create_order():
    return {}