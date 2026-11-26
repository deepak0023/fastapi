from sqlalchemy import Column, Integer, String
from database import Base

class Roles(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)