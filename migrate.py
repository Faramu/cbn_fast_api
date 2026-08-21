import json
from sqlmodel import Session, SQLModel
from app.database import engine
from app.models import (
    Proyek, Aplikasi, Sprint, Task, AnggotaProyek, Karyawan, Kantor, Absensi, DoubleJob, KpiKerjaSama, LaporanKpi
)
from datetime import date, datetime, time

def parse_date(d):
    return date.fromisoformat(d) if d else None
def parse_datetime(dt):
    return datetime.fromisoformat(dt) if dt else None
def parse_time(t):
    return time.fromisoformat(t) if t else None

def migrate():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    
    with open("backup_data.json", "r") as f:
        data = json.load(f)
        
    with Session(engine) as session:
        # Restore simple tables
        for k_data in data.get("Karyawan", []):
            session.add(Karyawan(**k_data))
        for k_data in data.get("Kantor", []):
            session.add(Kantor(**k_data))
        for k_data in data.get("Absensi", []):
            k_data['tanggal_absen'] = parse_date(k_data.get('tanggal_absen'))
            k_data['jam_absen'] = parse_time(k_data.get('jam_absen'))
            k_data['jam_keluar'] = parse_time(k_data.get('jam_keluar'))
            session.add(Absensi(**k_data))
        
        session.commit()
        
        # Restore Proyek and create Applications
        proyek_to_aplikasi = {}
        for p_data in data.get("Proyek", []):
            qa_proyek = p_data.pop("qa_proyek", None)
            
            p_data['tanggal_mulai'] = parse_date(p_data.get('tanggal_mulai'))
            p_data['tanggal_selesai'] = parse_date(p_data.get('tanggal_selesai'))
            
            proyek = Proyek(**p_data)
            session.add(proyek)
            session.commit()
            session.refresh(proyek)
            
            app = Aplikasi(
                id_proyek=proyek.id_proyek,
                nama_aplikasi=f"App {proyek.nama_proyek}",
                deskripsi=proyek.deskripsi,
                tanggal_mulai=proyek.tanggal_mulai,
                tanggal_selesai=proyek.tanggal_selesai,
                status=proyek.status,
                qa_aplikasi=qa_proyek
            )
            session.add(app)
            session.commit()
            session.refresh(app)
            proyek_to_aplikasi[proyek.id_proyek] = app.id_aplikasi
            
        for a_data in data.get("AnggotaProyek", []):
            session.add(AnggotaProyek(**a_data))
            
        session.commit()
        
        # Restore Sprint
        for s_data in data.get("Sprint", []):
            old_proyek_id = s_data.pop("id_proyek", None)
            s_data["id_aplikasi"] = proyek_to_aplikasi.get(old_proyek_id)
            s_data['tanggal_mulai'] = parse_date(s_data.get('tanggal_mulai'))
            s_data['tanggal_selesai'] = parse_date(s_data.get('tanggal_selesai'))
            session.add(Sprint(**s_data))
            
        session.commit()
        
        # Restore Task
        for t_data in data.get("Task", []):
            t_data['waktu_deadline'] = parse_datetime(t_data.get('waktu_deadline'))
            t_data['tugas_dimulai'] = parse_datetime(t_data.get('tugas_dimulai'))
            t_data['waktu_selesai'] = parse_datetime(t_data.get('waktu_selesai'))
            session.add(Task(**t_data))
            
        for d_data in data.get("DoubleJob", []):
            session.add(DoubleJob(**d_data))
        for k_data in data.get("KpiKerjaSama", []):
            session.add(KpiKerjaSama(**k_data))
        for l_data in data.get("LaporanKpi", []):
            session.add(LaporanKpi(**l_data))
            
        session.commit()
        print("Migration successful.")

if __name__ == "__main__":
    migrate()
