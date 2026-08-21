from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime, time
from typing import List, Optional
from ..database import get_session
from ..models import Task, Sprint, StatusTaskEnum
from ..schemas import TaskCreate, TaskReview, TaskUpdate

router = APIRouter(
    prefix="/api/task",
    tags=["Task"]
)

@router.get("/", response_model=List[Task])
def get_tasks(id_sprint: Optional[int] = None, session: Session = Depends(get_session)):
    query = select(Task)
    if id_sprint:
        query = query.where(Task.id_sprint == id_sprint)
    return session.exec(query).all()

@router.post("/", response_model=Task)
def create_task(task_in: TaskCreate, session: Session = Depends(get_session)):
    sprint = session.get(Sprint, task_in.id_sprint)
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
        
    # Capping Deadline Logic
    waktu_deadline = task_in.waktu_deadline
    # Convert sprint.tanggal_selesai (date) to datetime for comparison
    sprint_end_dt = datetime.combine(sprint.tanggal_selesai, time.max)
    
    if waktu_deadline > sprint_end_dt:
        waktu_deadline = sprint_end_dt
        
    task = Task(
        id_sprint=task_in.id_sprint,
        judul=task_in.judul,
        deskripsi=task_in.deskripsi,
        tipe_task=task_in.tipe_task,
        prioritas=task_in.prioritas,
        id_karyawan=task_in.id_karyawan,
        status=StatusTaskEnum.To_Do,
        waktu_deadline=waktu_deadline,
        dikerjakan_mandiri=task_in.dikerjakan_mandiri,
        jumlah_revisi=0
    )
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.put("/{id_task}", response_model=Task)
def update_task(id_task: int, task_in: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, id_task)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.put("/{id_task}/pull", response_model=Task)
def pull_task(id_task: int, id_karyawan: int, session: Session = Depends(get_session)):
    task = session.get(Task, id_task)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if task.status != StatusTaskEnum.To_Do:
        raise HTTPException(status_code=400, detail="Task is not in To_Do status")
        
    task.id_karyawan = id_karyawan
    task.status = StatusTaskEnum.In_Progress
    task.tugas_dimulai = datetime.now()
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.put("/{id_task}/submit", response_model=Task)
def submit_task(id_task: int, session: Session = Depends(get_session)):
    task = session.get(Task, id_task)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if task.status != StatusTaskEnum.In_Progress:
        raise HTTPException(status_code=400, detail="Task is not In_Progress")
        
    task.status = StatusTaskEnum.Ready_for_QA
    
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.put("/{id_task}/review", response_model=Task)
def review_task(id_task: int, review_in: TaskReview, session: Session = Depends(get_session)):
    task = session.get(Task, id_task)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if task.status != StatusTaskEnum.Ready_for_QA:
        raise HTTPException(status_code=400, detail="Task is not Ready_for_QA")
        
    if review_in.is_passed:
        task.status = StatusTaskEnum.Done
        task.waktu_selesai = datetime.now()
        # TODO: Trigger KPI Evaluator for Performa & Deadline here or separately
    else:
        task.status = StatusTaskEnum.In_Progress
        task.jumlah_revisi += 1
        
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
