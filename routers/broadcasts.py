from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Broadcast, Creator
from services.ai_service import rewrite_broadcast_in_creator_voice
from pydantic import BaseModel

router = APIRouter(prefix="/broadcasts", tags=["broadcasts"])

class BroadcastCreate(BaseModel):
    creator_id: int
    original_message: str
    target_segment: str = "all"

@router.post("/")
def create_broadcast(data: BroadcastCreate, db: Session = Depends(get_db)):
    creator = db.query(Creator).filter(Creator.id == data.creator_id).first()
    rewritten = rewrite_broadcast_in_creator_voice(
        voice_prompt=creator.voice_prompt,
        original_message=data.original_message,
        language=creator.primary_language
    )
    broadcast = Broadcast(
        creator_id=data.creator_id,
        original_message=data.original_message,
        ai_rewritten_message=rewritten,
        target_segment=data.target_segment,
        status="draft"
    )
    db.add(broadcast)
    db.commit()
    db.refresh(broadcast)
    return broadcast

@router.get("/creator/{creator_id}")
def get_broadcasts(creator_id: int, db: Session = Depends(get_db)):
    return db.query(Broadcast).filter(Broadcast.creator_id == creator_id).order_by(Broadcast.created_at.desc()).all()

@router.patch("/{broadcast_id}/send")
def send_broadcast(broadcast_id: int, db: Session = Depends(get_db)):
    broadcast = db.query(Broadcast).filter(Broadcast.id == broadcast_id).first()
    broadcast.status = "sent"
    broadcast.sent_count = 150
    db.commit()
    return broadcast