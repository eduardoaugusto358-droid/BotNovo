from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from uuid import UUID
import models
import schemas
from auth import get_password_hash

class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, user_data: schemas.UserCreate) -> models.User:
        """Create a new user"""
        # Check if username already exists
        result = await db.execute(
            select(models.User).filter(models.User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise ValueError("Username already exists")
        
        # Check if email already exists (if provided)
        if user_data.email:
            result = await db.execute(
                select(models.User).filter(models.User.email == user_data.email)
            )
            if result.scalar_one_or_none():
                raise ValueError("Email already exists")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = models.User(
            name=user_data.name,
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            role=user_data.role
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[models.User]:
        """Get user by ID"""
        result = await db.execute(
            select(models.User).filter(models.User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[models.User]:
        """Get user by username"""
        result = await db.execute(
            select(models.User).filter(models.User.username == username)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_user(
        db: AsyncSession, 
        user_id: UUID, 
        user_data: schemas.UserUpdate
    ) -> Optional[models.User]:
        """Update user"""
        result = await db.execute(
            select(models.User).filter(models.User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Update fields if provided
        if user_data.name is not None:
            user.name = user_data.name
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
        """Delete user"""
        result = await db.execute(
            select(models.User).filter(models.User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        await db.delete(user)
        await db.commit()
        return True
    
    @staticmethod
    async def get_user_with_instances(db: AsyncSession, user_id: UUID) -> Optional[models.User]:
        """Get user with their WhatsApp instances"""
        result = await db.execute(
            select(models.User)
            .options(selectinload(models.User.instances))
            .filter(models.User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_dashboard_stats(db: AsyncSession, user_id: UUID) -> schemas.DashboardStats:
        """Get dashboard statistics for user"""
        # Get total instances
        instances_result = await db.execute(
            select(models.WhatsAppInstance)
            .filter(models.WhatsAppInstance.user_id == user_id)
        )
        instances = instances_result.scalars().all()
        total_instances = len(instances)
        active_instances = len([i for i in instances if i.status == models.InstanceStatus.ACTIVE])
        
        # Get conversations
        conversations_result = await db.execute(
            select(models.Conversation)
            .filter(models.Conversation.user_id == user_id)
        )
        conversations = conversations_result.scalars().all()
        total_conversations = len(conversations)
        unread_messages = sum(c.unread_count for c in conversations)
        
        # Get campaigns
        campaigns_result = await db.execute(
            select(models.Campaign)
            .filter(models.Campaign.user_id == user_id)
        )
        campaigns = campaigns_result.scalars().all()
        total_campaigns = len(campaigns)
        active_campaigns = len([c for c in campaigns if c.status == models.CampaignStatus.ACTIVE])
        
        return schemas.DashboardStats(
            total_instances=total_instances,
            active_instances=active_instances,
            total_conversations=total_conversations,
            unread_messages=unread_messages,
            total_campaigns=total_campaigns,
            active_campaigns=active_campaigns
        )