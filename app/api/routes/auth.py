from fastapi import APIRouter, Depends, HTTPException

from app.controllers.auth_controller import AuthController, get_current_user, get_user_service
from app.schemas import UserCreate, UserLogin, Token, UserResponse, UserVerifyOTP
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


@router.post("/verify-otp", response_model=dict, summary="Verify User OTP")
async def verify_otp(
    verification_data: UserVerifyOTP,
    service: UserService = Depends(get_user_service)
):
    """
    Verify the 6-digit OTP sent to the user's email.
    
    **Successful example:**
    - email: "newuser@example.com"
    - otp_code: "123456"
    
    **Failure cases:**
    - Invalid or expired OTP: Returns 400 error
    """
    success = await service.verify_otp(verification_data.email, verification_data.otp_code)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
        
    return {"message": "Account successfully verified."}


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
    
    try:
        user = await service.authenticate_user(user_data.email, user_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except ValueError as e:
        # Catch Account not verified error
        raise HTTPException(status_code=403, detail=str(e))
    
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return Token(access_token=access_token, token_type="bearer")
