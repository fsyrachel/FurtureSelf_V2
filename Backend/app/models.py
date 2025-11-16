from __future__ import annotations
from typing import List, Optional
from uuid import UUID
import uuid
from datetime import datetime

from sqlalchemy import String, JSON, TEXT, ForeignKey
from sqlalchemy.types import TIMESTAMP, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.core.database import Base
from app.core.security import encrypt_data, decrypt_data

# (P1) 自定义加密类型
class EncryptedText(TypeDecorator):
    """
    一个自定义的 SQLAlchemy 类型，用于在存入数据库时自动加密，
    并在从数据库读出时自动解密。
    """
    impl = TEXT

    def process_bind_param(self, value, dialect):
        """在数据写入数据库前调用"""
        if value is not None:
            return encrypt_data(str(value))
        return value

    def process_result_value(self, value, dialect):
        """在数据从数据库读出后调用"""
        if value is not None:
            return decrypt_data(str(value))
        return value

# Define TIMESTAMPTZ as TIMESTAMP(timezone=True)
TIMESTAMPTZ = TIMESTAMP(timezone=True)


# (v1.3) 表 1: users
class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ONBOARDING")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now(), onupdate=func.now())

    current_profile: Mapped[Optional[CurrentProfile]] = relationship(
        "CurrentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    future_profiles: Mapped[List[FutureProfile]] = relationship(
        "FutureProfile", back_populates="user", cascade="all, delete-orphan"
    )
    letters: Mapped[List[Letter]] = relationship(
        "Letter", back_populates="user", cascade="all, delete-orphan"
    )
    reports: Mapped[List[Report]] = relationship(
        "Report", back_populates="user", cascade="all, delete-orphan"
    )
    vector_memories: Mapped[List[VectorMemory]] = relationship(
        "VectorMemory", back_populates="user", cascade="all, delete-orphan"
    )


# (v1.3) 表 2: current_profiles
class CurrentProfile(Base):
    __tablename__ = "current_profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    demo_data: Mapped[Optional[dict]] = mapped_column(JSON)
    vals_data: Mapped[Optional[dict]] = mapped_column(JSON)
    bfi_data: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship("User", back_populates="current_profile")


# (v1.3) 表 3: future_profiles
class FutureProfile(Base):
    __tablename__ = "future_profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    profile_name: Mapped[str] = mapped_column(String(255), nullable=False)
    future_values: Mapped[Optional[str]] = mapped_column(EncryptedText)
    future_vision: Mapped[Optional[str]] = mapped_column(EncryptedText)
    future_obstacles: Mapped[Optional[str]] = mapped_column(EncryptedText)
    profile_description: Mapped[Optional[str]] = mapped_column(EncryptedText)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship("User", back_populates="future_profiles")
    letter_replies: Mapped[List[LetterReply]] = relationship(
        "LetterReply", back_populates="future_profile", cascade="all, delete-orphan"
    )
    vector_memories: Mapped[List[VectorMemory]] = relationship(
        "VectorMemory", back_populates="future_profile", cascade="all, delete-orphan"
    )
    chat_messages: Mapped[List[ChatMessage]] = relationship(
        "ChatMessage", back_populates="future_profile", cascade="all, delete-orphan"
    )


# (v1.3) 表 4: letters
class Letter(Base):
    __tablename__ = "letters"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(EncryptedText, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship("User", back_populates="letters")
    letter_replies: Mapped[List[LetterReply]] = relationship(
        "LetterReply", back_populates="letter", cascade="all, delete-orphan"
    )


# (v1.3) 表 5: letter_replies
class LetterReply(Base):
    __tablename__ = "letter_replies"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    letter_id: Mapped[UUID] = mapped_column(ForeignKey("letters.id", ondelete="CASCADE"), nullable=False)
    future_profile_id: Mapped[UUID] = mapped_column(ForeignKey("future_profiles.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(EncryptedText, nullable=False)
    chat_status: Mapped[str] = mapped_column(String(50), nullable=False, default="NOT_STARTED")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now(), onupdate=func.now())

    letter: Mapped[Letter] = relationship("Letter", back_populates="letter_replies")
    future_profile: Mapped[FutureProfile] = relationship("FutureProfile", back_populates="letter_replies")


# (v1.3) 表 6: chat_messages
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    future_profile_id: Mapped[UUID] = mapped_column(ForeignKey("future_profiles.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sender: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(EncryptedText, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now(), onupdate=func.now())

    future_profile: Mapped[FutureProfile] = relationship("FutureProfile", back_populates="chat_messages")


# (v1.3) 表 7: reports
class Report(Base):
    __tablename__ = "reports"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(EncryptedText)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="GENERATING")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship("User", back_populates="reports")


# (v1.3) 表 8: vector_memory
class VectorMemory(Base):
    __tablename__ = "vector_memory"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    future_profile_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("future_profiles.id", ondelete="CASCADE"))
    doc_type: Mapped[str] = mapped_column(String(50), nullable=False)
    text_chunk: Mapped[Optional[str]] = mapped_column(EncryptedText)
    embedding: Mapped[Vector] = mapped_column(Vector(1024))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship("User", back_populates="vector_memories")
    future_profile: Mapped[Optional[FutureProfile]] = relationship("FutureProfile", back_populates="vector_memories")
