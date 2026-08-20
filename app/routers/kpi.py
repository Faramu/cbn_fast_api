from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database import get_session
from ..models import Task, Proyek, StatusTaskEnum, Sprint
from ..schemas import KpiEvaluationResponse

router = APIRouter(
    prefix="/api/kpi",
    tags=["KPI"]
)

@router.post("/evaluate-task/{id_task}", response_model=KpiEvaluationResponse)
def evaluate_task_kpi(id_task: int, session: Session = Depends(get_session)):
    task = session.get(Task, id_task)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if task.status != StatusTaskEnum.Done:
        raise HTTPException(status_code=400, detail="Task is not yet Done")
        
    # KPI Performa (Kualitas / Revisi) - Max 100
    kpi_performa = 100
    if task.jumlah_revisi > 3:
        extra_revisions = task.jumlah_revisi - 3
        kpi_performa -= (extra_revisions * 5)
        if kpi_performa < 0: kpi_performa = 0
        
    # KPI Deadline (Kecepatan) - Max 100
    kpi_deadline = 100
    if task.waktu_selesai and task.waktu_selesai > task.waktu_deadline:
        # Telat (Late). For simplicity, deduct 5 points if late at all (or you could deduct per day late)
        # SOP says: "Kurangi 5 Poin untuk setiap tiket terlambat", meaning it deducts 5 points from the score.
        kpi_deadline -= 5
        
    # In a real app, you would save this score to LaporanKpi table or update the user's running total.
    
    return KpiEvaluationResponse(
        message="Task KPI Evaluated successfully",
        kpi_performa=kpi_performa,
        kpi_deadline=kpi_deadline
    )

@router.post("/evaluate-project/{id_proyek}", response_model=KpiEvaluationResponse)
def evaluate_project_kpi(id_proyek: int, session: Session = Depends(get_session)):
    proyek = session.get(Proyek, id_proyek)
    if not proyek:
        raise HTTPException(status_code=404, detail="Proyek not found")
        
    # Check if ALL tasks in this project are DONE
    # Join Proyek -> Sprint -> Task
    statement = (
        select(Task)
        .join(Sprint, Task.id_sprint == Sprint.id_sprint)
        .where(Sprint.id_proyek == id_proyek)
    )
    
    all_tasks = session.exec(statement).all()
    if not all_tasks:
        return KpiEvaluationResponse(message="No tasks found in project", kpi_proyek=0)
        
    all_done = all(task.status == StatusTaskEnum.Done for task in all_tasks)
    
    if all_done:
        kpi_proyek = 100
        message = "Project completed. KPI Proyek is 100."
    else:
        kpi_proyek = 0
        message = "Project not yet completed. Tasks are still pending."
        
    # Save the score to LaporanKpi for the whole team...
    
    return KpiEvaluationResponse(
        message=message,
        kpi_proyek=kpi_proyek
    )
