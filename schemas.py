# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 17:43:53 2021

@author: Ravi Varma Injeti
"""

from typing import List, Optional, Dict

from pydantic import BaseModel


class HotelsBase(BaseModel):
    
    contact_email : str
    location : str
    pincode : int
    city : str


class HotelsCreate(HotelsBase):
    name : str


class Hotels(HotelsCreate):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name :str
    email: str
    


class UserCreate(UserBase):
    password: str


class NewUser(BaseModel):
    name: str
    email: str
    password: str




class Users(UserCreate):
    id: int

    class Config:
        orm_mode = True
        
        


class MenuItems(BaseModel):
    items = dict()

    def __repr__(self):
        return items.__dict__

