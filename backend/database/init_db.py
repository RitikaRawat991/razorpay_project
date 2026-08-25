from backend.database.base import Base
from backend.database.connection import engine
from backend.database.models import Merchant, Payment


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")