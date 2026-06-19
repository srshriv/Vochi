from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Creator(Base):
    __tablename__ = "creators"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    niche = Column(String)
    primary_language = Column(String, default="Hinglish")
    voice_prompt = Column(Text)
    sample_content = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    products = relationship("Product", back_populates="creator")
    conversations = relationship("Conversation", back_populates="creator")
    orders = relationship("Order", back_populates="creator")
    buyers = relationship("Buyer", back_populates="creator")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("creators.id"))
    brand_name = Column(String)
    name = Column(String, nullable=False)
    price = Column(Float)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    creator = relationship("Creator", back_populates="products")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("creators.id"))
    buyer_name = Column(String, default="Anonymous")
    buyer_phone = Column(String)
    message = Column(Text, nullable=False)
    intent = Column(String) 
    ai_response = Column(Text)
    status = Column(String, default="pending")
    language_detected = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    creator = relationship("Creator", back_populates="conversations")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("creators.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    buyer_name = Column(String)
    amount = Column(Float)
    commission_rate = Column(Float, default=0.10)
    creator_earnings = Column(Float)
    status = Column(String, default="confirmed")
    created_at = Column(DateTime, server_default=func.now())

    creator = relationship("Creator", back_populates="orders")

class Buyer(Base):
    __tablename__ = "buyers"
    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("creators.id"))
    name = Column(String)
    phone = Column(String)
    language_preference = Column(String)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    last_purchase = Column(DateTime)
    segment = Column(String, default="new") 
    created_at = Column(DateTime, server_default=func.now())

    creator = relationship("Creator", back_populates="buyers")

class Broadcast(Base):
    __tablename__ = "broadcasts"
    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("creators.id"))
    original_message = Column(Text)
    ai_rewritten_message = Column(Text)
    target_segment = Column(String, default="all")
    status = Column(String, default="draft") 
    sent_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())