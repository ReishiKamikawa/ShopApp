"""
Seed database with test data for API testing in Swagger UI
"""
import asyncio
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from app.core.security import get_password_hash


async def connect_db() -> AsyncIOMotorDatabase:
    """Connect to MongoDB"""
    client = AsyncIOMotorClient(settings.mongodb_url)
    return client[settings.database_name]


async def seed_data():
    """Seed the database with test data"""
    db = await connect_db()

    # Clear existing data
    print("🗑️  Clearing existing data...")
    await db.users.delete_many({})
    await db.products.delete_many({})
    await db.carts.delete_many({})
    await db.orders.delete_many({})
    await db.reviews.delete_many({})

    # ============= CREATE TEST USERS =============
    print("\n👥 Creating test users...")

    try:
        pwd = get_password_hash("password123")
        user1_data = {
            "email": "user1@example.com",
            "password": pwd,
            "name": "John Doe",
            "role": "user",
            "created_at": datetime.utcnow()
        }
    except Exception as hash_err:
        # Fallback: use bcrypt directly
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"])
        try:
            pwd = pwd_context.hash("password123")
            user1_data = {
                "email": "user1@example.com",
                "password": pwd,
                "name": "John Doe",
                "role": "user",
                "created_at": datetime.utcnow()
            }
        except Exception:
            print(f"⚠️  Skipping password hashing, using plain text (for testing only)")
            user1_data = {
                "email": "user1@example.com",
                "password": "password123_plain",
                "name": "John Doe",
                "role": "user",
                "created_at": datetime.utcnow()
            }

    user1_result = await db.users.insert_one(user1_data)
    user1_id = str(user1_result.inserted_id)
    print(f"✅ User 1 created: {user1_data['email']} (ID: {user1_id})")

    try:
        pwd = get_password_hash("password456")
        user2_data = {
            "email": "user2@example.com",
            "password": pwd,
            "name": "Jane Smith",
            "role": "user",
            "created_at": datetime.utcnow()
        }
    except Exception as hash_err:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"])
        try:
            pwd = pwd_context.hash("password456")
            user2_data = {
                "email": "user2@example.com",
                "password": pwd,
                "name": "Jane Smith",
                "role": "user",
                "created_at": datetime.utcnow()
            }
        except Exception:
            user2_data = {
                "email": "user2@example.com",
                "password": "password456_plain",
                "name": "Jane Smith",
                "role": "user",
                "created_at": datetime.utcnow()
            }

    user2_result = await db.users.insert_one(user2_data)
    user2_id = str(user2_result.inserted_id)
    print(f"✅ User 2 created: {user2_data['email']} (ID: {user2_id})")

    # ============= CREATE TEST PRODUCTS =============
    print("\n🛍️  Creating test products...")

    products = [
        {
            "name": "Laptop Pro",
            "description": "High-performance laptop for developers and gamers",
            "price": 1499.99,
            "stock": 15,
            "created_at": datetime.utcnow()
        },
        {
            "name": "Wireless Mouse",
            "description": "Ergonomic wireless mouse with 2.4GHz connection",
            "price": 29.99,
            "stock": 150,
            "created_at": datetime.utcnow()
        },
        {
            "name": "USB-C Hub",
            "description": "7-in-1 USB-C hub with multiple ports",
            "price": 49.99,
            "stock": 80,
            "created_at": datetime.utcnow()
        },
        {
            "name": "Mechanical Keyboard",
            "description": "RGB mechanical keyboard with Cherry MX switches",
            "price": 149.99,
            "stock": 25,
            "created_at": datetime.utcnow()
        },
        {
            "name": "4K Monitor",
            "description": "27-inch 4K ultra HD monitor with USB-C",
            "price": 599.99,
            "stock": 10,
            "created_at": datetime.utcnow()
        }
    ]

    product_ids = []
    for product in products:
        result = await db.products.insert_one(product)
        product_id = str(result.inserted_id)
        product_ids.append(product_id)
        print(f"✅ Product created: {product['name']} (${product['price']}, Stock: {product['stock']})")

    # ============= CREATE TEST CARTS =============
    print("\n🛒 Creating test carts...")

    cart1_data = {
        "user_id": user1_id,
        "items": [
            {"product_id": product_ids[0], "quantity": 1},
            {"product_id": product_ids[1], "quantity": 2}
        ],
        "updated_at": datetime.utcnow()
    }
    cart1_result = await db.carts.insert_one(cart1_data)
    print(f"✅ Cart 1 created for user1 with {len(cart1_data['items'])} items")

    cart2_data = {
        "user_id": user2_id,
        "items": [
            {"product_id": product_ids[2], "quantity": 1},
            {"product_id": product_ids[3], "quantity": 1}
        ],
        "updated_at": datetime.utcnow()
    }
    cart2_result = await db.carts.insert_one(cart2_data)
    print(f"✅ Cart 2 created for user2 with {len(cart2_data['items'])} items")

    # ============= CREATE TEST ORDERS =============
    print("\n📦 Creating test orders...")

    order1_data = {
        "user_id": user1_id,
        "items": [
            {"product_id": product_ids[4], "quantity": 1, "price": 599.99},
            {"product_id": product_ids[0], "quantity": 1, "price": 1499.99}
        ],
        "total_price": 2099.98,
        "status": "completed",
        "created_at": datetime.utcnow()
    }
    order1_result = await db.orders.insert_one(order1_data)
    order1_id = str(order1_result.inserted_id)
    print(f"✅ Order 1 created for user1: Total ${order1_data['total_price']} (Status: {order1_data['status']})")

    order2_data = {
        "user_id": user2_id,
        "items": [
            {"product_id": product_ids[1], "quantity": 3, "price": 29.99}
        ],
        "total_price": 89.97,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    order2_result = await db.orders.insert_one(order2_data)
    order2_id = str(order2_result.inserted_id)
    print(f"✅ Order 2 created for user2: Total ${order2_data['total_price']} (Status: {order2_data['status']})")

    # ============= CREATE TEST REVIEWS =============
    print("\n⭐ Creating test reviews...")

    reviews = [
        {
            "user_id": user1_id,
            "product_id": product_ids[0],
            "rating": 5,
            "comment": "Excellent laptop! Very fast and reliable for development.",
            "created_at": datetime.utcnow()
        },
        {
            "user_id": user2_id,
            "product_id": product_ids[0],
            "rating": 4,
            "comment": "Great laptop, bit expensive but worth it.",
            "created_at": datetime.utcnow()
        },
        {
            "user_id": user1_id,
            "product_id": product_ids[1],
            "rating": 5,
            "comment": "Perfect wireless mouse! Great ergonomics.",
            "created_at": datetime.utcnow()
        },
        {
            "user_id": user2_id,
            "product_id": product_ids[2],
            "rating": 4,
            "comment": "Good hub, very useful for my setup.",
            "created_at": datetime.utcnow()
        },
        {
            "user_id": user1_id,
            "product_id": product_ids[3],
            "rating": 5,
            "comment": "Amazing keyboard! Love the mechanical switches.",
            "created_at": datetime.utcnow()
        }
    ]

    for review in reviews:
        result = await db.reviews.insert_one(review)
        print(f"✅ Review created: {review['rating']}⭐ for {product_ids.index(review['product_id']) + 1} by user")

    # ============= PRINT TEST CREDENTIALS =============
    print("\n" + "="*60)
    print("✨ DATABASE SEEDED SUCCESSFULLY!")
    print("="*60)
    print("\n📝 TEST CREDENTIALS FOR SWAGGER UI:\n")
    print("User 1:")
    print(f"  Email: user1@example.com")
    print(f"  Password: password123")
    print(f"  ID: {user1_id}\n")
    print("User 2:")
    print(f"  Email: user2@example.com")
    print(f"  Password: password456")
    print(f"  ID: {user2_id}\n")

    print("📦 PRODUCT IDS (for testing):\n")
    product_names = ["Laptop Pro", "Wireless Mouse", "USB-C Hub", "Mechanical Keyboard", "4K Monitor"]
    for i, product_id in enumerate(product_ids):
        print(f"  {product_names[i]}: {product_id}")

    print("\n📋 ORDER IDS (for testing):\n")
    print(f"  Order 1: {order1_id}")
    print(f"  Order 2: {order2_id}")

    print("\n" + "="*60)
    print("🧪 TESTING FLOW:\n")
    print("1. POST /auth/register - Register a new user")
    print("2. POST /auth/login - Login with user1@example.com / password123")
    print("3. POST /products - Create a new product")
    print("4. GET /products - List all products")
    print("5. GET /products/{product_id} - Get a specific product")
    print("6. POST /cart/add - Add item to cart (requires token)")
    print("7. GET /cart - View your cart (requires token)")
    print("8. POST /orders - Create order from cart (requires token)")
    print("9. GET /orders - List your orders (requires token)")
    print("10. POST /reviews - Create a review (requires token)")
    print("11. GET /reviews/product/{product_id} - Get product reviews")
    print("="*60 + "\n")


if __name__ == "__main__":
    print("🌱 Starting database seeding...\n")
    asyncio.run(seed_data())
    print("✅ Done!")







