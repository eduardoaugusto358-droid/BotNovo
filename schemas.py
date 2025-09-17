from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from models import UserRole, InstanceStatus, MessageStatus, CampaignStatus

# User Schemas
class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.USER

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# WhatsApp Instance Schemas
class WhatsAppInstanceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    webhook_url: Optional[str] = None
    settings: Optional[Dict[str, Any]] = {}

class WhatsAppInstanceCreate(WhatsAppInstanceBase):
    pass

class WhatsAppInstanceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    webhook_url: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class WhatsAppInstanceResponse(WhatsAppInstanceBase):
    id: UUID
    user_id: UUID
    session_id: str
    status: InstanceStatus
    qr_code: Optional[str] = None
    last_seen: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Contact Schemas
class ContactBase(BaseModel):
    phone: str = Field(..., max_length=20)
    name: Optional[str] = Field(None, max_length=100)
    is_business: bool = False
    metadata: Optional[Dict[str, Any]] = {}

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: UUID
    profile_picture: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Message Schemas
class MessageBase(BaseModel):
    content: str
    message_type: str = "text"
    media_url: Optional[str] = None

class MessageCreate(MessageBase):
    conversation_id: UUID
    is_from_me: bool = True

class MessageResponse(MessageBase):
    id: UUID
    conversation_id: UUID
    instance_id: UUID
    whatsapp_message_id: Optional[str] = None
    is_from_me: bool
    status: MessageStatus
    timestamp: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

# Conversation Schemas
class ConversationBase(BaseModel):
    is_group: bool = False
    group_name: Optional[str] = None

class ConversationCreate(ConversationBase):
    contact_id: UUID
    instance_id: UUID

class ConversationResponse(ConversationBase):
    id: UUID
    user_id: UUID
    instance_id: UUID
    contact_id: UUID
    unread_count: int
    last_message_at: Optional[datetime] = None
    archived: bool
    created_at: datetime
    
    # Nested data
    contact: ContactResponse
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True

# Campaign Schemas
class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    message_template: str = Field(..., min_length=1)
    target_contacts: List[str] = []

class CampaignCreate(CampaignBase):
    instance_id: UUID
    scheduled_at: Optional[datetime] = None

class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    message_template: Optional[str] = Field(None, min_length=1)
    target_contacts: Optional[List[str]] = None
    scheduled_at: Optional[datetime] = None

class CampaignResponse(CampaignBase):
    id: UUID
    user_id: UUID
    instance_id: UUID
    status: CampaignStatus
    scheduled_at: Optional[datetime] = None
    sent_count: int
    delivered_count: int
    failed_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Finance Schemas
class FinanceEntryBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    amount: float
    entry_type: str = Field(..., regex="^(income|expense)$")
    date: datetime

class FinanceEntryCreate(FinanceEntryBase):
    pass

class FinanceEntryResponse(FinanceEntryBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# Group Schemas
class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    contacts: List[UUID] = []

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    contacts: Optional[List[UUID]] = None

class GroupResponse(GroupBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_instances: int
    active_instances: int
    total_conversations: int
    unread_messages: int
    total_campaigns: int
    active_campaigns: int

# QR Code Response
class QRCodeResponse(BaseModel):
    qr_code: str
    session_id: str
    status: str