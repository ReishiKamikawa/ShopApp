from datetime import datetime
from typing import List, Optional

from bson import ObjectId

from app.db.mongodb import get_database
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas import OrderResponse, OrderItemResponse
from app.db.redis import get_redis


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        cart_repository: CartRepository,
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.cart_repository = cart_repository
        self.redis = get_redis()

    async def create_order(self, user_id: str) -> OrderResponse:
        """Create order with transaction support"""
        db = get_database()
        
        # Get cart
        cart = await self.cart_repository.get_by_user_id(user_id)
        if not cart or not cart.get("items"):
            raise ValueError("Cart is empty")
        
        # Validate and prepare items
        order_items = []
        total_price = 0.0
        
        for cart_item in cart["items"]:
            product = await self.product_repository.get_by_id(str(cart_item["product_id"]))
            if not product:
                raise ValueError(f"Product {cart_item['product_id']} not found")
            
            # Try to decrease stock atomically
            success = await self.product_repository.decrease_stock(
                str(product["_id"]),
                cart_item["quantity"]
            )
            if not success:
                raise ValueError(f"Insufficient stock for product {product['name']}")
            
            order_items.append({
                "product_id": str(product["_id"]),  # Convert to string
                "quantity": cart_item["quantity"],
                "price": product["price"]
            })
            total_price += product["price"] * cart_item["quantity"]
        
        # Create order
        order_data = {
            "user_id": ObjectId(user_id),
            "items": order_items,
            "total_price": total_price,
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        
        order = await self.order_repository.create(order_data)
        
        # Clear cart
        await self.cart_repository.clear_cart(user_id)
        
        # Publish event
        await self.redis.publish("order.created", f"{order['_id']}")
        
        # Convert user_id to string for response
        order["user_id"] = str(order["user_id"])
        return OrderResponse(**order)

    async def get_order_by_id(self, order_id: str) -> Optional[OrderResponse]:
        order = await self.order_repository.get_by_id(order_id)
        if order:
            order["user_id"] = str(order["user_id"])
            return OrderResponse(**order)
        return None

    async def get_user_orders(self, user_id: str, page: int = 1, limit: int = 10) -> List[OrderResponse]:
        skip = (page - 1) * limit
        orders = await self.order_repository.get_by_user_id(user_id, skip, limit)
        result = []
        for order in orders:
            order["user_id"] = str(order["user_id"])
            result.append(OrderResponse(**order))
        return result

    async def get_all_orders(self, page: int = 1, limit: int = 10) -> List[OrderResponse]:
        skip = (page - 1) * limit
        orders = await self.order_repository.get_all(skip, limit)
        result = []
        for order in orders:
            order["user_id"] = str(order["user_id"])
            result.append(OrderResponse(**order))
        return result

    async def update_order_status(self, order_id: str, status: str) -> bool:
        return await self.order_repository.update(order_id, {"status": status})
