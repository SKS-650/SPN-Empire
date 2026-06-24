import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database.database import initialize_database_matrix

from app.backend.routes import (
    disease_routes,
    voice_routes,
    skin_routes,
    emergency_routes,
    reminder_routes,
    chat_routes,
)

app = FastAPI(
    title="Hamro Swasthya AI Backend",
    description="Production-ready REST API matrix supporting rural AI healthcare operations.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔄 Automatically mount and verify local SQLite tables on app load
@app.on_event("startup")
def startup_event():
    initialize_database_matrix()

# Serves static sound arrays (.mp3 responses) over network ports 
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 🔗 Integrated Routers Matching your workspace structural matrix
app.include_router(disease_routes.router, prefix="/api/v1/disease", tags=["Disease Analysis"])
app.include_router(voice_routes.router, prefix="/api/v1/voice", tags=["Voice Consultation"])
app.include_router(skin_routes.router, prefix="/api/v1/skin", tags=["Dermatology Vision"])
app.include_router(emergency_routes.router, prefix="/api/v1/emergency", tags=["Emergency SOS"])

# 🟢 FIXED: Kept singular matching your route file, which maps perfectly to the frontend now!
app.include_router(reminder_routes.router, prefix="/api/v1/reminder", tags=["Medicine Scheduler"])
app.include_router(chat_routes.router,    prefix="/api/v1/chat",     tags=["AI Health Chat"])

@app.get("/")
def root_check():
    return {"status": "online", "message": "Rural Healthcare AI Node Active"}