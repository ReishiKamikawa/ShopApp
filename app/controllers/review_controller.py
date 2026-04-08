from fastapi import Depends, HTTPException

from app.controllers.abstract_controller import AbstractController
from app.repositories.review_repository import ReviewRepository
from app.services.review_service import ReviewService
from app.schemas import ReviewCreate, ReviewResponse


def get_review_repository() -> ReviewRepository:
    return ReviewRepository()


def get_review_service(repo: ReviewRepository = Depends(get_review_repository)) -> ReviewService:
    return ReviewService(repo)


class ReviewController(AbstractController[ReviewResponse]):
    def __init__(self, service: ReviewService = Depends(get_review_service)):
        super().__init__(service)
        self.service = service

    async def create(self, data: ReviewCreate) -> ReviewResponse:
        return await self.service.create_review(data)

    async def get_by_id(self, id: str) -> ReviewResponse:
        review = await self.service.get_review_by_id(id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return review

    async def get_all(self, page: int = 1, limit: int = 10) -> list:
        return await self.service.get_all_reviews(page, limit)

    async def get_product_reviews(self, product_id: str, page: int = 1, limit: int = 10) -> list:
        return await self.service.get_product_reviews(product_id, page, limit)

    async def update(self, id: str, data: dict) -> bool:
        # Reviews typically shouldn't be updated
        raise HTTPException(status_code=403, detail="Cannot update reviews")

    async def delete(self, id: str) -> bool:
        success = await self.service.delete_review(id)
        if not success:
            raise HTTPException(status_code=404, detail="Review not found")
        return success
