from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User, Base
from schemas import UserCreate, UserLogin, UserResponse,UserUpdate,UserOut
from passlib.context import CryptContext
import jwt
import os
from database import get_db
from typing import List

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get("SECRET_KEY", "secret")  # JWT secret

# Async register
@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user.email))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = pwd_context.hash(user.password)
    db_user = User(email=user.email, password=hashed, role=user.role)
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    token = jwt.encode({"email": db_user.email, "role": db_user.role}, SECRET_KEY, algorithm="HS256")
    return {"email": db_user.email, "role": db_user.role, "token": token}


# Async login
@router.post("/login", response_model=UserResponse)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalars().first()
    
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    token = jwt.encode({"email": db_user.email, "role": db_user.role}, SECRET_KEY, algorithm="HS256")
    return {"email": db_user.email, "role": db_user.role, "token": token}

@router.get("/", response_model=List[UserOut])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users

# Update a user by ID
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# Delete a user by ID
@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return {"success": True, "message": f"User {user.email} deleted"}
