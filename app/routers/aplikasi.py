from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import Aplikasi, Proyek, Karyawan
from ..schemas import AplikasiCreate, AplikasiUpdate

router = APIRouter(
    prefix="/api/aplikasi",
    tags=["Aplikasi"]
)

@router.get("/", response_model=list[Aplikasi])
def get_aplikasi(session: Session = Depends(get_session)):
    return session.exec(select(Aplikasi)).all()

@router.get("/proyek/{id_proyek}", response_model=list[Aplikasi])
def get_aplikasi_by_proyek(id_proyek: int, session: Session = Depends(get_session)):
    return session.exec(select(Aplikasi).where(Aplikasi.id_proyek == id_proyek)).all()

@router.post("/", response_model=Aplikasi)
def create_aplikasi(aplikasi_in: AplikasiCreate, session: Session = Depends(get_session)):
    proyek = session.get(Proyek, aplikasi_in.id_proyek)
    if not proyek:
        raise HTTPException(status_code=404, detail="Proyek not found")
        
    if aplikasi_in.tanggal_mulai < proyek.tanggal_mulai:
        raise HTTPException(status_code=400, detail="Tanggal mulai aplikasi tidak boleh lebih cepat dari tanggal mulai proyek")
    if aplikasi_in.tanggal_selesai > proyek.tanggal_selesai:
        raise HTTPException(status_code=400, detail="Tanggal selesai aplikasi tidak boleh lebih lambat dari tanggal selesai proyek")
        
    aplikasi = Aplikasi.model_validate(aplikasi_in)
    session.add(aplikasi)
    session.commit()
    session.refresh(aplikasi)
    return aplikasi

@router.put("/{id_aplikasi}", response_model=Aplikasi)
def update_aplikasi(id_aplikasi: int, aplikasi_in: AplikasiUpdate, session: Session = Depends(get_session)):
    aplikasi = session.get(Aplikasi, id_aplikasi)
    if not aplikasi:
        raise HTTPException(status_code=404, detail="Aplikasi not found")
        
    update_data = aplikasi_in.model_dump(exclude_unset=True)
    
    # Validation dates if they are being updated
    proyek = session.get(Proyek, aplikasi.id_proyek)
    new_mulai = update_data.get('tanggal_mulai', aplikasi.tanggal_mulai)
    new_selesai = update_data.get('tanggal_selesai', aplikasi.tanggal_selesai)
    
    if proyek:
        if new_mulai < proyek.tanggal_mulai:
            raise HTTPException(status_code=400, detail="Tanggal mulai aplikasi tidak boleh lebih cepat dari tanggal mulai proyek")
        if new_selesai > proyek.tanggal_selesai:
            raise HTTPException(status_code=400, detail="Tanggal selesai aplikasi tidak boleh lebih lambat dari tanggal selesai proyek")
            
    for key, value in update_data.items():
        setattr(aplikasi, key, value)
        
    session.add(aplikasi)
    session.commit()
    session.refresh(aplikasi)
    return aplikasi
