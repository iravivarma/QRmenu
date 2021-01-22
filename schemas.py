# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 17:43:53 2021

@author: Ravi Varma Injeti
"""

from typing import List, Optional, Dict

from pydantic import BaseModel, EmailStr
from fastapi import Form


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


class user_item:
    """
    pydantic schema for new user sign-up
    """
    def __init__(self,
                 name: str = Form(...),
                 email: EmailStr = Form(...),
                 password: str = Form(...),
                 ):

        self.name = name
        self.email = email
        self.password = password











######################################################
###########security and user related schemas##########
class login_user_schema(BaseModel):
    """
    Pydantic schema for user login
    Currently the username is same as email
    """
    username: str
    name: Optional[str] = None
    email: Optional[str] = None
    disabled: Optional[bool] = None


class Token(BaseModel):
    """
    JWT token schema
    """    
    access_token: str
    token_type: str

