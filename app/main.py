from fastapi import FastAPI

from app.routers import health_router, push_router

# Initialize FastAPI app
app = FastAPI(
    title="CRM Push API",
    description="API for pushing contact profiles to HubSpot CRM",
    version="1.0.0",
)

# Register routers
app.include_router(health_router)
app.include_router(push_router)
