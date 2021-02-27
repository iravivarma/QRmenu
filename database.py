# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 18:43:52 2020

@author: Ravi Varma Injeti
@contributor: KrishNa
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from qr_logger import create_or_get_logger, log_info


# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
filename = 'database.log'
logging = create_or_get_logger(filename)
username = 'postgres'
password = 'postgres'
ip_address = 'localhost'
port = '5432'
db = 'mymenu'
#SQLALCHEMY_DATABASE_URL = f"postgresql://{username}:{password}@{ip_address}:{port}/{db}"
SQLALCHEMY_DATABASE_URL = "postgres://grgztuvnabdzsz:d1204bf882973a09ef3231b59d8975fc195d3f8cadfb07f130caa5ebeb188fef@ec2-54-90-13-87.compute-1.amazonaws.com:5432/db0n84qslnukga"
log_info(logging, SQLALCHEMY_DATABASE_URL)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()