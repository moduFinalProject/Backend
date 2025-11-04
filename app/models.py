from sqlalchemy import VARCHAR, Boolean, Column, Date, ForeignKey, Integer, Text,TIMESTAMP
from app.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class User(Base):
    
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True)
    email = Column(VARCHAR(100), unique=True, nullable=False)
    name = Column(VARCHAR(50), nullable=False)
    address = Column(VARCHAR(100), nullable=False)
    phone = Column(VARCHAR(20))
    birth_date = Column(Date, nullable=False)
    provider = Column(VARCHAR(50))
    provider_id = Column(VARCHAR(50))
    user_type = Column(VARCHAR(10))
    is_activate = Column(Boolean, default=True)
    deleted_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default= lambda : datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP, default= lambda : datetime.now(timezone.utc))
    last_accessed = Column(TIMESTAMP)
    gender = Column(VARCHAR(10), nullable=False)
    is_sanctions = Column(Boolean, default=False)






class UserBlacklist(Base):
    
    __tablename__ = "userblacklists"
    
    blacklist_id = Column(Integer, primary_key=True)
    blocked_by = Column(Integer,ForeignKey("users.user_id"), nullable=False)
    updated_by = Column(Integer,ForeignKey("users.user_id"), nullable=False)
    user_id = Column(Integer,ForeignKey("users.user_id"), nullable=False)
    reason = Column(VARCHAR(200))
    blocked_at = Column(TIMESTAMP,default=lambda : datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP,default=lambda : datetime.now(timezone.utc))
    block_period = Column(TIMESTAMP)
    



class UserActivityLog(Base):
    
    __tablename__ = "useractiviylogs"
    
    log_id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.user_id"), nullable=False)
    action_type = Column(VARCHAR(50))
    description = Column(VARCHAR(200))
    ip_address = Column(VARCHAR(100))
    created_at = Column(TIMESTAMP, default= lambda : datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP,default=lambda : datetime.now(timezone.utc))