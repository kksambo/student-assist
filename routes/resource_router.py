from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, delete, update
from database import get_db as get_session
from models import Resource
from schemas import ResourceCreate, ResourceResponse, ResourceUpdate

router = APIRouter(prefix="/resources", tags=["Resources"])

# 🟢 Create a Resource
@router.post("/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(resource: ResourceCreate, session: AsyncSession = Depends(get_session)):
    stmt = insert(Resource).values(**resource.dict()).returning(Resource)
    result = await session.execute(stmt)
    await session.commit()
    new_resource = result.scalar_one()
    return new_resource

# 🔵 Get All Resources
@router.get("/", response_model=list[ResourceResponse])
async def get_resources(session: AsyncSession = Depends(get_session)):
    stmt = select(Resource)
    result = await session.execute(stmt)
    resources = result.scalars().all()
    return resources

# 🟣 Get Resource by ID
@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(resource_id: int, session: AsyncSession = Depends(get_session)):
    stmt = select(Resource).where(Resource.id == resource_id)
    result = await session.execute(stmt)
    resource = result.scalar_one_or_none()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

# 🔴 Delete Resource by ID
@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(resource_id: int, session: AsyncSession = Depends(get_session)):
    stmt_select = select(Resource).where(Resource.id == resource_id)
    result = await session.execute(stmt_select)
    resource = result.scalar_one_or_none()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    stmt_delete = delete(Resource).where(Resource.id == resource_id)
    await session.execute(stmt_delete)
    await session.commit()
    return {"message": "Resource deleted successfully"}

# 🟠 Flexible Search (by name and/or campus_name)
@router.get("/search/", response_model=list[ResourceResponse])
async def search_resources(
    name: str | None = None,
    campus_name: str | None = None,
    session: AsyncSession = Depends(get_session)
):
    if not name and not campus_name:
        raise HTTPException(status_code=400, detail="Provide at least a name or campus_name to search")
    
    stmt = select(Resource)
    if name:
        stmt = stmt.where(Resource.name.ilike(f"%{name}%"))
    if campus_name:
        stmt = stmt.where(Resource.campus_name.ilike(f"%{campus_name}%"))

    result = await session.execute(stmt)
    resources = result.scalars().all()
    if not resources:
        raise HTTPException(status_code=404, detail="No resources found")
    return resources

# 🟡 Update Resource by ID
@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int,
    resource_update: ResourceUpdate,
    session: AsyncSession = Depends(get_session)
):
    stmt_select = select(Resource).where(Resource.id == resource_id)
    result = await session.execute(stmt_select)
    resource = result.scalar_one_or_none()

    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Prepare update values, ignore None
    update_data = {k: v for k, v in resource_update.dict().items() if v is not None}

    if update_data:
        stmt_update = update(Resource).where(Resource.id == resource_id).values(**update_data).returning(Resource)
        result = await session.execute(stmt_update)
        await session.commit()
        updated_resource = result.scalar_one()
        return updated_resource
    return resource
