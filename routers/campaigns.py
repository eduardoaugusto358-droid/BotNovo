from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from uuid import UUID

from database import get_db
from auth import get_current_active_user
import schemas
import models

router = APIRouter(prefix="/api/campaigns", tags=["Campaigns"])

@router.post("/", response_model=schemas.CampaignResponse)
async def create_campaign(
    campaign_data: schemas.CampaignCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new campaign"""
    # Verify instance belongs to user
    result = await db.execute(
        select(models.WhatsAppInstance)
        .filter(
            and_(
                models.WhatsAppInstance.id == campaign_data.instance_id,
                models.WhatsAppInstance.user_id == current_user.id
            )
        )
    )
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp instance not found"
        )
    
    campaign = models.Campaign(
        user_id=current_user.id,
        instance_id=campaign_data.instance_id,
        name=campaign_data.name,
        description=campaign_data.description,
        message_template=campaign_data.message_template,
        target_contacts=campaign_data.target_contacts,
        scheduled_at=campaign_data.scheduled_at,
        status=models.CampaignStatus.DRAFT
    )
    
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    
    return campaign

@router.get("/", response_model=List[schemas.CampaignResponse])
async def get_campaigns(
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all campaigns for current user"""
    result = await db.execute(
        select(models.Campaign)
        .filter(models.Campaign.user_id == current_user.id)
        .order_by(models.Campaign.created_at.desc())
    )
    return result.scalars().all()

@router.get("/{campaign_id}", response_model=schemas.CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific campaign"""
    result = await db.execute(
        select(models.Campaign)
        .filter(
            and_(
                models.Campaign.id == campaign_id,
                models.Campaign.user_id == current_user.id
            )
        )
    )
    
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return campaign

@router.put("/{campaign_id}", response_model=schemas.CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    campaign_data: schemas.CampaignUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update campaign"""
    result = await db.execute(
        select(models.Campaign)
        .filter(
            and_(
                models.Campaign.id == campaign_id,
                models.Campaign.user_id == current_user.id
            )
        )
    )
    
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Update fields if provided
    if campaign_data.name is not None:
        campaign.name = campaign_data.name
    if campaign_data.description is not None:
        campaign.description = campaign_data.description
    if campaign_data.message_template is not None:
        campaign.message_template = campaign_data.message_template
    if campaign_data.target_contacts is not None:
        campaign.target_contacts = campaign_data.target_contacts
    if campaign_data.scheduled_at is not None:
        campaign.scheduled_at = campaign_data.scheduled_at
    
    await db.commit()
    await db.refresh(campaign)
    
    return campaign

@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete campaign"""
    result = await db.execute(
        select(models.Campaign)
        .filter(
            and_(
                models.Campaign.id == campaign_id,
                models.Campaign.user_id == current_user.id
            )
        )
    )
    
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    await db.delete(campaign)
    await db.commit()
    
    return {"message": "Campaign deleted successfully"}

@router.post("/{campaign_id}/start")
async def start_campaign(
    campaign_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Start/activate a campaign"""
    result = await db.execute(
        select(models.Campaign)
        .filter(
            and_(
                models.Campaign.id == campaign_id,
                models.Campaign.user_id == current_user.id
            )
        )
    )
    
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    if campaign.status == models.CampaignStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign is already active"
        )
    
    campaign.status = models.CampaignStatus.ACTIVE
    await db.commit()
    
    # TODO: Implement campaign execution logic
    # This would typically involve a background task or celery job
    
    return {"message": "Campaign started successfully"}

@router.post("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Pause a campaign"""
    result = await db.execute(
        select(models.Campaign)
        .filter(
            and_(
                models.Campaign.id == campaign_id,
                models.Campaign.user_id == current_user.id
            )
        )
    )
    
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    campaign.status = models.CampaignStatus.PAUSED
    await db.commit()
    
    return {"message": "Campaign paused successfully"}