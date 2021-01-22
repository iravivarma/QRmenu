# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 21:48:41 2020

@author: Ravi Varma Injeti
@contributor: KrishNa
"""
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
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
    FavHotel = relationship("CustomerFavHotel", back_populates="owner")


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
    FavHotel = relationship("CustomerFavHotel", back_populates="hotels")
    menu = relationship("Menu", back_populates="hotels")
    
    
class Menu(Base):
    __tablename__ = "menu"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), unique=True)
    items = Column(JSON)
    qr_menu_path = Column(String)

    hotels = relationship("Hotels", back_populates="menu")
    

class CustomerFavHotel(Base):
    __tablename__ = "fav_hotel"
    id = Column(Integer, primary_key=True, index=True)
    user_id =Column(Integer, ForeignKey("users.id"))
    hotel_id = Column(Integer, ForeignKey("hotels.id"), unique=True)


    hotels = relationship("Hotels", back_populates="FavHotel")
    owner = relationship("Users", back_populates="FavHotel")



'''
1. origins/same or different
2. request packet size - content length
3. response packet size
4. type of request
5. request_method
6. content type
7. origin
8. referrer
9. browser name
10. destination path
11. device name
12. device ip address
13. if such api is called again and already stored in table, increment the count
14. datetime the request is requested.
15. reponse time
'''


class RequestResponseDetails(Base):
    __tablename__ = 'request_response_details'
    id = Column(Integer, primary_key=True, index=True)
    same_origin_yn = Column(Boolean)
    request_size = Column(Integer)
    response_size = Column(Integer)
    request_type = Column(String)
    request_method = Column(String)
    content_type = Column(String)
    origin = Column(String)
    referrer = Column(String)
    browser_name = Column(String)
    destination_path = Column(String)
    device_name = Column(String)
    ip_address = Column(String)
    datetime = Column(String)
    execution_time = Column(String)

    


    
    

    
    


# Base.metadata.create_all(engine, Base.metadata.tables.values(),checkfirst=True)
#Base.metadata.create_all(engine)
Users.__table__.create(bind=engine, checkfirst=True)
Hotels.__table__.create(bind=engine, checkfirst=True)
Menu.__table__.create(bind=engine, checkfirst=True)
CustomerFavHotel.__table__.create(bind=engine, checkfirst=True)
RequestResponseDetails.__table__.create(bind=engine, checkfirst=True)