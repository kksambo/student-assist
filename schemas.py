from pydantic import BaseModel
from datetime import datetime
from typing import List
from typing import Optional

class UserBase(BaseModel):
    email: str
    role: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str]
    password: Optional[str]
    role: Optional[str]

class UserOut(BaseModel):
    email: Optional[str]
    role: Optional[str]

    class Config:
        orm_mode = True

class UserResponse(UserBase):
    token:Optional[str]
   

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: str
    password: str




from pydantic import BaseModel

class StudentResourceCreate(BaseModel):
    title: str
    module_name: str

class StudentResourceResponse(BaseModel):
    id: int
    title: str
    module_name: str
    file_path: str

    class Config:
        orm_mode = True

class ChatInput(BaseModel):
    email: str
    question: str

class ChatResponse(BaseModel):
    success: bool
    answer: str

class ChatMessageSchema(BaseModel):
    id: int
    student_email: str
    message: str
    sender: str
    created_at: datetime

    class Config:
        orm_mode = True

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageSchema]

# ------------------------------
# StudentResource Schemas
# ------------------------------
class StudentResourceBase(BaseModel):
    title: str
    module_name: str
    file_path: str

class StudentResourceCreate(StudentResourceBase):
    pass

class StudentResourceUpdate(BaseModel):
    title: Optional[str]
    module_name: Optional[str]
    file_path: Optional[str]

class StudentResourceResponse(StudentResourceBase):
    id: int

    class Config:
        orm_mode = True

# ------------------------------
# TUTSupport Schemas
# ------------------------------
class TUTSupportBase(BaseModel):
    type: str
    info: str

class TUTSupportCreate(TUTSupportBase):
    pass

class TUTSupportUpdate(BaseModel):
    type: Optional[str]
    info: Optional[str]

class TUTSupportResponse(TUTSupportBase):
    id: int

    class Config:
        orm_mode = True

# ------------------------------
# ChatMessage Schemas
# ------------------------------
class ChatMessageBase(BaseModel):
    student_email: str
    message: str
    sender: str  # "student" or "bot"

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageUpdate(BaseModel):
    message: Optional[str]

class ChatMessageResponse(ChatMessageBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True



class ResourceBase(BaseModel):
    name: str
    campus_name: str
    info: str
    contact: Optional[str] = None
    email: Optional[str] = None

class ResourceCreate(ResourceBase):
    pass

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    campus_name: Optional[str] = None
    info: Optional[str] = None
    contact: Optional[str] = None
    email: Optional[str] = None

class ResourceResponse(ResourceBase):
    id: int

    class Config:
        orm_mode = True
class FinancialAidResourceBase(BaseModel):
    name: str
    description: str
    requirements: Optional[str] = None
    link: Optional[str] = None

class FinancialAidResourceCreate(FinancialAidResourceBase):
    pass

class FinancialAidResourceResponse(FinancialAidResourceBase):
    id: int

    class Config:
        orm_mode = True