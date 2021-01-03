# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 17:43:53 2021

@author: Ravi Varma Injeti
"""

from typing import List, Optional

from pydantic import BaseModel


class HotelsBase(BaseModel):
    
    contact_email : str
    location : str
    pincode : int
    city : str


class HotelsCreate(HotelsBase):
    user_id : str


class Hotels(HotelsBase):
    id: int
    name: str

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
        
        
        

    
    