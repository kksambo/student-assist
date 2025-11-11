from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import StudentResource
from schemas import StudentResourceCreate, StudentResourceResponse
import shutil
import os

router = APIRouter(prefix="/student-resources", tags=["Student Resources"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=StudentResourceResponse)
async def upload_resource(
    title: str = Form(...),
    module_name: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    # Save file to disk
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Save metadata to DB
    resource = StudentResource(title=title, module_name=module_name, file_path=file_location)
    db.add(resource)
    await db.commit()
    await db.refresh(resource)
    return resource

from fastapi.responses import FileResponse

@router.get("/resources/module/{module_name}")
async def get_resources(module_name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StudentResource).where(StudentResource.module_name == module_name))
    resources = result.scalars().all()

    # Return URLs or endpoints to download
    return [
        {"id": r.id, "title": r.title, "download_url": f"/resources/download/{r.id}"}
        for r in resources
    ]

@router.get("/module/{module_name}", response_model=list[StudentResourceResponse])
async def get_resources_by_module(module_name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StudentResource).where(StudentResource.module_name == module_name))
    resources = result.scalars().all()
    if not resources:
        raise HTTPException(status_code=404, detail="No resources found for this module")
    return resources

@router.get("/resources/download/{resource_id}")
async def download_resource(resource_id: int, db: AsyncSession = Depends(get_db)):
    resource = await db.get(StudentResource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return FileResponse(path=resource.file_path, filename=resource.title + ".pdf", media_type="application/pdf")
