from typing import List, Optional

from bson import ObjectId

from app.repositories.review_repository import ReviewRepository
from app.schemas import ReviewCreate, ReviewResponse


class ReviewService:
    def __init__(self, review_repository: ReviewRepository):
        self.review_repository = review_repository

    async def create_review(self, user_id: str, review_data: ReviewCreate) -> ReviewResponse:
        # Check if user already reviewed this product
        existing = await self.review_repository.get_by_user_and_product(user_id, review_data.product_id)
        if existing:
            raise ValueError("You already reviewed this product")
        
        from datetime import datetime
        review_dict = review_data.dict()
        review_dict["user_id"] = ObjectId(user_id)
        review_dict["product_id"] = ObjectId(review_dict["product_id"])
        review_dict["created_at"] = datetime.utcnow()

        review = await self.review_repository.create(review_dict)
        # Convert ObjectIds to strings
        review["user_id"] = str(review["user_id"])
        review["product_id"] = str(review["product_id"])
        return ReviewResponse(**review)

    async def get_review_by_id(self, review_id: str) -> Optional[ReviewResponse]:
        review = await self.review_repository.get_by_id(review_id)
        if review:
            # Convert ObjectIds to strings
            review["user_id"] = str(review["user_id"])
            review["product_id"] = str(review["product_id"])
            return ReviewResponse(**review)
        return None

    async def get_product_reviews(self, product_id: str, page: int = 1, limit: int = 10) -> List[ReviewResponse]:
        skip = (page - 1) * limit
        reviews = await self.review_repository.get_by_product_id(product_id, skip, limit)
        result = []
        for review in reviews:
            review["user_id"] = str(review["user_id"])
            review["product_id"] = str(review["product_id"])
            result.append(ReviewResponse(**review))
        return result

    async def get_all_reviews(self, page: int = 1, limit: int = 10) -> List[ReviewResponse]:
        skip = (page - 1) * limit
        reviews = await self.review_repository.get_all(skip, limit)
        result = []
        for review in reviews:
            review["user_id"] = str(review["user_id"])
            review["product_id"] = str(review["product_id"])
            result.append(ReviewResponse(**review))
        return result

    async def delete_review(self, review_id: str) -> bool:
        return await self.review_repository.delete(review_id)
