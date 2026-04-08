from fastapi import Header, HTTPException


async def verify_role(authorization: str = Header(None), required_role: str = None):
    """Verify user role from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    from app.core.security import decode_access_token
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_role = payload.get("role")
        
        if required_role and user_role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        return {"user_id": payload.get("sub"), "role": user_role}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
