from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URL_DATABASE="mysql+pymysql://root:@localhost:3308/videojuegos"
engine=create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocomit=False,autoflush=False,bind=engine)
Base=declarative_base()