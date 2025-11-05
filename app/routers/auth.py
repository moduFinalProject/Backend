from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from app.database import get_db
from app.models import User
from app.security import (
    PasswordHasher, 
    create_access_token, 
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["인증"])

# ===== 요청/응답 스키마 =====
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="최소 8자 이상")
    name: str = Field(..., min_length=2, max_length=50)
    phone: Optional[str] = None
    user_type: str = Field(default="job_seeker", description="job_seeker 또는 employer")

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    phone: Optional[str]
    user_type: str
    
    class Config:
        from_attributes = True


# ===== 회원가입 =====
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    회원가입
    - 이메일 중복 확인
    - 비밀번호 해싱 (PBKDF2-HMAC-SHA256)
    - 사용자 생성
    """
    
    # 1. 이메일 중복 확인
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다"
        )
    
    # 2. 비밀번호 해싱 (security.py의 PasswordHasher 사용)
    hashed_password = PasswordHasher.hash_password_combined(user_data.password)
    
    # 3. 사용자 생성
    new_user = User(
        email=user_data.email,
        password=hashed_password,
        name=user_data.name,
        phone=user_data.phone,
        user_type=user_data.user_type
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


# ===== 로그인 =====
@router.post("/login", response_model=TokenResponse)
def login(
    login_data: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    로그인
    - 이메일로 사용자 조회
    - 비밀번호 검증 (security.py의 PasswordHasher 사용)
    - JWT 토큰 생성 (security.py의 create_access_token 사용)
    """
    
    # 1. 사용자 조회
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다"
        )
    
    # 2. 비밀번호 검증 (security.py의 verify_password_combined 사용)
    if not PasswordHasher.verify_password_combined(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못되었습니다"
        )
    
    # 3. JWT 토큰 생성 (security.py의 create_access_token 사용)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # 4. 응답
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "user_type": user.user_type
        }
    }


# ===== 현재 사용자 정보 조회 =====
@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    현재 로그인한 사용자 정보 조회
    - security.py의 get_current_user 의존성 사용
    - Authorization: Bearer <token> 헤더 필수
    """
    return current_user


# ===== 로그아웃 =====
@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user)
):
    """
    로그아웃
    - JWT는 stateless이므로 서버에서 할 일은 없음
    - 클라이언트에서 토큰 삭제 필요
    """
    return {
        "message": "로그아웃되었습니다",
        "user_id": current_user.id
    }


# ===== 비밀번호 변경 =====
@router.put("/change-password")
def change_password(
    old_password: str,
    new_password: str = Field(..., min_length=8),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    비밀번호 변경
    - 기존 비밀번호 확인
    - 새 비밀번호로 변경 (해싱)
    """
    
    # 1. 기존 비밀번호 확인
    if not PasswordHasher.verify_password_combined(old_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="기존 비밀번호가 일치하지 않습니다"
        )
    
    # 2. 새 비밀번호 해싱
    new_hashed_password = PasswordHasher.hash_password_combined(new_password)
    
    # 3. 비밀번호 업데이트
    current_user.password = new_hashed_password
    db.commit()
    
    return {"message": "비밀번호가 변경되었습니다"}