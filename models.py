from sqlalchemy import Column, String, Text, DateTime
from db import Base

class PageVisit(Base):
    __tablename__ = "page_visits"

    url = Column(String, primary_key=True)
    title = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime)
