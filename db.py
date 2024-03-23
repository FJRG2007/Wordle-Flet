from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine(
    "sqlite:///database/main.db", # Definimos la ruta de la base de datos que vamos a utilizar.
    connect_args={"check_same_thread": False}
    )

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()