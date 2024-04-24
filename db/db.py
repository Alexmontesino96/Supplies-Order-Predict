import os
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import declarative_base

nombre_base_datos = 'supplies_db'

# Crea la URL de la base de datos SQLite
database_url = f"sqlite:///{nombre_base_datos}.db"

engine = create_engine(database_url, echo=True)

Session = sessionmaker(bind=engine)

Base = declarative_base()
