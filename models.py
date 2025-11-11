from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)  # "admin" or "student"



class StudentResource(Base):
    __tablename__ = "student_resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    module_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

class TUTSupport(Base):
    __tablename__ = "tut_support"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)      # e.g., "phone", "email", "center", "web_link"
    info = Column(Text, nullable=False)

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    student_email = Column(String, nullable=False, index=True)
    message = Column(Text, nullable=False)
    sender = Column(String, nullable=False)    # "student" or "bot"
    created_at = Column(DateTime, default=datetime.utcnow)


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    campus_name = Column(String(100), nullable=False)
    info = Column(String(255), nullable=False)
    contact = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)

class FinancialAidResource(Base):
    __tablename__ = "financial_aid_resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    requirements = Column(String(1000), nullable=True)
    link = Column(String(500), nullable=True)