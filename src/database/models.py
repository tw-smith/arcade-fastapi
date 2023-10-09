from sqlalchemy import Column, ForeignKey, Boolean, String, Integer, DateTime
from sqlalchemy.orm import relationship
from src.database.services.database import Base
import uuid


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=False)
    is_host = Column(Boolean, default=False)
    is_ready = Column(Boolean, default=False)
    scores = relationship("Score", back_populates="player", cascade="all, delete")
    lobby_id = Column(Integer, ForeignKey("lobbies.id"))
    lobby = relationship("Lobby", back_populates="players")


class Score(Base):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True, index=True)
    date_set = Column(DateTime)
    score_type = Column(String)
    value = Column(Integer, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    player = relationship("User", back_populates="scores")


class Lobby(Base):
    __tablename__ = "lobbies"
    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String, unique=True, index=True, default=str(uuid.uuid4()))
    name = Column(String, unique=True)

    players = relationship("User", back_populates="lobby")

