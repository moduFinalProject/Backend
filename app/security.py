from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError,jwt
import secrets
import os
from app.database import get_db
from app.login_logic import get_user_by_id
from app.config.settings import settings
from sqlalchemy.ext.asyncio import AsyncSession

SECRET_KEY=settings.jwt_secret
ALGORITHM=settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=settings.access_token_expire_minutes


def create_access_token(data:dict):
    
    to_encode = data.copy()
    expire = datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encode_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    
    return encode_jwt



def verify_token(token:str):
    
    try:
        payload = jwt.decode(token, SECRET_KEY,algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None







oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_user(token: str = Depends(oauth2_scheme), db : AsyncSession = Depends(get_db)):
    '''현재 사용자정보를 가져오는 함수, 추후 레디스 블랙리스트로 필터링 기능 추가'''
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰 입니다.")
    
    user = await get_user_by_id(db, payload.get('sub'))
    
    if not user: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "사용자를 찾을 수 없습니다.")
    
    return user
