from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

URL = "postgresql://postgres:root123@localhost/office"

engin = create_engine(URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engin)

Base = declarative_base()
