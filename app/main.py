from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import booking, services, schedule, appointments, dashboard, users, transactions

app = FastAPI(
    title="Nail Booking System",
    description="API for the Nail Booking System, following DDD, TDD, and BDD principles.",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React development servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the v1 API routers
app.include_router(booking.router, prefix="/api/v1", tags=["Booking"])
app.include_router(services.router, prefix="/api/v1", tags=["Services"])
app.include_router(schedule.router, prefix="/api/v1", tags=["Schedule"])
app.include_router(appointments.router, prefix="/api/v1", tags=["Appointments"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(transactions.router, prefix="/api/v1", tags=["Transactions"])


@app.get("/", tags=["Health Check"])
async def read_root():
    """A simple health check endpoint."""
    return {"status": "ok", "message": "Welcome to the Nail Booking System API!"}
