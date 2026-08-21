from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime, time
from .models import RoleEnum, KpiStatusEnum, PersetujuanEnum, MetodologiEnum, StatusProyekEnum, StatusSprintEnum, PrioritasEnum, StatusTaskEnum, TipeTaskEnum, JenisKerjaEnum, StatusSubmitEnum

# --- Proyek ---
class ProyekCreate(BaseModel):
    nama_proyek: str
    deskripsi: Optional[str] = None
    tanggal_mulai: date
    tanggal_selesai: date
    metodologi: MetodologiEnum
    status: StatusProyekEnum = StatusProyekEnum.Aktif

class ProyekUpdate(BaseModel):
    nama_proyek: Optional[str] = None
    deskripsi: Optional[str] = None
    tanggal_mulai: Optional[date] = None
    tanggal_selesai: Optional[date] = None
    metodologi: Optional[MetodologiEnum] = None
    status: Optional[StatusProyekEnum] = None

class AplikasiCreate(BaseModel):
    id_proyek: int
    nama_aplikasi: str
    deskripsi: Optional[str] = None
    tanggal_mulai: date
    tanggal_selesai: date
    status: StatusProyekEnum = StatusProyekEnum.Aktif
    qa_aplikasi: Optional[int] = None

class AplikasiUpdate(BaseModel):
    nama_aplikasi: Optional[str] = None
    deskripsi: Optional[str] = None
    tanggal_mulai: Optional[date] = None
    tanggal_selesai: Optional[date] = None
    status: Optional[StatusProyekEnum] = None
    qa_aplikasi: Optional[int] = None

class AnggotaProyekCreate(BaseModel):
    id_karyawan: int
    proyek_role: str # e.g., "Technical_Leader", "Anggota"

class TimProyekCreate(BaseModel):
    anggota: List[AnggotaProyekCreate]

# --- Sprint ---
class SprintCreate(BaseModel):
    id_aplikasi: int
    nama_sprint: str
    deskripsi: Optional[str] = None
    tanggal_mulai: date
    tanggal_selesai: date
    status: StatusSprintEnum

class SprintUpdate(BaseModel):
    nama_sprint: Optional[str] = None
    deskripsi: Optional[str] = None
    tanggal_mulai: Optional[date] = None
    tanggal_selesai: Optional[date] = None
    status: Optional[StatusSprintEnum] = None

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

class TaskUpdate(BaseModel):
    judul: Optional[str] = None
    deskripsi: Optional[str] = None
    tipe_task: Optional[TipeTaskEnum] = None
    prioritas: Optional[PrioritasEnum] = None
    status: Optional[StatusTaskEnum] = None
    waktu_deadline: Optional[datetime] = None

class TaskReview(BaseModel):
    is_passed: bool # True = Lolos, False = Revisi

# --- KPI Evaluator Response ---
class KpiEvaluationResponse(BaseModel):
    message: str
    kpi_performa: Optional[int] = None
    kpi_deadline: Optional[int] = None
    kpi_proyek: Optional[int] = None

# --- Submit Task ---
class SubmitTaskCreate(BaseModel):
    id_task: int
    url_task: str
    catatan: Optional[str] = None

class SubmitTaskReview(BaseModel):
    is_passed: bool  # True = Pass, False = Reject (kembali ke In_Progress)
