# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 21:48:41 2020

@author: Ravi Varma Injeti
"""
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
# from database import Base, engine

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/mymenu"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    hotels = relationship("Hotels", back_populates="owner")
    FavMenu = relationship("CustomerFavMenu", back_populates="owner")


class Hotels(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    contact_email = Column(String, unique=True, index=True)
    location = Column(String)
    pincode = Column(Integer)
    city = Column(String, index = True)

    owner = relationship("Users", back_populates="hotels")
    FavMenu = relationship("CustomerFavMenu", back_populates="hotels")
    menu = relationship("Menu", back_populates="hotels")
    
    
class Menu(Base):
    __tablename__ = "menu"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), unique=True)
    items = Column(JSON) 

    hotels = relationship("Hotels", back_populates="menu")
    

class CustomerFavMenu(Base):
    __tablename__ = "fav_menu"
    id = Column(Integer, primary_key=True, index=True)
    user_id =Column(Integer, ForeignKey("users.id"))
    hotel_id = Column(Integer, ForeignKey("hotels.id"), unique=True)


    hotels = relationship("Hotels", back_populates="FavMenu")
    owner = relationship("Users", back_populates="FavMenu")
    
    
    
    

    
    


# Base.metadata.create_all(engine, Base.metadata.tables.values(),checkfirst=True)
#Base.metadata.create_all(engine)
Users.__table__.create(bind=engine, checkfirst=True)
Hotels.__table__.create(bind=engine, checkfirst=True)
Menu.__table__.create(bind=engine, checkfirst=True)
CustomerFavMenu.__table__.create(bind=engine, checkfirst=True)