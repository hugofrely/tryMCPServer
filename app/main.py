from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app.routers import health_router, push_router

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="CRM Push API",
    description="API for pushing contact profiles to HubSpot CRM",
    version="1.0.0",
)

# Register routers
app.include_router(health_router)
app.include_router(push_router)
