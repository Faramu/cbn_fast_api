import json
from sqlmodel import Session, select
from app.database import engine
from app.models import Proyek, Sprint, Task, AnggotaProyek, Karyawan, Kantor, Absensi, DoubleJob, KpiKerjaSama, LaporanKpi

def dump_table(model, session):
    records = session.exec(select(model)).all()
    return [r.model_dump(mode='json') for r in records]

def backup():
    with Session(engine) as session:
        data = {
            "Karyawan": dump_table(Karyawan, session),
            "Kantor": dump_table(Kantor, session),
            "Absensi": dump_table(Absensi, session),
            "Proyek": dump_table(Proyek, session),
            "AnggotaProyek": dump_table(AnggotaProyek, session),
            "Sprint": dump_table(Sprint, session),
            "Task": dump_table(Task, session),
            "DoubleJob": dump_table(DoubleJob, session),
            "KpiKerjaSama": dump_table(KpiKerjaSama, session),
            "LaporanKpi": dump_table(LaporanKpi, session),
        }
        with open("backup_data.json", "w") as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    backup()
