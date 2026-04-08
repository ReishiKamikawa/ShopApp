from fastapi import APIRouter, Depends, Header, HTTPException

from app.controllers.review_controller import ReviewController, get_review_service
from app.schemas import ReviewCreate, ReviewResponse
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["reviews"])


async def get_user_id_from_header(authorization: str = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized - Missing authorization header")
    from app.core.security import decode_access_token
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized - Invalid token")


@router.post("", response_model=ReviewResponse, status_code=201, summary="Create a product review")
async def create_review(
    review_data: ReviewCreate,
    user_id: str = Depends(get_user_id_from_header),
    service: ReviewService = Depends(get_review_service)
):
    """
    Create a review for a product.
    
    **Required:** Authorization header with Bearer token
    
    **Successful example:**
    - product_id: "507f1f77bcf86cd799439011" (valid product ID)
    - rating: 5 (1-5 scale)
    - comment: "Great product!"
    - Authorization: Bearer <valid_token>
    
    **Failure cases:**
    - Missing Authorization header: Returns 401
    - Invalid token: Returns 401
    - Rating < 1 or > 5: Returns validation error
    - Product doesn't exist: Returns 400
    - Duplicate review (same user + product): Returns 400
    - Empty comment: Returns validation error
    """
    try:
        return await service.create_review(user_id, review_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{review_id}", response_model=ReviewResponse, summary="Get review by ID")
async def get_review(
    review_id: str, 
    service: ReviewService = Depends(get_review_service)
):
    """
    Get a review by its ID.
    
    **Path parameters:**
    - review_id: Review ID (from create review response)
    
    **Successful example:**
    - review_id: "507f1f77bcf86cd799439014"
    
    **Failure cases:**
    - Non-existent review ID: Returns 404
    - Invalid review ID format: Returns 400
    """
    review = await service.get_review_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.get("", response_model=list, summary="List all reviews")
async def list_reviews(
    page: int = 1, 
    limit: int = 10, 
    service: ReviewService = Depends(get_review_service)
):
    """
    List all reviews with pagination.
    
    **Query parameters:**
    - page: Page number (default: 1)
    - limit: Items per page (default: 10)
    
    **Successful example:**
    - page=1, limit=10
    
    **Failure cases:**
    - page < 1: Returns empty list
    - limit <= 0: Returns validation error
    """
    return await service.get_all_reviews(page, limit)


@router.get("/product/{product_id}", response_model=list, summary="Get reviews for a product")
async def get_product_reviews(
    product_id: str,
    page: int = 1,
    limit: int = 10,
    service: ReviewService = Depends(get_review_service)
):
    """
    Get all reviews for a specific product.
    
    **Path parameters:**
    - product_id: Product ID to get reviews for
    
    **Query parameters:**
    - page: Page number (default: 1)
    - limit: Items per page (default: 10)
    
    **Successful example:**
    - product_id: "507f1f77bcf86cd799439011"
    - page=1, limit=10
    
    **Failure cases:**
    - Non-existent product ID: Returns empty list or 404
    - Invalid page/limit: Returns validation error
    """
    return await service.get_product_reviews(product_id, page, limit)


@router.delete("/{review_id}", response_model=bool, summary="Delete a review")
async def delete_review(
    review_id: str, 
    service: ReviewService = Depends(get_review_service)
):
    """
    Delete a review by its ID.
    
    **Path parameters:**
    - review_id: Review ID to delete
    
    **Successful example:**
    - review_id: "507f1f77bcf86cd799439014"
    
    **Failure cases:**
    - Non-existent review ID: Returns false
    - Invalid review ID format: Returns 400
    """
    return await service.delete_review(review_id)
