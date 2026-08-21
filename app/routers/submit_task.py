from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import SubmitTask, Task, StatusTaskEnum, StatusSubmitEnum
from ..schemas import SubmitTaskCreate, SubmitTaskReview

router = APIRouter(
    prefix="/api/submit-task",
    tags=["SubmitTask"]
)


@router.post("/", response_model=SubmitTask)
def create_submit(submit_in: SubmitTaskCreate, session: Session = Depends(get_session)):
    """Karyawan submit task: buat record SubmitTask (status=Review) dan ubah Task → Ready_for_QA."""
    task = session.get(Task, submit_in.id_task)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != StatusTaskEnum.In_Progress:
        raise HTTPException(
            status_code=400,
            detail=f"Task harus berstatus In_Progress untuk di-submit. Status saat ini: {task.status}"
        )

    # Buat record submit
    submit = SubmitTask(
        id_task=submit_in.id_task,
        url_task=submit_in.url_task,
        catatan=submit_in.catatan,
        status=StatusSubmitEnum.Review,
    )
    session.add(submit)

    # Ubah status task → Ready_for_QA (masuk kolom Review di kanban)
    task.status = StatusTaskEnum.Ready_for_QA
    session.add(task)

    session.commit()
    session.refresh(submit)
    return submit


@router.get("/task/{id_task}", response_model=List[SubmitTask])
def get_submits_by_task(id_task: int, session: Session = Depends(get_session)):
    """Ambil semua riwayat submit untuk satu task."""
    return session.exec(select(SubmitTask).where(SubmitTask.id_task == id_task)).all()


@router.get("/{id_submit_task}", response_model=SubmitTask)
def get_submit(id_submit_task: int, session: Session = Depends(get_session)):
    submit = session.get(SubmitTask, id_submit_task)
    if not submit:
        raise HTTPException(status_code=404, detail="SubmitTask not found")
    return submit


@router.put("/{id_submit_task}/review", response_model=SubmitTask)
def review_submit(id_submit_task: int, review_in: SubmitTaskReview, session: Session = Depends(get_session)):
    """QA review submit task.
    - is_passed=True  → SubmitTask.status=Pass,  Task.status=Done
    - is_passed=False → SubmitTask.status=Reject, Task.status=In_Progress, jumlah_revisi += 1
    """
    submit = session.get(SubmitTask, id_submit_task)
    if not submit:
        raise HTTPException(status_code=404, detail="SubmitTask not found")
    if submit.status != StatusSubmitEnum.Review:
        raise HTTPException(status_code=400, detail="Submit sudah diproses sebelumnya")

    task = session.get(Task, submit.id_task)
    if not task:
        raise HTTPException(status_code=404, detail="Task terkait tidak ditemukan")

    if review_in.is_passed:
        submit.status = StatusSubmitEnum.Pass
        task.status   = StatusTaskEnum.Done
    else:
        submit.status      = StatusSubmitEnum.Reject
        task.status        = StatusTaskEnum.In_Progress
        task.jumlah_revisi = (task.jumlah_revisi or 0) + 1

    session.add(submit)
    session.add(task)
    session.commit()
    session.refresh(submit)
    return submit
