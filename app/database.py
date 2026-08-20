from sqlmodel import create_engine, SQLModel, Session

DATABASE_URL = "mysql+pymysql://root:@localhost:3306/db_kpi"

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
