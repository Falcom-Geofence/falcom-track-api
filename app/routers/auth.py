from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import User
from ..schemas import Token, LoginRequest
from ..auth import verify_password, create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user: User | None = db.query(User).filter_by(employee_id=data.employee_id).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token({"user_id": user.id, "role": user.role.value})
    refresh = create_refresh_token({"user_id": user.id})
    return Token(access_token=access, refresh_token=refresh)
