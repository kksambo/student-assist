from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import StudentResource, TUTSupport, ChatMessage
from schemas import (
    StudentResourceResponse, StudentResourceUpdate, StudentResourceCreate,
    TUTSupportResponse, TUTSupportUpdate, TUTSupportCreate,
    ChatMessageResponse, ChatMessageUpdate, ChatMessageCreate
)

router = APIRouter(prefix="/admin", tags=["Admin Resources"])

# ------------------------------
# StudentResource Routes
# ------------------------------

# Create
@router.post("/resources", response_model=StudentResourceResponse)
async def create_resource(resource: StudentResourceCreate, db: AsyncSession = Depends(get_db)):
    new_resource = StudentResource(**resource.dict())
    db.add(new_resource)
    await db.commit()
    await db.refresh(new_resource)
    return new_resource

# Read
@router.get("/resources", response_model=list[StudentResourceResponse])
async def get_all_resources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StudentResource))
    return result.scalars().all()

# Update
@router.put("/resources/{resource_id}", response_model=StudentResourceResponse)
async def update_resource(resource_id: int, resource_update: StudentResourceUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StudentResource).where(StudentResource.id == resource_id))
    resource = result.scalar_one_or_none()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    for field, value in resource_update.dict(exclude_unset=True).items():
        setattr(resource, field, value)

    db.add(resource)
    await db.commit()
    await db.refresh(resource)
    return resource

# Delete
@router.delete("/resources/{resource_id}", response_model=dict)
async def delete_resource(resource_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StudentResource).where(StudentResource.id == resource_id))
    resource = result.scalar_one_or_none()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    await db.delete(resource)
    await db.commit()
    return {"success": True, "message": f"Resource '{resource.title}' deleted"}


# ------------------------------
# TUTSupport Routes
# ------------------------------

# Create
@router.post("/support", response_model=TUTSupportResponse)
async def create_support(support: TUTSupportCreate, db: AsyncSession = Depends(get_db)):
    new_support = TUTSupport(**support.dict())
    db.add(new_support)
    await db.commit()
    await db.refresh(new_support)
    return new_support

# Read
@router.get("/support", response_model=list[TUTSupportResponse])
async def get_all_support(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TUTSupport))
    return result.scalars().all()

# Update
@router.put("/support/{support_id}", response_model=TUTSupportResponse)
async def update_support(support_id: int, support_update: TUTSupportUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TUTSupport).where(TUTSupport.id == support_id))
    support = result.scalar_one_or_none()
    if not support:
        raise HTTPException(status_code=404, detail="Support entry not found")

    for field, value in support_update.dict(exclude_unset=True).items():
        setattr(support, field, value)

    db.add(support)
    await db.commit()
    await db.refresh(support)
    return support

# Delete
@router.delete("/support/{support_id}", response_model=dict)
async def delete_support(support_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TUTSupport).where(TUTSupport.id == support_id))
    support = result.scalar_one_or_none()
    if not support:
        raise HTTPException(status_code=404, detail="Support entry not found")

    await db.delete(support)
    await db.commit()
    return {"success": True, "message": f"Support entry '{support.type}' deleted"}


# ------------------------------
# ChatMessage Routes
# ------------------------------

# Create
@router.post("/chat-messages", response_model=ChatMessageResponse)
async def create_chat_message(msg: ChatMessageCreate, db: AsyncSession = Depends(get_db)):
    new_msg = ChatMessage(**msg.dict())
    db.add(new_msg)
    await db.commit()
    await db.refresh(new_msg)
    return new_msg

# Read
@router.get("/chat-messages", response_model=list[ChatMessageResponse])
async def get_all_chat_messages(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatMessage))
    return result.scalars().all()

# Update
@router.put("/chat-messages/{msg_id}", response_model=ChatMessageResponse)
async def update_chat_message(msg_id: int, msg_update: ChatMessageUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatMessage).where(ChatMessage.id == msg_id))
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Chat message not found")

    for field, value in msg_update.dict(exclude_unset=True).items():
        setattr(message, field, value)

    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message

# Delete
@router.delete("/chat-messages/{msg_id}", response_model=dict)
async def delete_chat_message(msg_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatMessage).where(ChatMessage.id == msg_id))
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Chat message not found")

    await db.delete(message)
    await db.commit()
    return {"success": True, "message": "Chat message deleted"}
