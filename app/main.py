from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.redis import connect_to_redis, close_redis_connection
from app.api.routes import auth, products, orders, reviews, cart


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    await connect_to_redis()
    print("✓ Application startup complete")
    
    yield
    
    # Shutdown
    await close_mongo_connection()
    await close_redis_connection()
    print("✓ Application shutdown complete")


app = FastAPI(
    title="ShopApp API",
    description="E-commerce Mini Backend System",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(reviews.router)
app.include_router(cart.router)


@app.get("/")
async def root():
    return {"message": "Welcome to ShopApp API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
