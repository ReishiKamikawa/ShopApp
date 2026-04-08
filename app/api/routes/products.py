from fastapi import APIRouter, Depends, HTTPException

from app.controllers.product_controller import ProductController, get_product_service
from app.schemas import ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductResponse, summary="Create a new product", status_code=201)
async def create_product(
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service)
):
    """
    Create a new product.

    **Successful example:**
    - name: "Laptop"
    - description: "High-performance laptop"
    - price: 999.99
    - stock: 50

    **Failure cases:**
    - Empty fields will fail validation
    - Negative price will fail validation
    """
    return await service.create_product(product_data)


@router.get("/{product_id}", response_model=ProductResponse, summary="Get product by ID")
async def get_product(
    product_id: str,
    service: ProductService = Depends(get_product_service)
):
    """
    Get a product by its ID.

    **Successful example:** Use a valid product ID (from create product response)

    **Failure cases:**
    - Invalid or non-existent product ID: Returns 404
    - Malformed ObjectId: Returns 400
    """
    try:
        from bson import ObjectId
        # Validate it's a valid ObjectId format
        ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product ID format")

    product = await service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("", response_model=list, summary="List all products")
async def list_products(
    page: int = 1,
    limit: int = 10,
    sort: str = "created_at",
    service: ProductService = Depends(get_product_service)
):
    """
    List all products with pagination.

    **Query parameters:**
    - page: Page number (default: 1)
    - limit: Items per page (default: 10)
    - sort: Sort field (default: created_at)

    **Successful example:** Call without parameters or with page=1, limit=10

    **Failure cases:**
    - page < 1: Returns empty list
    - limit <= 0: Returns validation error
    """
    return await service.get_all_products(page, limit, sort)


@router.patch("/{product_id}", response_model=bool, summary="Update a product")
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    service: ProductService = Depends(get_product_service)
):
    """
    Update a product's details.

    **Successful example:** Use valid product ID and partial update data

    **Failure cases:**
    - Non-existent product ID: Returns false
    - Negative price: Returns validation error
    """
    return await service.update_product(product_id, product_data)


@router.delete("/{product_id}", response_model=bool, summary="Delete a product")
async def delete_product(
    product_id: str,
    service: ProductService = Depends(get_product_service)
):
    """
    Delete a product by ID.

    **Successful example:** Use valid product ID

    **Failure cases:**
    - Non-existent product ID: Returns false
    """
    return await service.delete_product(product_id)
