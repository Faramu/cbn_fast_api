import bcrypt
from sqlmodel import Session, select
from app.database import engine
from app.models import Karyawan, RoleEnum

names = [
    "Andi Prayoga", "Budi Santoso", "Citra Lestari", "Dewi Sartika", "Eko Prasetyo",
    "Fajar Nugroho", "Gita Gutawa", "Hadi Sucipto", "Indra Wijaya", "Joko Widodo",
    "Kartika Putri", "Lestari Ayu", "Maman Abdurrahman", "Nita Talia", "Oka Antara",
    "Putri Titian", "Qori Sandioriva", "Rudi Hartono", "Siti Aminah", "Tono Haryanto"
]

roles = [
    RoleEnum.Direktur, # 1
    RoleEnum.HRD, RoleEnum.HRD, RoleEnum.HRD, # 3
    RoleEnum.Karyawan, RoleEnum.Karyawan, RoleEnum.Karyawan, RoleEnum.Karyawan,
    RoleEnum.Karyawan, RoleEnum.Karyawan, RoleEnum.Karyawan, RoleEnum.Karyawan,
    RoleEnum.Karyawan, RoleEnum.Karyawan, RoleEnum.Karyawan, RoleEnum.Karyawan,
    RoleEnum.Karyawan, RoleEnum.Karyawan, RoleEnum.Karyawan, RoleEnum.Karyawan
]

def seed_karyawan():
    with Session(engine) as session:
        karyawans = session.exec(select(Karyawan).order_by(Karyawan.id_karyawan)).all()
        
        # Hash password 123123
        hashed_password = bcrypt.hashpw(b"123123", bcrypt.gensalt()).decode('utf-8')
        
        for i, k in enumerate(karyawans):
            if i < len(names):
                k.nama_karyawan = names[i]
                first_name = names[i].split(" ")[0].lower()
                k.email = f"{first_name}@gmail.com"
                k.role = roles[i]
                k.password = hashed_password
                
                # Make NIP unique per email just in case
                k.nip = f"NIP-{first_name.upper()}-2026"
                session.add(k)
        
        session.commit()
        print("Karyawan data updated successfully!")

if __name__ == "__main__":
    seed_karyawan()
