from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Product
from pydantic import BaseModel

router = APIRouter(prefix="/products", tags=["products"])

class ProductCreate(BaseModel):
    creator_id: int
    brand_name: str
    name: str
    price: float
    description: str

@router.post("/")
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/creator/{creator_id}")
def get_products_by_creator(creator_id: int, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.creator_id == creator_id, Product.is_active == True).all()

@router.patch("/{product_id}/toggle")
def toggle_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = not product.is_active
    db.commit()
    return {"is_active": product.is_active}