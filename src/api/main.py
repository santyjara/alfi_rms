import uvicorn
from db import startup_db_handler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import menu, orders, payments, reservations, tables

# Create FastAPI app
app = FastAPI(
    title="Restaurant Management System",
    description="API for managing restaurant operations",
    version="1.0.0",
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
app.include_router(tables.router)
app.include_router(reservations.router)
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(payments.router)


# Startup event
@app.on_event("startup")
def startup_event():
    startup_db_handler()


@app.get("/")
def read_root():
    return {
        "app": "Restaurant Management System",
        "version": "1.0.0",
        "documentation": "/docs",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
