from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

URL_DATABASE='mysql+pymysql://root:admin@localhost:3306/rag_llm_proj'

engine= create_engine(URL_DATABASE)

SessionLocal =sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base= declarative_base()

