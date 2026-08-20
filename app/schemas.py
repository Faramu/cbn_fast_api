from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime, time
from .models import RoleEnum, KpiStatusEnum, PersetujuanEnum, MetodologiEnum, StatusProyekEnum, StatusSprintEnum, PrioritasEnum, StatusTaskEnum, TipeTaskEnum, JenisKerjaEnum

# --- Proyek ---
class ProyekCreate(BaseModel):
    nama_proyek: str
    deskripsi: Optional[str] = None
    tanggal_mulai: date
    tanggal_selesai: date
    metodologi: MetodologiEnum
    status: StatusProyekEnum = StatusProyekEnum.Aktif
    qa_proyek: Optional[int] = None

class AnggotaProyekCreate(BaseModel):
    id_karyawan: int
    proyek_role: str # e.g., "Technical_Leader", "Anggota"

class TimProyekCreate(BaseModel):
    anggota: List[AnggotaProyekCreate]

# --- Sprint ---
class SprintCreate(BaseModel):
    id_proyek: int
    nama_sprint: str
    deskripsi: Optional[str] = None
    tanggal_mulai: date
    tanggal_selesai: date
    status: StatusSprintEnum

# --- Task ---
class TaskCreate(BaseModel):
    id_sprint: int
    judul: str
    deskripsi: Optional[str] = None
    tipe_task: TipeTaskEnum
    prioritas: PrioritasEnum
    id_karyawan: Optional[int] = None # Assignee target by Role
    waktu_deadline: datetime
    dikerjakan_mandiri: bool = False

class TaskReview(BaseModel):
    is_passed: bool # True = Lolos, False = Revisi

# --- KPI Evaluator Response ---
class KpiEvaluationResponse(BaseModel):
    message: str
    kpi_performa: Optional[int] = None
    kpi_deadline: Optional[int] = None
    kpi_proyek: Optional[int] = None
