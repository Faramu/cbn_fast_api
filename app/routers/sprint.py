from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import Sprint, Aplikasi
from ..schemas import SprintCreate, SprintUpdate

router = APIRouter(
    prefix="/api/sprint",
    tags=["Sprint"]
)

@router.get("/", response_model=list[Sprint])
def get_sprints(session: Session = Depends(get_session)):
    return session.exec(select(Sprint)).all()

@router.get("/aplikasi/{id_aplikasi}", response_model=list[Sprint])
def get_sprints_by_aplikasi(id_aplikasi: int, session: Session = Depends(get_session)):
    return session.exec(select(Sprint).where(Sprint.id_aplikasi == id_aplikasi)).all()

@router.post("/", response_model=Sprint)
def create_sprint(sprint_in: SprintCreate, session: Session = Depends(get_session)):
    aplikasi = session.get(Aplikasi, sprint_in.id_aplikasi)
    if not aplikasi:
        raise HTTPException(status_code=404, detail="Aplikasi not found")
        
    if sprint_in.tanggal_selesai > aplikasi.tanggal_selesai:
        raise HTTPException(
            status_code=400, 
            detail=f"Tanggal selesai sprint ({sprint_in.tanggal_selesai}) tidak boleh melebihi tanggal selesai aplikasi ({aplikasi.tanggal_selesai})"
        )
        
    sprint = Sprint.model_validate(sprint_in)
    session.add(sprint)
    session.commit()
    session.refresh(sprint)
    return sprint

@router.put("/{id_sprint}", response_model=Sprint)
def update_sprint(id_sprint: int, sprint_in: SprintUpdate, session: Session = Depends(get_session)):
    sprint = session.get(Sprint, id_sprint)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    update_data = sprint_in.model_dump(exclude_unset=True)

    # Validate tanggal_selesai against aplikasi
    if "tanggal_selesai" in update_data:
        aplikasi = session.get(Aplikasi, sprint.id_aplikasi)
        if aplikasi and update_data["tanggal_selesai"] > aplikasi.tanggal_selesai:
            raise HTTPException(
                status_code=400,
                detail=f"Tanggal selesai sprint tidak boleh melebihi tanggal selesai aplikasi ({aplikasi.tanggal_selesai})"
            )

    for key, value in update_data.items():
        setattr(sprint, key, value)

    session.add(sprint)
    session.commit()
    session.refresh(sprint)
    return sprint
