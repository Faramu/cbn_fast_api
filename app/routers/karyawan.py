from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, Request
from sqlmodel import Session, select
import shutil
import os
import uuid
import bcrypt
from ..database import get_session
from ..models import Karyawan

router = APIRouter(
    prefix="/api/karyawan",
    tags=["Karyawan"]
)

@router.get("/")
def get_karyawan(session: Session = Depends(get_session)):
    statement = select(Karyawan.id_karyawan, Karyawan.nama_karyawan, Karyawan.email, Karyawan.role)
    results = session.exec(statement).all()
    
    # We return a list of dicts or pydantic models. 
    # Since we didn't specify a response_model, a dict works well.
    karyawans = []
    for r in results:
        karyawans.append({
            "id_karyawan": r.id_karyawan,
            "nama_karyawan": r.nama_karyawan,
            "email": r.email,
            "role": r.role.value if r.role else None
        })
    return karyawans

@router.post("/update_profile")
async def update_profile(
    request: Request,
    id_karyawan: int = Form(...),
    nama_karyawan: str = Form(...),
    email: str = Form(...),
    nip: str = Form(...),
    posisi: str = Form(...),
    password: str = Form(None),
    foto: UploadFile = File(None),
    session: Session = Depends(get_session)
):
    user = session.exec(select(Karyawan).where(Karyawan.id_karyawan == id_karyawan)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Karyawan tidak ditemukan")
        
    user.nama_karyawan = nama_karyawan
    user.email = email
    user.nip = nip
    user.posisi = posisi
    
    if password:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed.decode('utf-8')
        
    if foto and foto.filename:
        ext = foto.filename.split('.')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        filepath = os.path.join("uploads", filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
            
        # Store relative path
        user.foto_karyawan = f"uploads/{filename}"
        
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {
        "message": "Profil berhasil diperbarui",
        "user": {
            "id_karyawan": user.id_karyawan,
            "nama_karyawan": user.nama_karyawan,
            "email": user.email,
            "role": user.role.value,
            "nip": user.nip,
            "posisi": user.posisi,
            "foto_karyawan": user.foto_karyawan
        }
    }
