from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, func
from app.database import Base

class URL(Base):
    __tablename__ = "urls"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    short_code = Column(String(10), unique=True, index=True, nullable=False)

    long_url = Column(String(2048), nullable=False)

    user_id = Column(BigInteger, nullable=True)

    click_count = Column(BigInteger, default=0, nullable=False, server_default="0")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    expires_at = Column(DateTime(timezone=True), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)