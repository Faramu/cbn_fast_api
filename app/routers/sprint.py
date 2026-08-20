from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import Sprint, Proyek
from ..schemas import SprintCreate

router = APIRouter(
    prefix="/api/sprint",
    tags=["Sprint"]
)

@router.get("/", response_model=list[Sprint])
def get_sprints(session: Session = Depends(get_session)):
    return session.exec(select(Sprint)).all()

@router.post("/", response_model=Sprint)
def create_sprint(sprint_in: SprintCreate, session: Session = Depends(get_session)):
    proyek = session.get(Proyek, sprint_in.id_proyek)
    if not proyek:
        raise HTTPException(status_code=404, detail="Proyek not found")
        
    if sprint_in.tanggal_selesai > proyek.tanggal_selesai:
        raise HTTPException(
            status_code=400, 
            detail=f"Tanggal selesai sprint ({sprint_in.tanggal_selesai}) tidak boleh melebihi tanggal selesai proyek ({proyek.tanggal_selesai})"
        )
        
    sprint = Sprint.model_validate(sprint_in)
    session.add(sprint)
    session.commit()
    session.refresh(sprint)
    return sprint
