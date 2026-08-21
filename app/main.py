from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from sqlmodel import SQLModel
from .database import engine

# Import routers
from .routers import proyek, aplikasi, sprint, task, kpi, auth, karyawan, submit_task, geofence_absen

app = FastAPI(title="KPI API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(proyek.router)
app.include_router(aplikasi.router)
app.include_router(sprint.router)
app.include_router(task.router)
app.include_router(kpi.router)
app.include_router(auth.router)
app.include_router(karyawan.router)
app.include_router(submit_task.router)
app.include_router(geofence_absen.router)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to KPI API"}

