from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import Proyek, AnggotaProyek, Karyawan
from ..schemas import ProyekCreate, TimProyekCreate, ProyekUpdate

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

from typing import Any

@router.get("/", response_model=list[Any])
def get_proyek(session: Session = Depends(get_session)):
    statement = select(Proyek)
    proyeks = session.exec(statement).all()
    
    results = []
    for p in proyeks:
        p_dict = p.model_dump()
        
        # Get team member photos
        anggota_stmt = select(Karyawan.foto_karyawan).join(
            AnggotaProyek, AnggotaProyek.id_karyawan == Karyawan.id_karyawan
        ).where(AnggotaProyek.id_proyek == p.id_proyek)
        
        fotos = session.exec(anggota_stmt).all()
        # Filter out None and deduplicate if necessary
        p_dict["team_photos"] = [f for f in fotos if f]
        results.append(p_dict)
        
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

@router.put("/{id_proyek}", response_model=Proyek)
def update_proyek(id_proyek: int, proyek_in: ProyekUpdate, session: Session = Depends(get_session)):
    proyek = session.get(Proyek, id_proyek)
    if not proyek:
        raise HTTPException(status_code=404, detail="Proyek not found")
    
    update_data = proyek_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(proyek, key, value)
        
    session.add(proyek)
    session.commit()
    session.refresh(proyek)
    return proyek
