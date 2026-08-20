from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import Proyek, AnggotaProyek
from ..schemas import ProyekCreate, TimProyekCreate

router = APIRouter(
    prefix="/api/proyek",
    tags=["Proyek"]
)

@router.post("/", response_model=Proyek)
def create_proyek(proyek_in: ProyekCreate, session: Session = Depends(get_session)):
    proyek = Proyek.model_validate(proyek_in)
    session.add(proyek)
    session.commit()
    session.refresh(proyek)
    return proyek

@router.get("/", response_model=list[Proyek])
def get_proyek(session: Session = Depends(get_session)):
    statement = select(Proyek)
    results = session.exec(statement).all()
    return results

@router.post("/{id_proyek}/tim", response_model=list[AnggotaProyek])
def assign_tim(id_proyek: int, tim_in: TimProyekCreate, session: Session = Depends(get_session)):
    proyek = session.get(Proyek, id_proyek)
    if not proyek:
        raise HTTPException(status_code=404, detail="Proyek not found")
    
    anggota_list = []
    for agg in tim_in.anggota:
        new_anggota = AnggotaProyek(
            id_proyek=id_proyek,
            id_karyawan=agg.id_karyawan,
            proyek_role=agg.proyek_role
        )
        session.add(new_anggota)
        anggota_list.append(new_anggota)
    
    session.commit()
    for agg in anggota_list:
        session.refresh(agg)
        
    return anggota_list
