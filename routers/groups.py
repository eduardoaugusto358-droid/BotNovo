from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from uuid import UUID

from database import get_db
from auth import get_current_active_user
import schemas
import models

router = APIRouter(prefix="/api/groups", tags=["Groups"])

@router.post("/", response_model=schemas.GroupResponse)
async def create_group(
    group_data: schemas.GroupCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new contact group"""
    group = models.Group(
        user_id=current_user.id,
        name=group_data.name,
        description=group_data.description,
        contacts=group_data.contacts
    )
    
    db.add(group)
    await db.commit()
    await db.refresh(group)
    
    return group

@router.get("/", response_model=List[schemas.GroupResponse])
async def get_groups(
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all groups for current user"""
    result = await db.execute(
        select(models.Group)
        .filter(models.Group.user_id == current_user.id)
        .order_by(models.Group.created_at.desc())
    )
    return result.scalars().all()

@router.get("/{group_id}", response_model=schemas.GroupResponse)
async def get_group(
    group_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific group"""
    result = await db.execute(
        select(models.Group)
        .filter(
            and_(
                models.Group.id == group_id,
                models.Group.user_id == current_user.id
            )
        )
    )
    
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    return group

@router.put("/{group_id}", response_model=schemas.GroupResponse)
async def update_group(
    group_id: UUID,
    group_data: schemas.GroupUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update group"""
    result = await db.execute(
        select(models.Group)
        .filter(
            and_(
                models.Group.id == group_id,
                models.Group.user_id == current_user.id
            )
        )
    )
    
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Update fields if provided
    if group_data.name is not None:
        group.name = group_data.name
    if group_data.description is not None:
        group.description = group_data.description
    if group_data.contacts is not None:
        group.contacts = group_data.contacts
    
    await db.commit()
    await db.refresh(group)
    
    return group

@router.delete("/{group_id}")
async def delete_group(
    group_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete group"""
    result = await db.execute(
        select(models.Group)
        .filter(
            and_(
                models.Group.id == group_id,
                models.Group.user_id == current_user.id
            )
        )
    )
    
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    await db.delete(group)
    await db.commit()
    
    return {"message": "Group deleted successfully"}