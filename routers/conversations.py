from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Conversation, Creator, Product
from services.ai_service import classify_intent, detect_language, generate_response
from pydantic import BaseModel

router = APIRouter(prefix="/conversations", tags=["conversations"])

class MessageIn(BaseModel):
    creator_id: int
    buyer_name: str
    buyer_phone: str
    message: str

@router.post("/")
def receive_message(data: MessageIn, db: Session = Depends(get_db)):
    creator = db.query(Creator).filter(Creator.id == data.creator_id).first()
    intent = classify_intent(data.message)
    language = detect_language(data.message)
    
    products = db.query(Product).filter(Product.creator_id == data.creator_id, Product.is_active == True).all()
    product_list = [{"name": p.name, "brand_name": p.brand_name, "price": p.price, "description": p.description} for p in products]
    
    ai_response = generate_response(
        voice_prompt=creator.voice_prompt,
        message=data.message,
        intent=intent,
        language=language,
        products=product_list
    )
    
    conversation = Conversation(
        creator_id=data.creator_id,
        buyer_name=data.buyer_name,
        buyer_phone=data.buyer_phone,
        message=data.message,
        intent=intent,
        ai_response=ai_response,
        language_detected=language,
        status="replied"
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

@router.get("/creator/{creator_id}")
def get_conversations(creator_id: int, db: Session = Depends(get_db)):
    return db.query(Conversation).filter(Conversation.creator_id == creator_id).order_by(Conversation.created_at.desc()).limit(50).all()