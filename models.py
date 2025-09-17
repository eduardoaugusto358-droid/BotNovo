from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class InstanceStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    OFFLINE = "offline"
    ERROR = "error"

class MessageStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"

class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    instances = relationship("WhatsAppInstance", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")
    finances = relationship("FinanceEntry", back_populates="user", cascade="all, delete-orphan")

class WhatsAppInstance(Base):
    __tablename__ = "whatsapp_instances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    session_id = Column(String(100), unique=True, nullable=False)
    status = Column(Enum(InstanceStatus), default=InstanceStatus.PENDING)
    qr_code = Column(Text, nullable=True)
    webhook_url = Column(String(500), nullable=True)
    settings = Column(JSON, default=dict)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="instances")
    conversations = relationship("Conversation", back_populates="instance", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="instance", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="instance", cascade="all, delete-orphan")

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), nullable=False)
    name = Column(String(100), nullable=True)
    profile_picture = Column(String(500), nullable=True)
    is_business = Column(Boolean, default=False)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conversations = relationship("Conversation", back_populates="contact")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("whatsapp_instances.id"), nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=False)
    is_group = Column(Boolean, default=False)
    group_name = Column(String(100), nullable=True)
    unread_count = Column(Integer, default=0)
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    archived = Column(Boolean, default=False)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    instance = relationship("WhatsAppInstance", back_populates="conversations")
    contact = relationship("Contact", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("whatsapp_instances.id"), nullable=False)
    whatsapp_message_id = Column(String(100), nullable=True)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")  # text, image, document, audio, video
    media_url = Column(String(500), nullable=True)
    is_from_me = Column(Boolean, nullable=False)
    status = Column(Enum(MessageStatus), default=MessageStatus.PENDING)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    instance = relationship("WhatsAppInstance", back_populates="messages")

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("whatsapp_instances.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    message_template = Column(Text, nullable=False)
    target_contacts = Column(JSON, default=list)  # List of phone numbers
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="campaigns")
    instance = relationship("WhatsAppInstance", back_populates="campaigns")

class FinanceEntry(Base):
    __tablename__ = "finance_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    description = Column(String(200), nullable=False)
    category = Column(String(50), nullable=True)
    amount = Column(Float, nullable=False)
    entry_type = Column(String(20), nullable=False)  # income, expense
    date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="finances")

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    contacts = Column(JSON, default=list)  # List of contact IDs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="groups")

# Add groups relationship to User
User.groups = relationship("Group", back_populates="user", cascade="all, delete-orphan")