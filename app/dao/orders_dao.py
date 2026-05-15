from datetime import datetime
import pandas as pd
from datetime import datetime
from typing import Optional

from app.dto.order_dto import OrderItem, OrderRequest
from app.utils.csv_loader import load_csv, DATA_DIR

class OrderDAO:
    def __init__(self) -> None:
        # These are DataFrames
        self._book_orders = load_csv("orders/book_order.csv")
        self._book_orders_item = load_csv("orders/book_order_item.csv")
        self._uniform_orders = load_csv("orders/uniform_order.csv")
        self._uniform_orders_item = load_csv("orders/uniform_order_item.csv")

    def get_order(self, request_id: str) -> Optional[OrderRequest]:
        if request_id.startswith("BOF"):
            orders_df = self._book_orders
            items_df = self._book_orders_item
            id_field = "book_order_id"
            product_field = "book_id"
        elif request_id.startswith("UOF"):
            orders_df = self._uniform_orders
            items_df = self._uniform_orders_item
            id_field = "uniform_order_id"
            product_field = "uniform_size_id"
        else:
            return None

        order_rows = orders_df.loc[orders_df[id_field] == request_id].to_dict("records")
        if not order_rows:
            return None

        order_row = order_rows[0]

        item_rows = items_df.loc[items_df[id_field] == request_id].to_dict("records")

        order_items = [
            OrderItem(
                order_item_id=item["order_item_id"],
                request_id=request_id,
                product_id=item[product_field],
                quantity=int(item["quantity"]),
                unit_price=float(item["unit_price"]),
                subtotal=float(item["subtotal"])
            )
            for item in item_rows
        ]

        return OrderRequest(
            request_id=request_id,
            user_id=order_row["user_id"],
            total_amount=float(order_row["total_amount"]),
            order_items=order_items,
            status=order_row["status"],
            date_created=datetime.strptime(order_row["date_created"], "%Y-%m-%d"),
            approved_by=order_row.get("approved_by") or None
        )

    def save_order(self, order: OrderRequest):
        if order.request_id.startswith("BOF"):
            order_file = DATA_DIR / "orders/book_order.csv"
            item_file = DATA_DIR / "orders/book_order_item.csv"
            id_field = "book_order_id"
            product_field = "book_id"
        elif order.request_id.startswith("UOF"):
            order_file = DATA_DIR / "orders/uniform_order.csv"
            item_file = DATA_DIR / "orders/uniform_order_item.csv"
            id_field = "uniform_order_id"
            product_field = "uniform_size_id"
        else:
            raise ValueError("Unknown order type")

        order_file.parent.mkdir(parents=True, exist_ok=True)
        item_file.parent.mkdir(parents=True, exist_ok=True)

        order_row = {
            id_field: order.request_id,
            "user_id": order.user_id,
            "total_amount": order.total_amount,
            "order_items": len(order.order_items),
            "requested_at": order.date_created.isoformat(timespec="minutes"),
            "status": order.status,
            "date_created": order.date_created.strftime("%Y-%m-%d"),
            "approved_by": order.approved_by or ""
        }

        pd.DataFrame([order_row]).to_csv(order_file, mode="a", header=not order_file.exists(), index=False)

        item_rows = [
            {
                "order_item_id": item.order_item_id,
                id_field: order.request_id,
                product_field: item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "subtotal": item.subtotal
            }
            for item in order.order_items
        ]

        pd.DataFrame(item_rows).to_csv(item_file, mode="a", header=not item_file.exists(), index=False)

        # refresh cache
        if order.request_id.startswith("BOF"):
            self._book_orders = load_csv("orders/book_order.csv")
            self._book_orders_item = load_csv("orders/book_order_item.csv")
        else:
            self._uniform_orders = load_csv("orders/uniform_order.csv")
            self._uniform_orders_item = load_csv("orders/uniform_order_item.csv")

        return {"message": "Order saved successfully", "order_id": order.request_id}

    def update_order(self, request_id: str, updated_order: OrderRequest):
        if request_id.startswith("BOF"):
            order_file = DATA_DIR / "orders/book_order.csv"
            id_field = "book_order_id"
        elif request_id.startswith("UOF"):
            order_file = DATA_DIR / "orders/uniform_order.csv"
            id_field = "uniform_order_id"
        else:
            raise ValueError("Unknown order type")

        orders_df = pd.read_csv(order_file)

        if updated_order.status is not None:
            orders_df.loc[orders_df[id_field] == request_id, "status"] = updated_order.status

        if updated_order.approved_by is not None:
            orders_df.loc[orders_df[id_field] == request_id, "approved_by"] = updated_order.approved_by or ""

        orders_df.to_csv(order_file, index=False)

        if request_id.startswith("BOF"):
            self._book_orders = load_csv("orders/book_order.csv")
        else:
            self._uniform_orders = load_csv("orders/uniform_order.csv")

        return {"message": f"Order {request_id} updated successfully"}
    
        self._orders = load_csv("orders/book_order.csv")

    # ✅ ADD THIS (soft delete)
    def cancel_order(self, order_id: str):
        if order_id.startswith("BOF"):
            order_file = DATA_DIR / "orders/book_order.csv"
            id_field = "book_order_id"
            df = self._book_orders
        elif order_id.startswith("UOF"):
            order_file = DATA_DIR / "orders/uniform_order.csv"
            id_field = "uniform_order_id"
            df = self._uniform_orders
        else:
            return None

        mask = df[id_field] == order_id

        if not mask.any():
            return None

        df.loc[mask, "status"] = "cancelled"
        df.to_csv(order_file, index=False)

        # refresh cache
        if order_id.startswith("BOF"):
            self._book_orders = load_csv("orders/book_order.csv")
        else:
            self._uniform_orders = load_csv("orders/uniform_order.csv")

        return {
            "message": f"Order {order_id} cancelled successfully",
            "status": "cancelled"
        }
