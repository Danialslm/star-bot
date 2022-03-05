from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from env import DEBUG

# create a db engine and session maker
engine = create_engine(
    f'sqlite:///{Path(__file__).parent / "star_bot.db"}',
    echo=bool(DEBUG),  # echo queries in debug mode
    connect_args={"check_same_thread": False},
)
Session = sessionmaker(bind=engine)


def create_tables():
    from models import Base
    Base.metadata.create_all(engine)
