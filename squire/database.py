"""
Database models and configuration for SquigLeague

SQLAlchemy models for PostgreSQL persistence
"""

from datetime import datetime, timedelta
from typing import Optional
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


# ═══════════════════════════════════════════════
# USER MODELS
# ═══════════════════════════════════════════════


class User(Base):
    """User account with email verification"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Profile fields
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    verification_tokens = relationship("EmailVerificationToken", back_populates="user", cascade="all, delete-orphan")
    created_matchups = relationship("Matchup", foreign_keys="Matchup.player1_user_id", back_populates="player1_user")
    joined_matchups = relationship("Matchup", foreign_keys="Matchup.player2_user_id", back_populates="player2_user")
    location_verifications = relationship("LocationVerification", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email_verified={self.email_verified})>"


class EmailVerificationToken(Base):
    """Email verification tokens with expiry"""
    
    __tablename__ = "email_verification_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="verification_tokens")
    
    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f"<EmailVerificationToken(user_id={self.user_id}, expires_at={self.expires_at})>"


# ═══════════════════════════════════════════════
# FACTION MODELS
# ═══════════════════════════════════════════════


class Faction(Base):
    """Game system factions"""
    
    __tablename__ = "factions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_system = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    abbreviation = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Faction(game_system='{self.game_system}', name='{self.name}')>"


# ═══════════════════════════════════════════════
# MATCHUP MODELS
# ═══════════════════════════════════════════════


class Matchup(Base):
    """Matchup with lifecycle tracking"""
    
    __tablename__ = "matchups"
    
    id = Column(String(50), primary_key=True)
    game_system = Column(String(50), nullable=False)
    status = Column(String(50), default="created", nullable=False, index=True)
    
    # Players
    player1_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    player1_name = Column(String(100), nullable=False)
    player1_army_list = Column(Text, nullable=True)
    player1_faction_id = Column(UUID(as_uuid=True), ForeignKey("factions.id"), nullable=True)
    
    player2_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    player2_name = Column(String(100), nullable=True)
    player2_army_list = Column(Text, nullable=True)
    player2_faction_id = Column(UUID(as_uuid=True), ForeignKey("factions.id"), nullable=True)
    
    # Battle plan (stored as JSON)
    battle_plan_json = Column(Text, nullable=True)
    
    # Lifecycle timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    battle_started_at = Column(DateTime, nullable=True)
    battle_ended_at = Column(DateTime, nullable=True)
    
    # Optional scheduling
    scheduled_time = Column(DateTime, nullable=True)
    location_name = Column(String(200), nullable=True)
    
    # Results
    winner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    player1_vp = Column(Integer, nullable=True)
    player2_vp = Column(Integer, nullable=True)
    result_notes = Column(Text, nullable=True)
    result_verified_at = Column(DateTime, nullable=True)
    
    # Dispute handling
    disputed_at = Column(DateTime, nullable=True)
    dispute_reason = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    resolved_by_admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    location_manually_verified = Column(Boolean, default=False)
    
    # Relationships
    player1_user = relationship("User", foreign_keys=[player1_user_id], back_populates="created_matchups")
    player2_user = relationship("User", foreign_keys=[player2_user_id], back_populates="joined_matchups")
    player1_faction = relationship("Faction", foreign_keys=[player1_faction_id])
    player2_faction = relationship("Faction", foreign_keys=[player2_faction_id])
    location_verifications = relationship("LocationVerification", back_populates="matchup", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Matchup(id='{self.id}', status='{self.status}', system='{self.game_system}')>"


# ═══════════════════════════════════════════════
# LOCATION VERIFICATION MODELS
# ═══════════════════════════════════════════════


class LocationVerification(Base):
    """Geolocation verification records"""
    
    __tablename__ = "matchup_locations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matchup_id = Column(String(50), ForeignKey("matchups.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)  # "start_battle" | "submit_result"
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=False)  # meters
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    matchup = relationship("Matchup", back_populates="location_verifications")
    user = relationship("User", back_populates="location_verifications")
    
    def __repr__(self):
        return f"<LocationVerification(matchup_id='{self.matchup_id}', event='{self.event_type}')>"


# ═══════════════════════════════════════════════
# FACTION MODELS
# ═══════════════════════════════════════════════


class Faction(Base):
    """Factions/armies available per game system"""
    
    __tablename__ = "factions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    game_system = Column(String(50), nullable=False, index=True)  # 'AoS', '40K', 'Old World'
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_factions = relationship("UserFaction", back_populates="faction", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Faction(name='{self.name}', system='{self.game_system}')>"


class UserFaction(Base):
    """User's favorite factions - many-to-many relationship"""
    
    __tablename__ = "user_factions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    faction_id = Column(UUID(as_uuid=True), ForeignKey("factions.id", ondelete="CASCADE"), nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)  # User's main faction per system
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", backref="factions")
    faction = relationship("Faction", back_populates="user_factions")
    
    def __repr__(self):
        return f"<UserFaction(user_id={self.user_id}, faction_id={self.faction_id})>"


# ═══════════════════════════════════════════════
# DATABASE CONFIGURATION
# ═══════════════════════════════════════════════


def get_database_url() -> str:
    """Get database URL from environment"""
    import os
    
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "squigleague")
    db_user = os.getenv("DB_USER", "squig")
    db_password = os.getenv("DB_PASSWORD", "dev_password_123")
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def init_database():
    """Initialize database connection and create tables"""
    engine = create_engine(get_database_url(), echo=True)
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get database session"""
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()
