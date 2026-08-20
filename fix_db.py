from sqlmodel import create_engine, text
engine = create_engine('mysql+pymysql://root:@localhost:3306/db_kpi')
with engine.connect() as conn:
    conn.execute(text('ALTER TABLE Task MODIFY id_karyawan INT NULL;'))
    conn.commit()
