import asyncio
import aioredis

from app.db.mongodb import get_database
from app.db.redis import get_redis


async def order_created_handler(message):
    """Handle order.created event"""
    print(f"📦 Order created: {message}")
    # Add analytics/logging logic here


async def product_updated_handler(message):
    """Handle product.updated event"""
    print(f"📝 Product updated: {message}")
    # Invalidate caches, update analytics


async def review_created_handler(message):
    """Handle review.created event"""
    print(f"⭐ Review created: {message}")
    # Update product ratings, send notifications


async def subscribe_to_events():
    """Subscribe to Redis Pub/Sub events"""
    redis = get_redis()
    pubsub = redis.pubsub()

    await pubsub.subscribe("order.created", "product.updated", "review.created")

    print("✓ Worker listening for events...")

    async for message in pubsub.listen():
        if message["type"] == "message":
            channel = message["channel"].decode()
            data = message["data"].decode()

            if channel == "order.created":
                await order_created_handler(data)
            elif channel == "product.updated":
                await product_updated_handler(data)
            elif channel == "review.created":
                await review_created_handler(data)


async def main():
    from app.db.mongodb import connect_to_mongo
    from app.db.redis import connect_to_redis

    await connect_to_mongo()
    await connect_to_redis()

    try:
        await subscribe_to_events()
    except KeyboardInterrupt:
        print("\n✗ Worker stopped")


if __name__ == "__main__":
    asyncio.run(main())
