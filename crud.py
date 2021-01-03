# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 18:21:47 2021

@author: Ravi Varma Injeti
"""

from sqlalchemy.orm import Session

import models, schemas


def get_user(db: Session, user_name: str):
    return db.query(models.Users).filter(models.Users.name == user_name)

def get_hotels(db: Session, name: str):
    return db.query(models.Hotels).filter(models.Hotels.name == name)


    


def get_user_by_email(db: Session, email: str):
    return db.query(models.Users).filter(models.Users.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Users).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.NewUser):
    secret_password = user.password + "notreallyhashed"
    db_user = models.Users(name=user.name, email=user.email, password=secret_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Hotels).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.HotelsCreate, user_name: str):
    
    get_id = get_user(db, user_name)
    my_id = 0
    for ids in get_id:
        my_id = ids.id
    #print(db_item)
    item.user_id = my_id
    print(item.dict())
    db_item = models.Hotels(**item.dict(), name=user_name)
    
    print(item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item