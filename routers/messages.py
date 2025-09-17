from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID

from database import get_db
from auth import get_current_active_user
from services.whatsapp_service import whatsapp_service
import schemas
import models

router = APIRouter(prefix="/api/messages", tags=["Messages"])

@router.get("/conversations", response_model=List[schemas.ConversationResponse])
async def get_conversations(
    instance_id: Optional[UUID] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all conversations for current user"""
    query = (
        select(models.Conversation)
        .options(
            selectinload(models.Conversation.contact),
            selectinload(models.Conversation.messages)
        )
        .filter(models.Conversation.user_id == current_user.id)
        .order_by(desc(models.Conversation.last_message_at))
    )
    
    if instance_id:
        query = query.filter(models.Conversation.instance_id == instance_id)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/conversations/{conversation_id}", response_model=schemas.ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific conversation with messages"""
    result = await db.execute(
        select(models.Conversation)
        .options(
            selectinload(models.Conversation.contact),
            selectinload(models.Conversation.messages)
        )
        .filter(
            and_(
                models.Conversation.id == conversation_id,
                models.Conversation.user_id == current_user.id
            )
        )
    )
    
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return conversation

@router.post("/send", response_model=schemas.MessageResponse)
async def send_message(
    message_data: schemas.MessageCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message"""
    # Get conversation
    result = await db.execute(
        select(models.Conversation)
        .filter(
            and_(
                models.Conversation.id == message_data.conversation_id,
                models.Conversation.user_id == current_user.id
            )
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get instance
    result = await db.execute(
        select(models.WhatsAppInstance)
        .filter(models.WhatsAppInstance.id == conversation.instance_id)
    )
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp instance not found"
        )
    
    # Get contact
    result = await db.execute(
        select(models.Contact)
        .filter(models.Contact.id == conversation.contact_id)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    
    try:
        # Send message via WhatsApp
        result = await whatsapp_service.send_message(
            instance.session_id,
            contact.phone,
            message_data.content,
            message_data.message_type
        )
        
        # Create message record
        message = models.Message(
            conversation_id=conversation.id,
            instance_id=instance.id,
            whatsapp_message_id=result.get('messageId') if result else None,
            content=message_data.content,
            message_type=message_data.message_type,
            media_url=message_data.media_url,
            is_from_me=True,
            status=models.MessageStatus.SENT,
            timestamp=func.now()
        )
        
        db.add(message)
        
        # Update conversation
        conversation.last_message_at = func.now()
        
        await db.commit()
        await db.refresh(message)
        
        return message
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )

@router.post("/conversations/{conversation_id}/mark-read")
async def mark_conversation_read(
    conversation_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark conversation as read"""
    result = await db.execute(
        select(models.Conversation)
        .filter(
            and_(
                models.Conversation.id == conversation_id,
                models.Conversation.user_id == current_user.id
            )
        )
    )
    
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation.unread_count = 0
    await db.commit()
    
    return {"message": "Conversation marked as read"}

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete conversation"""
    result = await db.execute(
        select(models.Conversation)
        .filter(
            and_(
                models.Conversation.id == conversation_id,
                models.Conversation.user_id == current_user.id
            )
        )
    )
    
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    await db.delete(conversation)
    await db.commit()
    
    return {"message": "Conversation deleted successfully"}