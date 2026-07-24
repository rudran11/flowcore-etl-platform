from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any
from flowcore_server.services.auth import AuthService
from flowcore_server.repositories.interfaces.uow import AbstractUnitOfWork
from flowcore_server.dependencies.core import get_uow
from flowcore_server.dependencies.auth import get_current_user
from flowcore_shared.schemas.auth import UserInDB, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    uow: AbstractUnitOfWork = Depends(get_uow)
) -> Dict[str, Any]:
    async with uow:
        user = await uow.users.get_by_email(form_data.username) # using email as username
        if not user or not AuthService.verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        access_token = AuthService.create_access_token(data={"sub": user.id})
        refresh_token = AuthService.create_refresh_token(data={"sub": user.id})
        
        # Set refresh token as an HttpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True, 
            samesite="lax",
            max_age=7 * 24 * 60 * 60 # 7 days
        )
        
        return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    uow: AbstractUnitOfWork = Depends(get_uow)
) -> Dict[str, Any]:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
        
    try:
        payload = AuthService.verify_token(refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
            
        async with uow:
            user = await uow.users.get(user_id)
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
                
            access_token = AuthService.create_access_token(data={"sub": user.id})
            return {"access_token": access_token, "token_type": "bearer"}
            
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_me(user: UserInDB = Depends(get_current_user)):
    return user
