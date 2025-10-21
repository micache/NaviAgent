"""SQLAlchemy models định nghĩa cấu trúc bảng database.

Chỉ dùng để khai báo schema và lấy tên bảng/cột, không dùng ORM session.
"""

from __future__ import annotations

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """Bảng users - Thông tin profile người dùng."""

    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=False), primary_key=True)
    created_at = Column(DateTime(timezone=True))
    full_name = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    average_budget = Column(Integer, nullable=True)


class Trip(Base):
    """Bảng trips - Chuyến đi của người dùng."""

    __tablename__ = "trips"

    id = Column(UUID(as_uuid=False), primary_key=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.user_id"), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    address = Column(Text, nullable=True)
    status = Column(String, nullable=True)


class ChatSession(Base):
    """Bảng chat_sessions - Phiên chat giữa user và agent."""

    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=False), primary_key=True)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.user_id"), nullable=False)
    title = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True))
    update_at = Column(DateTime(timezone=True))


class ChatMessage(Base):
    """Bảng chat_messages - Tin nhắn trong phiên chat."""

    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=False), primary_key=True)
    session_id = Column(UUID(as_uuid=False), ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True))
