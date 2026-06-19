from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Order, Buyer
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/orders", tags=["orders"])

class OrderCreate(BaseModel):
    creator_id: int
    product_id: int
    buyer_name: str
    amount: float
    commission_rate: float = 0.10

@router.post("/")
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    earnings = data.amount * data.commission_rate
    order = Order(
        creator_id=data.creator_id,
        product_id=data.product_id,
        buyer_name=data.buyer_name,
        amount=data.amount,
        commission_rate=data.commission_rate,
        creator_earnings=earnings
    )
    db.add(order)
    
    buyer = db.query(Buyer).filter(Buyer.creator_id == data.creator_id, Buyer.name == data.buyer_name).first()
    if buyer:
        buyer.total_orders += 1
        buyer.total_spent += data.amount
        buyer.last_purchase = datetime.now()
        buyer.segment = "superfan" if buyer.total_orders >= 3 else "regular" if buyer.total_orders >= 2 else "new"
    else:
        buyer = Buyer(
            creator_id=data.creator_id,
            name=data.buyer_name,
            total_orders=1,
            total_spent=data.amount,
            last_purchase=datetime.now(),
            segment="new"
        )
        db.add(buyer)
        
    db.commit()
    db.refresh(order)
    return order

@router.get("/creator/{creator_id}")
def get_orders(creator_id: int, db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.creator_id == creator_id).order_by(Order.created_at.desc()).all()

@router.get("/creator/{creator_id}/earnings")
def get_earnings(creator_id: int, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.creator_id == creator_id).all()
    total_revenue = sum(o.amount for o in orders)
    total_earnings = sum(o.creator_earnings for o in orders)
    return {
        "total_revenue": total_revenue,
        "total_earnings": total_earnings,
        "total_orders": len(orders)
    }