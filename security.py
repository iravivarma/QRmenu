import pickle
import random
import string
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Optional
from urllib import parse

# third party imports
# -------------------
from fastapi import APIRouter, status
from fastapi import BackgroundTasks, Request, Form, Depends
from fastapi_mail.fastmail import FastMail
from fastapi import Header, File, Body, Query, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from typing import Optional
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from fastapi.security.oauth2 import (
    OAuth2,
    OAuthFlowsModel,
    get_authorization_scheme_param,
)

from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse, HTMLResponse
from starlette.requests import Request

from jwt import PyJWTError
from jose import JWTError, jwt


from starlette.responses import JSONResponse, RedirectResponse, HTMLResponse

from pydantic import BaseModel, EmailStr

from passlib.context import CryptContext
import requests as rq
import msal


from models import Users
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import crud, models, schemas


security_router = APIRouter()

template_dir = os.path.dirname(
    os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
)
template_dir = os.path.join(template_dir, "Documents")
template_dir = os.path.join(template_dir, "QRmenu")
template_dir = os.path.join(template_dir, "templates")
print(template_dir)

templates = Jinja2Templates(directory=template_dir)

SECRET_KEY = "7ff8f44c419861f95ff39d0f157d41f2446b92a9868df2501c2e66061cdd8c74"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 3
COOKIE_AUTHORIZATION_NAME = "Authorization"
COOKIE_DOMAIN = 'http://127.0.0.1:8000'

# give the time for each token.
# Note: it is in minutes.
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# oauth2_scheme = OAuth2PasswordBearer(
#     tokenUrl="token",
#     scopes={"me": "Read information about the current user.", "items": "Read items."},
# )


class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = False,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        header_authorization: str = request.headers.get("Authorization")
        cookie_authorization: str = request.cookies.get("Authorization")

        header_scheme, header_param = get_authorization_scheme_param(
            header_authorization
        )
        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
        )

        if header_scheme.lower() == "bearer":
            authorization = True
            scheme = header_scheme
            param = header_param

        elif cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param

        else:
            authorization = False

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        return param



oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="/token")



@security_router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Takes in the OAuth2PasswordRequestForm and returns the access token.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}






async def get_current_google_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )
    db = get_db()
    print(token)
    if token is not None:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except:
            return None
        if email is not None:
            authenticated_user = crud.authenticate_user_email(db, email)
            user = authenticated_user
            return crud.get_user(user.name)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """This verifies that the hashed_password in DB is same as what user enters."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Generates hash for the password."""
    return pwd_context.hash(password)





def authenticate_user(db, username: str, password: str):
    """
    First gets the user with get_user function, then
    verifies its password woth the password entered at the front end.

    Parameters
    ----------
    username : str
        The username that the user entered.
    password : str
        The password entered by the user.

    Returns
    -------
    user : UserInDB
        The user info.
    """
    user = crud.get_user(db, username).first()
    print(user.__dict__)

    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user



async def get_current_active_user(current_user: schemas.NewUser = Depends(get_current_google_user)):
    # , current_google_user: User = Depends(get_current_google_user)
    """
    """
    print(current_user)
    return current_user



@security_router.get("/login")
def login_user_page(request: Request, redirect_url: Optional[str]=None, db: Session = Depends(get_db)):
    """Redirects to the user login or sign in page"""
    if redirect_url is None:
        redirect_url = "/userbase"
    #auth_url = _build_auth_url(scopes=SCOPE,state="/"+redirect_url)
    print("Redirect url",redirect_url)
    return templates.TemplateResponse("login.html", {"request": request, "redirect":redirect_url})
    



@security_router.get("/profile")
async def get_profile(request : Request, username: str, current_user: schemas.NewUser = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if not current_user:
        return "Not authorized"
    data = current_user
    return templates.TemplateResponse("User_Profile.html", {"request": request, "username": username, "position": data["position"],
                                        "location": data["location"], "email": data["email"], "company": data["company"]})


@security_router.post("/authenticate", response_model=schemas.Token)
async def check_user_and_make_token(request: Request, db: Session = Depends(get_db)):
    formdata = await request.form()
    print(request)
    print(formdata)
    print(formdata["username"],formdata["password"])
    authenticated_user = authenticate_user(db, formdata["username"],formdata["password"])
    print(authenticated_user)
    if authenticated_user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    access_token = create_access_token(
        data={"sub": authenticated_user.id}, expires_delta=access_token_expires
    )

    #################### SUCCESSFULLY LOGED IN USING CUSTOM DETAILS ######################
    #crud.logged_in(authenticated_user.id,"custom",request)

    token = jsonable_encoder(access_token)
    print("token is----------------------")
    print(token)
    response = JSONResponse({"access_token": token, "token_type": "bearer"})
    
    response.set_cookie(
        key=COOKIE_AUTHORIZATION_NAME,
        value=f"Bearer {token}",
        domain=COOKIE_DOMAIN,
        httponly=True,
        max_age=10800,          # 3 hours
        expires=10800,          # 3 hours
    )
    print(response.__dict__)
    return response

@security_router.get("/logout")
async def logout_and_remove_cookie(request: Request, current_user: schemas.NewUser = Depends(get_current_active_user), db: Session = Depends(get_db)) -> "RedirectResponse":
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    if not current_user:
        return response
    # usertype = crud.get_user_third_party(current_user.email)
    # if usertype=="google":
    #     return templates.TemplateResponse("google_signout.html", {"request": request})
    # else:
    response.delete_cookie(key=COOKIE_AUTHORIZATION_NAME, domain=COOKIE_DOMAIN)
    crud.logged_out(current_user.email)
    # return templates.TemplateResponse("logout.html",{"request":request, "instanceid":"13917092-3f6f-49e5-b39b-e21c89f24565"})
    return response


@security_router.get("/me")
async def get_mine(request: Request, current_user: schemas.NewUser = Depends(get_current_active_user), db: Session = Depends(get_db) ):
    return current_user


@security_router.get("/new_user_signup")
async def enter_new_user(request: Request):
    """Redirects to the New user sign up page"""

    return templates.TemplateResponse("signup.html", {"request": request})


@security_router.post("/new_user/")
async def newUser(user: schemas.user_item = Depends(), redirect_url:Optional[str]=None, db: Session = Depends(get_db)):
    try:
        user.password = get_password_hash(user.password)
        inserted_user = crud.create_user(db, user)
        #return inserted_user
    except:
        raise HTTPException(status_code=409, detail="Invalid username/password or user already exists")
    #event_processor("SignUp",inserted_user)
    if redirect_url:
        return RedirectResponse(url=f"/login?redirect_url={redirect_url}", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)



def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=3)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt