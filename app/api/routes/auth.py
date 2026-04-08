from fastapi import APIRouter, Depends, HTTPException

from app.controllers.auth_controller import AuthController, get_current_user, get_user_service
from app.schemas import UserCreate, UserLogin, Token, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201, summary="Register a new user")
async def register(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """
    Register a new user account.

    **Successful example:**
    - email: "newuser@example.com"
    - password: "securepass123"
    - name: "Jane Doe"
    - role: "user" (optional)

    **Failure cases:**
    - Email already exists: Returns 400 error
    - Password too short: Returns validation error
    - Missing required fields: Returns validation error
    """
    try:
        user = await service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token, summary="Login user")
async def login(
    user_data: UserLogin,
    service: UserService = Depends(get_user_service)
):
    """
    Login with email and password.

    **Successful example:**
    - email: "user@example.com"
    - password: "password123"

    Returns access token to use in subsequent requests:
    - Use the token in Authorization header: "Bearer <token>"

    **Failure cases:**
    - Invalid email: Returns 401 Unauthorized
    - Wrong password: Returns 401 Unauthorized
    - User doesn't exist: Returns 401 Unauthorized
    """
    from app.core.security import create_access_token
    
    user = await service.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return Token(access_token=access_token, token_type="bearer")
