from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form, File
from sqlmodel import Session, select
from datetime import date, datetime
import shutil
import os
from decimal import Decimal
from ..database import get_session
from ..models import Kantor, Absensi, JenisKerjaEnum, PersetujuanEnum
from ..schemas import KantorCreate, KantorResponse, AbsensiResponse

router = APIRouter(tags=["Geofence & Absen"])

@router.get("/api/kantor", response_model=list[KantorResponse])
def get_semua_kantor(db: Session = Depends(get_session)):
    return db.exec(select(Kantor)).all()

@router.post("/api/kantor", response_model=KantorResponse)
def create_atau_update_kantor(kantor: KantorCreate, db: Session = Depends(get_session)):
    db_kantor = db.exec(select(Kantor)).first()
    if db_kantor:
        db_kantor.kantor_latitude = Decimal(str(kantor.kantor_latitude))
        db_kantor.kantor_longitude = Decimal(str(kantor.kantor_longitude))
        db_kantor.radius_meter = kantor.radius_meter
    else:
        db_kantor = Kantor(
            kantor_latitude=Decimal(str(kantor.kantor_latitude)),
            kantor_longitude=Decimal(str(kantor.kantor_longitude)),
            radius_meter=kantor.radius_meter
        )
        db.add(db_kantor)
    
    db.commit()
    db.refresh(db_kantor)
    return db_kantor

@router.post("/api/absen")
async def submit_absensi(
    id_karyawan: int = Form(...),
    jenis_kerja: str = Form(...),
    latitude: float = Form(None),
    longitude: float = Form(None),
    kpi_status: int = Form(...),
    alasan_telat: str = Form(None),
    foto: UploadFile = File(None),
    db: Session = Depends(get_session)
):
    foto_path = None
    if foto:
        os.makedirs("uploads/absen", exist_ok=True)
        foto_path = f"uploads/absen/{id_karyawan}_{foto.filename}"
        with open(foto_path, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
            
    absen_baru = Absensi(
        id_karyawan=id_karyawan,
        jenis_kerja=JenisKerjaEnum(jenis_kerja),
        tanggal_absen=date.today(),
        jam_absen=datetime.now().time(),
        latitude=Decimal(str(latitude)) if latitude else 0.0,
        longitude=Decimal(str(longitude)) if longitude else 0.0,
        kpi_status=kpi_status,
        alasan_telat=alasan_telat,
        bukti_keterlambatan=foto_path,
        persetujuan_terlambat=PersetujuanEnum.Pending if kpi_status < 100 else None
    )
    
    db.add(absen_baru)
    db.commit()
    db.refresh(absen_baru)
    return {"message": "Absensi berhasil disimpan", "data": absen_baru}
