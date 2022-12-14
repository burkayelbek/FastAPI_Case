from datetime import timedelta, datetime
from typing import Optional
from fastapi import (APIRouter, Depends, HTTPException, Response, status)
from fastapi.security import OAuth2PasswordRequestForm
from jose import (jwt, JWTError)
from src.schemas.user import LoginToken
from sqlalchemy.orm import Session
from src.service.user import verify_password
from src.base.utils import AuthBearerToken
from src.base.settings import settings
from src.service.user import get_user_by_id
from src.base.database import get_db

router = APIRouter()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=59
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm="HS256"
    )
    return encoded_jwt


def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = get_user_by_id(username=username, db=db)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@router.post("/login", response_model=LoginToken)
def login_for_access_token(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db),
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password is wrong!",
        )
    access_token_expires = timedelta(minutes=59)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )
    return {"access_token": access_token, "token_type": "bearer"}


oauth2_scheme = AuthBearerToken(tokenUrl="/login/token")


def get_current_user_from_token(
        token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms="HS256"
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Unauthorized User. Do not have permission")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized User. Do not have permission")
    user = get_user_by_id(username=email, db=db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized User. Do not have permission")
    return user
