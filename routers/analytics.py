from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Conversation, Order, Buyer

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/creator/{creator_id}")
def get_analytics(creator_id: int, db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(Conversation.creator_id == creator_id).all()
    orders = db.query(Order).filter(Order.creator_id == creator_id).all()
    buyers = db.query(Buyer).filter(Buyer.creator_id == creator_id).all()
    
    total_conversations = len(conversations)
    total_orders = len(orders)
    conversion_rate = round((total_orders / total_conversations) * 100, 1) if total_conversations > 0 else 0
    
    intent_breakdown = {}
    language_breakdown = {}
    for c in conversations:
        intent_breakdown[c.intent] = intent_breakdown.get(c.intent, 0) + 1
        if c.language_detected:
            language_breakdown[c.language_detected] = language_breakdown.get(c.language_detected, 0) + 1
            
    superfans = [b for b in buyers if b.segment == "superfan"]
    regulars = [b for b in buyers if b.segment == "regular"]
    
    return {
        "total_conversations": total_conversations,
        "total_orders": total_orders,
        "conversion_rate": conversion_rate,
        "total_revenue": sum(o.amount for o in orders),
        "total_earnings": sum(o.creator_earnings for o in orders),
        "intent_breakdown": intent_breakdown,
        "language_breakdown": language_breakdown,
        "buyer_segments": {
            "superfans": len(superfans),
            "regular": len(regulars),
            "new": len([b for b in buyers if b.segment == "new"])
        }
    }