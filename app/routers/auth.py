from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select
import bcrypt
from ..database import get_session
from ..models import Karyawan

router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"]
)

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(request: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(Karyawan).where(Karyawan.email == request.email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah",
        )
    
    # Check password
    if not bcrypt.checkpw(request.password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah",
        )
    
    return {
        "message": "Login berhasil",
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
