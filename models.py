from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    page_visits = relationship("PageVisit", back_populates="owner")

class PageVisit(Base):
    __tablename__ = "page_visits"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text)
    title = Column(Text)
    visit_time = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="page_visits")