#!/usr/bin/env python3
"""
Create a new user script
Usage: python scripts/create_user.py <username> <password> <name> [email] [role]
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database import ASYNC_DATABASE_URL
from models import User, UserRole
from auth import get_password_hash
import uuid

async def create_user(username, password, name, email=None, role="user"):
    """Create a new user"""
    
    print(f"🔨 Creating user: {username}")
    
    # Create async engine
    engine = create_async_engine(ASYNC_DATABASE_URL)
    
    # Create session
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if user already exists
            from sqlalchemy import select
            result = await session.execute(
                select(User).filter(User.username == username)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"❌ User '{username}' already exists")
                return False
            
            # Validate role
            user_role = UserRole.USER
            if role.lower() == "admin":
                user_role = UserRole.ADMIN
            elif role.lower() != "user":
                print(f"⚠️  Invalid role '{role}'. Using 'user' instead.")
            
            # Create user
            new_user = User(
                id=uuid.uuid4(),
                name=name,
                username=username,
                email=email,
                password_hash=get_password_hash(password),
                role=user_role,
                is_active=True
            )
            
            session.add(new_user)
            await session.commit()
            
            print(f"✅ User '{username}' created successfully!")
            print(f"   Name: {name}")
            print(f"   Email: {email or 'Not provided'}")
            print(f"   Role: {user_role.value}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            await session.rollback()
            return False
        finally:
            await engine.dispose()

def main():
    if len(sys.argv) < 4:
        print("Usage: python scripts/create_user.py <username> <password> <name> [email] [role]")
        print("Example: python scripts/create_user.py joao 123456 'João Silva' joao@example.com admin")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    name = sys.argv[3]
    email = sys.argv[4] if len(sys.argv) > 4 else None
    role = sys.argv[5] if len(sys.argv) > 5 else "user"
    
    success = asyncio.run(create_user(username, password, name, email, role))
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()