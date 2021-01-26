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
    mobile_no: str




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
                 mobile_no: str = Form(...),
                 ):

        self.name = name
        self.email = email
        self.password = password
        self.mobile_no = mobile_no


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


class EmailSchema:
    """
    Pydantic Schema for email account recovery.

    Attributes
    ----------
    email : str
        The email where the recovery mail would be sent.
    """

    def __init__(self, email: str = Form(...)):
        """
        Parameters
        ----------
        email : HTML Form
            Would initialize the email from the submitted html form.
        """

        self.email = email


# class NewPassword(BaseModel):
#     """
#     Pydantic schema for user login
#     Currently the username is same as email
#     """
#     password1: str
#     password2: str

#     def __init__(self, password1:str = Form(...), password2:str = Form(...)):
#         super().__init__(password1, password2)


class NewPassword:
    """
    Pydantic Schema for account password.

    Attributes
    ----------
    password : str
        The new password that user will enter after forgot email verification.
    """

    def __init__(self, password1: str = Form(...),
                        password2: str = Form(...)):
        """
        Parameters
        ----------
        password : HTML Form
            Would initialize the password from the submitted html form.
        """

        self.password1 = password1
        self.password2 = password2


class SentPasscode:
    """
    Pydantic Schema for email account recovery.

    Attributes
    ----------
    passcode : str
        The passcode sent to the user on their mail.
    """

    def __init__(self, passcode: str = Form(...)):
        """
        Parameters
        ----------
        passcode : HTML Form
            Would initialize the passcode from the submitted html form.
        """

        self.passcode = passcode

