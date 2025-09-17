from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from datetime import datetime
import logging

from database import get_db
from services.instance_service import InstanceService
import models

router = APIRouter(prefix="/api/webhook", tags=["Webhooks"])
logger = logging.getLogger(__name__)

@router.post("/whatsapp/{instance_id}")
async def whatsapp_webhook(
    instance_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle WhatsApp webhooks from Baileys service"""
    try:
        data = await request.json()
        webhook_type = data.get('type')
        session_id = data.get('sessionId')
        
        logger.info(f"Received webhook: {webhook_type} for instance {instance_id}")
        
        # Get instance
        result = await db.execute(
            select(models.WhatsAppInstance)
            .filter(models.WhatsAppInstance.id == instance_id)
        )
        instance = result.scalar_one_or_none()
        
        if not instance:
            logger.error(f"Instance {instance_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instance not found"
            )
        
        if webhook_type == 'qr_code':
            # Update QR code
            qr_code = data.get('qrCode')
            if qr_code:
                instance.qr_code = qr_code
                instance.status = models.InstanceStatus.PENDING
                await db.commit()
                logger.info(f"Updated QR code for instance {instance_id}")
        
        elif webhook_type == 'connected':
            # Update connection status
            phone = data.get('phone')
            instance.status = models.InstanceStatus.ACTIVE
            instance.last_seen = func.now()
            instance.qr_code = None  # Clear QR code
            
            if phone:
                instance.phone = phone
            
            await db.commit()
            logger.info(f"Instance {instance_id} connected with phone {phone}")
        
        elif webhook_type == 'message':
            # Handle incoming message
            message_data = data.get('message', {})
            
            # Find or create contact
            phone = message_data.get('from', '').replace('@s.whatsapp.net', '')
            if not phone:
                logger.warning("No phone number in message webhook")
                return {"status": "ignored"}
            
            # Find existing contact
            result = await db.execute(
                select(models.Contact)
                .filter(models.Contact.phone == phone)
            )
            contact = result.scalar_one_or_none()
            
            if not contact:
                # Create new contact
                contact = models.Contact(
                    phone=phone,
                    name=phone  # Default name is phone number
                )
                db.add(contact)
                await db.flush()  # Get contact ID
            
            # Find or create conversation
            result = await db.execute(
                select(models.Conversation)
                .filter(
                    models.Conversation.instance_id == instance_id,
                    models.Conversation.contact_id == contact.id
                )
            )
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                # Create new conversation
                conversation = models.Conversation(
                    user_id=instance.user_id,
                    instance_id=instance_id,
                    contact_id=contact.id,
                    is_group=False
                )
                db.add(conversation)
                await db.flush()  # Get conversation ID
            
            # Create message
            message = models.Message(
                conversation_id=conversation.id,
                instance_id=instance_id,
                whatsapp_message_id=message_data.get('id'),
                content=message_data.get('content', ''),
                message_type=message_data.get('messageType', 'text'),
                is_from_me=False,
                status=models.MessageStatus.DELIVERED,
                timestamp=datetime.fromtimestamp(message_data.get('timestamp', 0))
            )
            db.add(message)
            
            # Update conversation
            conversation.unread_count += 1
            conversation.last_message_at = func.now()
            
            await db.commit()
            logger.info(f"Processed incoming message for instance {instance_id}")
        
        elif webhook_type == 'disconnected':
            # Handle disconnection
            instance.status = models.InstanceStatus.OFFLINE
            instance.last_seen = func.now()
            await db.commit()
            logger.info(f"Instance {instance_id} disconnected")
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process webhook"
        )