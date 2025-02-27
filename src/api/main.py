import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all routers
from src.api.routers import auth, menu, order, payment, reservation, table

# Import database utilities
from src.gateways.database.utils import startup_db_handler

# Create FastAPI app
app = FastAPI(
    title="Restaurant Management System",
    description="API for managing restaurant operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)  # Auth router first
app.include_router(table.router)
app.include_router(reservation.router)
app.include_router(menu.router)
app.include_router(order.router)
app.include_router(payment.router)


# Startup event
@app.on_event("startup")
def startup_event():
    startup_db_handler()


@app.get("/")
def read_root():
    return {
        "application": "Restaurant Management System API",
        "version": "1.0.0",
        "documentation": "/docs",
        "alternative_documentation": "/redoc",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
