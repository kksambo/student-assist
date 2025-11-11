from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from typing import List
from database import get_db as get_async_db  # make sure this returns AsyncSession
from models import FinancialAidResource
from schemas import FinancialAidResourceCreate, FinancialAidResourceResponse

router = APIRouter(prefix="/financial-aid", tags=["Financial Aid"])

# Create a new financial aid resource
@router.post("/", response_model=FinancialAidResourceResponse)
async def create_financial_aid_resource(
    resource: FinancialAidResourceCreate, db: AsyncSession = Depends(get_async_db)
):
    db_resource = FinancialAidResource(**resource.dict())
    db.add(db_resource)
    await db.commit()
    await db.refresh(db_resource)
    return db_resource

# Get all financial aid resources
@router.get("/", response_model=List[FinancialAidResourceResponse])
async def get_financial_aid_resources(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(FinancialAidResource))
    resources = result.scalars().all()
    return resources

# Get a single resource by ID
@router.get("/{resource_id}", response_model=FinancialAidResourceResponse)
async def get_financial_aid_resource(resource_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(FinancialAidResource).where(FinancialAidResource.id == resource_id))
    resource = result.scalars().first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

# Update a resource
@router.put("/{resource_id}", response_model=FinancialAidResourceResponse)
async def update_financial_aid_resource(
    resource_id: int,
    updated: FinancialAidResourceCreate,
    db: AsyncSession = Depends(get_async_db),
):
    result = await db.execute(select(FinancialAidResource).where(FinancialAidResource.id == resource_id))
    resource = result.scalars().first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    for key, value in updated.dict().items():
        setattr(resource, key, value)

    db.add(resource)
    await db.commit()
    await db.refresh(resource)
    return resource

# Delete a resource
@router.delete("/{resource_id}")
async def delete_financial_aid_resource(resource_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(FinancialAidResource).where(FinancialAidResource.id == resource_id))
    resource = result.scalars().first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    await db.delete(resource)
    await db.commit()
    return {"detail": "Resource deleted successfully"}
