from datetime import datetime
from typing import List, Optional, Annotated

from pydantic import BaseModel, Field, PlainSerializer, WithJsonSchema
from bson import ObjectId


def serialize_object_id(value):
    """Serialize ObjectId to string"""
    return str(value) if value else None


PyObjectId = Annotated[
    ObjectId,
    PlainSerializer(serialize_object_id),
    WithJsonSchema({"type": "string"})
]


# User schemas
class UserVerifyOTP(BaseModel):
    email: str = Field(..., example="john@example.com", description="User email")
    otp_code: str = Field(..., example="123456", description="6-digit OTP code")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "otp_code": "123456"
            }
        }


class UserCreate(BaseModel):
    email: str = Field(..., example="john@example.com", description="User email address")
    password: str = Field(..., example="password123", description="User password (min 6 characters)")
    name: str = Field(..., example="John Doe", description="User full name")
    role: Optional[str] = Field(default="user", example="user", description="User role: user or admin")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "password123",
                "name": "John Doe",
                "role": "user"
            }
        }


class UserLogin(BaseModel):
    email: str = Field(..., example="john@example.com", description="User email")
    password: str = Field(..., example="password123", description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "password123"
            }
        }


class UserResponse(BaseModel):
    id: PyObjectId = Field(alias="_id", example="507f1f77bcf86cd799439011")
    email: str = Field(..., example="john@example.com")
    name: str = Field(..., example="John Doe")
    role: str = Field(..., example="user")
    is_verified: bool = Field(default=False, example=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}


class Token(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(default="bearer", example="bearer")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


# Product schemas
class ProductCreate(BaseModel):
    name: str = Field(..., example="Laptop", description="Product name")
    description: str = Field(..., example="High-performance laptop for gaming", description="Product description")
    price: float = Field(..., gt=0, example=999.99, description="Product price (must be > 0)")
    stock: int = Field(..., ge=0, example=50, description="Available stock quantity")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Laptop",
                "description": "High-performance laptop for gaming",
                "price": 999.99,
                "stock": 50
            }
        }


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Laptop Pro", description="Updated product name")
    description: Optional[str] = Field(None, example="Updated description")
    price: Optional[float] = Field(None, example=1299.99)
    stock: Optional[int] = Field(None, example=30)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Laptop Pro",
                "price": 1299.99,
                "stock": 30
            }
        }


class ProductResponse(BaseModel):
    id: PyObjectId = Field(alias="_id", example="507f1f77bcf86cd799439011")
    name: str = Field(..., example="Laptop")
    description: str = Field(..., example="High-performance laptop for gaming")
    price: float = Field(..., example=999.99)
    stock: int = Field(..., example=50)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}


# Cart schemas
class CartItemCreate(BaseModel):
    product_id: str = Field(..., example="507f1f77bcf86cd799439011", description="Product ID to add")
    quantity: int = Field(..., gt=0, example=2, description="Quantity to add (must be > 0)")

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "507f1f77bcf86cd799439011",
                "quantity": 2
            }
        }


class CartItemResponse(BaseModel):
    product_id: str = Field(..., example="507f1f77bcf86cd799439011")
    quantity: int = Field(..., example=2)


class CartResponse(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id", example="507f1f77bcf86cd799439011")
    user_id: str = Field(..., example="507f1f77bcf86cd799439012")
    items: List[CartItemResponse]
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}


# Order schemas
class OrderCreate(BaseModel):
    """Create order from cart - no additional data needed"""
    pass


class OrderItemResponse(BaseModel):
    product_id: str = Field(..., example="507f1f77bcf86cd799439011")
    quantity: int = Field(..., example=2)
    price: float = Field(..., example=999.99)


class OrderResponse(BaseModel):
    id: PyObjectId = Field(alias="_id", example="507f1f77bcf86cd799439013")
    user_id: str = Field(..., example="507f1f77bcf86cd799439012")
    items: List[OrderItemResponse]
    total_price: float = Field(..., example=1999.98)
    status: str = Field(..., example="pending")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}


# Review schemas
class ReviewCreate(BaseModel):
    product_id: str = Field(..., example="507f1f77bcf86cd799439011", description="Product ID to review")
    rating: int = Field(..., gt=0, le=5, example=5, description="Rating from 1-5 (must be between 1 and 5)")
    comment: str = Field(..., example="Great product!", description="Review comment")

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "507f1f77bcf86cd799439011",
                "rating": 5,
                "comment": "Great product! Highly recommended."
            }
        }


class ReviewResponse(BaseModel):
    id: PyObjectId = Field(alias="_id", example="507f1f77bcf86cd799439014")
    user_id: str = Field(..., example="507f1f77bcf86cd799439012")
    product_id: str = Field(..., example="507f1f77bcf86cd799439011")
    rating: int = Field(..., example=5)
    comment: str = Field(..., example="Great product!")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}

    @classmethod
    def from_dict(cls, data: dict):
        """Convert ObjectIds to strings for response"""
        if isinstance(data.get("user_id"), ObjectId):
            data["user_id"] = str(data["user_id"])
        if isinstance(data.get("product_id"), ObjectId):
            data["product_id"] = str(data["product_id"])
        if "created_at" not in data:
            data["created_at"] = datetime.utcnow()
        return cls(**data)

