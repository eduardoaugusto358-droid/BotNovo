#!/usr/bin/env python3
"""
Database initialization script
Creates tables and initial admin user
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database import Base, ASYNC_DATABASE_URL
from models import User, UserRole
from auth import get_password_hash
from config import settings
import uuid

async def init_database():
    """Initialize database with tables and admin user"""
    
    print("🚀 Initializing database...")
    
    # Create async engine
    engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
    
    # Create all tables
    async with engine.begin() as conn:
        print("📝 Creating database tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully!")
    
    # Create session
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Create admin user
    async with AsyncSessionLocal() as session:
        try:
            # Check if admin user already exists
            from sqlalchemy import select
            result = await session.execute(
                select(User).filter(User.username == "admin")
            )
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                print("⚠️  Admin user already exists")
            else:
                print("👤 Creating admin user...")
                
                admin_user = User(
                    id=uuid.uuid4(),
                    name="Administrator",
                    username="admin",
                    email="admin@whatsappbot.com",
                    password_hash=get_password_hash("admin123"),
                    role=UserRole.ADMIN,
                    is_active=True
                )
                
                session.add(admin_user)
                await session.commit()
                
                print("✅ Admin user created successfully!")
                print("   Username: admin")
                print("   Password: admin123")
                print("   ⚠️  Please change the default password after first login!")
                
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            await session.rollback()
            raise
    
    await engine.dispose()
    print("🎉 Database initialization completed!")

if __name__ == "__main__":
    asyncio.run(init_database())