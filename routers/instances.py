from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from database import get_db
from auth import get_current_active_user
from services.instance_service import InstanceService
import schemas
import models

router = APIRouter(prefix="/api/instances", tags=["WhatsApp Instances"])

@router.post("/", response_model=schemas.WhatsAppInstanceResponse)
async def create_instance(
    instance_data: schemas.WhatsAppInstanceCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new WhatsApp instance"""
    try:
        instance = await InstanceService.create_instance(db, current_user.id, instance_data)
        return instance
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create instance: {str(e)}"
        )

@router.get("/", response_model=List[schemas.WhatsAppInstanceResponse])
async def get_instances(
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all instances for current user"""
    return await InstanceService.get_user_instances(db, current_user.id)

@router.get("/{instance_id}", response_model=schemas.WhatsAppInstanceResponse)
async def get_instance(
    instance_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific instance"""
    instance = await InstanceService.get_instance_by_id(db, instance_id, current_user.id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found"
        )
    return instance

@router.put("/{instance_id}", response_model=schemas.WhatsAppInstanceResponse)
async def update_instance(
    instance_id: UUID,
    instance_data: schemas.WhatsAppInstanceUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update instance"""
    instance = await InstanceService.update_instance(db, instance_id, current_user.id, instance_data)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found"
        )
    return instance

@router.delete("/{instance_id}")
async def delete_instance(
    instance_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete instance"""
    success = await InstanceService.delete_instance(db, instance_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found"
        )
    return {"message": "Instance deleted successfully"}

@router.get("/{instance_id}/qr-code", response_model=schemas.QRCodeResponse)
async def get_qr_code(
    instance_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get QR code for instance connection"""
    instance = await InstanceService.get_instance_by_id(db, instance_id, current_user.id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found"
        )
    
    qr_code = await InstanceService.get_qr_code(db, instance_id, current_user.id)
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not available. Instance may already be connected."
        )
    
    return schemas.QRCodeResponse(
        qr_code=qr_code,
        session_id=instance.session_id,
        status=instance.status.value
    )

@router.post("/{instance_id}/sync")
async def sync_instance_status(
    instance_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync instance status with WhatsApp service"""
    instance = await InstanceService.sync_instance_status(db, instance_id, current_user.id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found"
        )
    return {"message": "Status synchronized", "status": instance.status.value}