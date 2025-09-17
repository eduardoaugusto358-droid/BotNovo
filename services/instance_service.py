from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from uuid import UUID, uuid4
import models
import schemas
from services.whatsapp_service import whatsapp_service
from config import settings

class InstanceService:
    @staticmethod
    async def create_instance(
        db: AsyncSession, 
        user_id: UUID, 
        instance_data: schemas.WhatsAppInstanceCreate
    ) -> models.WhatsAppInstance:
        """Create a new WhatsApp instance"""
        
        # Generate unique session ID
        session_id = f"session_{user_id}_{uuid4().hex[:8]}"
        
        # Create database record
        db_instance = models.WhatsAppInstance(
            user_id=user_id,
            name=instance_data.name,
            phone=instance_data.phone,
            session_id=session_id,
            webhook_url=instance_data.webhook_url,
            settings=instance_data.settings or {},
            status=models.InstanceStatus.PENDING
        )
        
        db.add(db_instance)
        await db.commit()
        await db.refresh(db_instance)
        
        # Create WhatsApp session
        try:
            webhook_url = f"{settings.frontend_url}/api/webhook/whatsapp/{db_instance.id}"
            await whatsapp_service.create_session(session_id, webhook_url)
        except Exception as e:
            # If session creation fails, update status to error
            db_instance.status = models.InstanceStatus.ERROR
            await db.commit()
            raise e
        
        return db_instance
    
    @staticmethod
    async def get_instance_by_id(
        db: AsyncSession, 
        instance_id: UUID,
        user_id: Optional[UUID] = None
    ) -> Optional[models.WhatsAppInstance]:
        """Get instance by ID"""
        query = select(models.WhatsAppInstance).filter(
            models.WhatsAppInstance.id == instance_id
        )
        
        if user_id:
            query = query.filter(models.WhatsAppInstance.user_id == user_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_instances(
        db: AsyncSession, 
        user_id: UUID
    ) -> List[models.WhatsAppInstance]:
        """Get all instances for a user"""
        result = await db.execute(
            select(models.WhatsAppInstance)
            .filter(models.WhatsAppInstance.user_id == user_id)
            .order_by(models.WhatsAppInstance.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def update_instance(
        db: AsyncSession,
        instance_id: UUID,
        user_id: UUID,
        instance_data: schemas.WhatsAppInstanceUpdate
    ) -> Optional[models.WhatsAppInstance]:
        """Update instance"""
        instance = await InstanceService.get_instance_by_id(db, instance_id, user_id)
        
        if not instance:
            return None
        
        # Update fields if provided
        if instance_data.name is not None:
            instance.name = instance_data.name
        if instance_data.phone is not None:
            instance.phone = instance_data.phone
        if instance_data.webhook_url is not None:
            instance.webhook_url = instance_data.webhook_url
        if instance_data.settings is not None:
            instance.settings = instance_data.settings
        
        await db.commit()
        await db.refresh(instance)
        return instance
    
    @staticmethod
    async def delete_instance(
        db: AsyncSession,
        instance_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete instance"""
        instance = await InstanceService.get_instance_by_id(db, instance_id, user_id)
        
        if not instance:
            return False
        
        # Delete WhatsApp session
        try:
            await whatsapp_service.delete_session(instance.session_id)
        except Exception:
            pass  # Continue even if session deletion fails
        
        # Delete from database
        await db.delete(instance)
        await db.commit()
        return True
    
    @staticmethod
    async def get_qr_code(
        db: AsyncSession,
        instance_id: UUID,
        user_id: UUID
    ) -> Optional[str]:
        """Get QR code for instance"""
        instance = await InstanceService.get_instance_by_id(db, instance_id, user_id)
        
        if not instance:
            return None
        
        # Get QR code from Baileys service
        qr_code = await whatsapp_service.get_qr_code(instance.session_id)
        
        if qr_code:
            # Update instance with QR code
            instance.qr_code = qr_code
            await db.commit()
        
        return qr_code
    
    @staticmethod
    async def update_instance_status(
        db: AsyncSession,
        instance_id: UUID,
        status: models.InstanceStatus,
        phone: Optional[str] = None
    ) -> bool:
        """Update instance status (called by webhook)"""
        result = await db.execute(
            select(models.WhatsAppInstance).filter(
                models.WhatsAppInstance.id == instance_id
            )
        )
        instance = result.scalar_one_or_none()
        
        if not instance:
            return False
        
        instance.status = status
        if phone:
            instance.phone = phone
        if status == models.InstanceStatus.ACTIVE:
            instance.last_seen = func.now()
        
        await db.commit()
        return True
    
    @staticmethod
    async def sync_instance_status(
        db: AsyncSession,
        instance_id: UUID,
        user_id: UUID
    ) -> Optional[models.WhatsAppInstance]:
        """Sync instance status with Baileys service"""
        instance = await InstanceService.get_instance_by_id(db, instance_id, user_id)
        
        if not instance:
            return None
        
        # Get status from Baileys service
        status_data = await whatsapp_service.get_session_status(instance.session_id)
        
        if status_data:
            # Map Baileys status to our status
            baileys_status = status_data.get('status', 'disconnected')
            if baileys_status == 'connected':
                instance.status = models.InstanceStatus.ACTIVE
            elif baileys_status == 'connecting':
                instance.status = models.InstanceStatus.PENDING
            else:
                instance.status = models.InstanceStatus.OFFLINE
            
            # Update phone if available
            if status_data.get('phone'):
                instance.phone = status_data['phone']
            
            # Update last seen
            if baileys_status == 'connected':
                instance.last_seen = func.now()
            
            await db.commit()
            await db.refresh(instance)
        
        return instance