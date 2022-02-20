from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from env import DEBUG

# create a db engine and session maker
engine = create_engine('sqlite:///star_bot.db', echo=bool(DEBUG))  # echo queries in debug mode
Session = sessionmaker(bind=engine)


def create_tables():
    from models import Base
    Base.metadata.create_all(engine)
