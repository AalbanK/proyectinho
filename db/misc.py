from .database import SessionLocal

def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()