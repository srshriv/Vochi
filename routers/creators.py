from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Creator
from services.ai_service import build_voice_prompt
from pydantic import BaseModel

router = APIRouter(prefix="/creators", tags=["creators"])

class CreatorCreate(BaseModel):
    name: str
    niche: str
    primary_language: str
    sample_content: str

class CreatorResponse(BaseModel):
    id: int
    name: str
    niche: str
    primary_language: str
    voice_prompt: str | None
    class Config:
        from_attributes = True

@router.post("/", response_model=CreatorResponse)
def create_creator(data: CreatorCreate, db: Session = Depends(get_db)):
    voice_prompt = build_voice_prompt(data.name, data.niche, data.primary_language, data.sample_content)
    creator = Creator(
        name=data.name,
        niche=data.niche,
        primary_language=data.primary_language,
        sample_content=data.sample_content,
        voice_prompt=voice_prompt
    )
    db.add(creator)
    db.commit()
    db.refresh(creator)
    return creator

@router.get("/{creator_id}", response_model=CreatorResponse)
def get_creator(creator_id: int, db: Session = Depends(get_db)):
    creator = db.query(Creator).filter(Creator.id == creator_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    return creator

@router.get("/")
def list_creators(db: Session = Depends(get_db)):
    return db.query(Creator).all()