from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import date, datetime, time
from decimal import Decimal

class RoleEnum(str, Enum):
    HRD = "HRD"
    Karyawan = "Karyawan"
    Direktur = "Direktur"
    Quality_Assurance = "Quality_Assurance"
    Proyek_Manager = "Proyek_Manager"
    Koordinator_Proyek_Manager = "Koordinator_Proyek_Manager"
    Technical_Leader = "Technical_Leader"
    Koordinator_Technical_Leader = "Koordinator_Technical_Leader"

class JenisKerjaEnum(str, Enum):
    WFO = "WFO"
    WFA = "WFA"

class KpiStatusEnum(str, Enum):
    Excellent_Normal = "Excellent_Normal"
    Late_Danger = "Late_Danger"

class MetodologiEnum(str, Enum):
    Scrum = "Scrum"
    Kanban = "Kanban"

class PersetujuanEnum(str, Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"

class StatusProyekEnum(str, Enum):
    Aktif = "Aktif"
    Pending = "Pending"
    Selesai = "Selesai"

class ProyekRoleEnum(str, Enum):
    Member = "Member"
    Technical_Leader = "Technical_Leader"
    QA = "QA"

class StatusSprintEnum(str, Enum):
    Direncanakan = "Direncanakan"
    Aktif = "Aktif"
    Selesai = "Selesai"

class PrioritasEnum(str, Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"

class StatusTaskEnum(str, Enum):
    To_Do = "To_Do"
    In_Progress = "In_Progress"
    Ready_for_QA = "Ready_for_QA"
    Done = "Done"

class TipeTaskEnum(str, Enum):
    Feature = "Feature"
    Bug = "Bug"
    Tech_Debt = "Tech_Debt"
    Change_Request = "Change_Request"

class Karyawan(SQLModel, table=True):
    __tablename__ = "Karyawan"
    id_karyawan: Optional[int] = Field(default=None, primary_key=True)
    nip: str = Field(unique=True)
    nama_karyawan: str
    email: str = Field(unique=True)
    password: str
    posisi: str
    role: RoleEnum
    foto_karyawan: Optional[str] = None

class Kantor(SQLModel, table=True):
    __tablename__ = "Kantor"
    id_kantor: Optional[int] = Field(default=None, primary_key=True)
    kantor_latitude: Decimal
    kantor_longitude: Decimal
    radius_meter: int

class Absensi(SQLModel, table=True):
    __tablename__ = "Absensi"
    id_absensi: Optional[int] = Field(default=None, primary_key=True)
    id_karyawan: int = Field(foreign_key="Karyawan.id_karyawan")
    tanggal_absen: date
    jam_absen: time
    jam_keluar: Optional[time] = None
    jenis_kerja: JenisKerjaEnum
    latitude: Decimal
    longitude: Decimal
    kpi_status: KpiStatusEnum
    alasan_telat: Optional[str] = None
    bukti_keterlambatan: Optional[str] = None
    persetujuan_terlambat: Optional[PersetujuanEnum] = None

class Proyek(SQLModel, table=True):
    __tablename__ = "Proyek"
    id_proyek: Optional[int] = Field(default=None, primary_key=True)
    nama_proyek: str
    deskripsi: Optional[str] = None
    tanggal_mulai: date
    tanggal_selesai: date
    metodologi: MetodologiEnum
    status: StatusProyekEnum
    qa_proyek: Optional[int] = Field(default=None, foreign_key="Karyawan.id_karyawan")

class AnggotaProyek(SQLModel, table=True):
    __tablename__ = "AnggotaProyek"
    id_anggota_proyek: Optional[int] = Field(default=None, primary_key=True)
    id_proyek: int = Field(foreign_key="Proyek.id_proyek")
    id_karyawan: int = Field(foreign_key="Karyawan.id_karyawan")
    proyek_role: ProyekRoleEnum

class Sprint(SQLModel, table=True):
    __tablename__ = "Sprint"
    id_sprint: Optional[int] = Field(default=None, primary_key=True)
    id_proyek: int = Field(foreign_key="Proyek.id_proyek")
    nama_sprint: str
    deskripsi: Optional[str] = None
    tanggal_mulai: date
    tanggal_selesai: date
    status: StatusSprintEnum

class Task(SQLModel, table=True):
    __tablename__ = "Task"
    id_task: Optional[int] = Field(default=None, primary_key=True)
    id_sprint: int = Field(foreign_key="Sprint.id_sprint")
    judul: str
    deskripsi: Optional[str] = None
    tipe_task: TipeTaskEnum
    prioritas: PrioritasEnum
    id_karyawan: Optional[int] = Field(default=None, foreign_key="Karyawan.id_karyawan")
    status: StatusTaskEnum
    waktu_deadline: datetime
    tugas_dimulai: Optional[datetime] = None
    waktu_selesai: Optional[datetime] = None
    jumlah_revisi: int = Field(default=0)
    dikerjakan_mandiri: bool = Field(default=False)

class DoubleJob(SQLModel, table=True):
    __tablename__ = "DoubleJob"
    id_double_job: Optional[int] = Field(default=None, primary_key=True)
    id_karyawan: int = Field(foreign_key="Karyawan.id_karyawan")
    id_proyek_asal: int = Field(foreign_key="Proyek.id_proyek")
    id_proyek_tujuan: int = Field(foreign_key="Proyek.id_proyek")
    status: PersetujuanEnum
    bonus_kpi: int

class KpiKerjaSama(SQLModel, table=True):
    __tablename__ = "KpiKerjaSama"
    id_kpi_kerja_sama: Optional[int] = Field(default=None, primary_key=True)
    id_karyawan_tl: int = Field(foreign_key="Karyawan.id_karyawan")
    id_karyawan_anggota: int = Field(foreign_key="Karyawan.id_karyawan")
    tahun: int
    nilai_kpi: Decimal
    catatan: Optional[str] = None

class LaporanKpi(SQLModel, table=True):
    __tablename__ = "LaporanKpi"
    id_laporan_kpi: Optional[int] = Field(default=None, primary_key=True)
    id_karyawan: int = Field(foreign_key="Karyawan.id_karyawan")
    tahun: int
    kpi_absensi: Decimal
    kpi_kualitas: Decimal
    kpi_proyek: Decimal
    kpi_deadline: Decimal
    kpi_double_job: Decimal
    kpi_kerja_sama: Decimal
    final_kpi: Decimal
