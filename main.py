from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import creators, conversations, orders, products, broadcasts, analytics

# Automatically generates tables on startup if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vochi API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(creators.router)
app.include_router(conversations.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(broadcasts.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {"status": "Vochi API running"}