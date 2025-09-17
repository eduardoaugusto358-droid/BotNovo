from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, extract
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from database import get_db
from auth import get_current_active_user
import schemas
import models

router = APIRouter(prefix="/api/finances", tags=["Finances"])

@router.post("/", response_model=schemas.FinanceEntryResponse)
async def create_finance_entry(
    entry_data: schemas.FinanceEntryCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new finance entry"""
    entry = models.FinanceEntry(
        user_id=current_user.id,
        description=entry_data.description,
        category=entry_data.category,
        amount=entry_data.amount,
        entry_type=entry_data.entry_type,
        date=entry_data.date
    )
    
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    
    return entry

@router.get("/", response_model=List[schemas.FinanceEntryResponse])
async def get_finance_entries(
    year: Optional[int] = None,
    month: Optional[int] = None,
    entry_type: Optional[str] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get finance entries with optional filters"""
    query = select(models.FinanceEntry).filter(
        models.FinanceEntry.user_id == current_user.id
    )
    
    if year:
        query = query.filter(extract('year', models.FinanceEntry.date) == year)
    
    if month:
        query = query.filter(extract('month', models.FinanceEntry.date) == month)
    
    if entry_type and entry_type in ['income', 'expense']:
        query = query.filter(models.FinanceEntry.entry_type == entry_type)
    
    query = query.order_by(models.FinanceEntry.date.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{entry_id}", response_model=schemas.FinanceEntryResponse)
async def get_finance_entry(
    entry_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific finance entry"""
    result = await db.execute(
        select(models.FinanceEntry)
        .filter(
            and_(
                models.FinanceEntry.id == entry_id,
                models.FinanceEntry.user_id == current_user.id
            )
        )
    )
    
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finance entry not found"
        )
    
    return entry

@router.put("/{entry_id}", response_model=schemas.FinanceEntryResponse)
async def update_finance_entry(
    entry_id: UUID,
    entry_data: schemas.FinanceEntryCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update finance entry"""
    result = await db.execute(
        select(models.FinanceEntry)
        .filter(
            and_(
                models.FinanceEntry.id == entry_id,
                models.FinanceEntry.user_id == current_user.id
            )
        )
    )
    
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finance entry not found"
        )
    
    entry.description = entry_data.description
    entry.category = entry_data.category
    entry.amount = entry_data.amount
    entry.entry_type = entry_data.entry_type
    entry.date = entry_data.date
    
    await db.commit()
    await db.refresh(entry)
    
    return entry

@router.delete("/{entry_id}")
async def delete_finance_entry(
    entry_id: UUID,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete finance entry"""
    result = await db.execute(
        select(models.FinanceEntry)
        .filter(
            and_(
                models.FinanceEntry.id == entry_id,
                models.FinanceEntry.user_id == current_user.id
            )
        )
    )
    
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finance entry not found"
        )
    
    await db.delete(entry)
    await db.commit()
    
    return {"message": "Finance entry deleted successfully"}

@router.get("/summary/monthly")
async def get_monthly_summary(
    year: int,
    month: int,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get monthly financial summary"""
    result = await db.execute(
        select(models.FinanceEntry)
        .filter(
            and_(
                models.FinanceEntry.user_id == current_user.id,
                extract('year', models.FinanceEntry.date) == year,
                extract('month', models.FinanceEntry.date) == month
            )
        )
    )
    
    entries = result.scalars().all()
    
    total_income = sum(e.amount for e in entries if e.entry_type == 'income')
    total_expenses = sum(e.amount for e in entries if e.entry_type == 'expense')
    net_income = total_income - total_expenses
    
    return {
        "year": year,
        "month": month,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_income": net_income,
        "entries_count": len(entries)
    }