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
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from fastapi import APIRouter, status
from fastapi import BackgroundTasks, Request, Form, Depends
#from fastapi_mail.fastmail import FastMail
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



##############################################################
############reset or update password apis#####################

def send_email(background_tasks: BackgroundTasks, email, code, request: Request):
    """Sends an email with a defined template containing the passcode.

    Email is intialized at '/enter_recovery_email' endpoint as global.
    You have to fill in here your email and password from which you want
    to send the mail (GMAIL).

    Parameters
    ----------
    background_tasks : BackgroudTasks
        For sending the mail in the background.
    request : Request
        For using JinJaTemplates as a response.

    Returns
    -------
    template : Jinaja Template
        Returns the template "after_email_sent_response.html".
    """

    template = """
        <html>
        <body>
        <p>Hi !!!
        <br>Thanks for using Workeeper</p>
        <p> Your passcode is : %s </p>
        </body>
        </html>
        """ % (
        code
    )

    conf = ConnectionConfig(
    MAIL_USERNAME='krishnardt365@gmail.com',
    MAIL_PASSWORD="google@1A0",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False)


    message = MessageSchema(

        subject="password recovery",

        recipients=[email],  # List of recipients, as many as you can pass  

        body=template,

        subtype="html"

    )


    
    fm = FastMail(conf)

    #await fm.send_message(message)

    background_tasks.add_task(
        fm.send_message,
        message
    )

    return templates.TemplateResponse(
        "after_email_sent_response.html", {"request": request}
    )


@security_router.get("/enter_recovery_email")
async def get_email(request: Request):
    """Returns the homepage template where you enter your email - 'enter_email_for_recovery.html'"""

    return templates.TemplateResponse(
        "enter_email_for_recovery.html", {"request": request}
    )



def get_random_alphanumeric_string(length):
    """Generates a random alphanumeric string of given length.

    Parameters
    ----------
    length : int
        The length of random string to be generated.

    Returns
    -------
    result_str : string
        A random string of the length given.
    """

    letters_and_digits = string.ascii_letters + string.digits
    result_str = "".join((random.choice(letters_and_digits) for i in range(length)))
    return result_str




@security_router.post("/send_mail")
async def send_mail(
    background_tasks: BackgroundTasks,
    request: Request,
    email_schema: schemas.EmailSchema = Depends(), db: Session = Depends(get_db)
):
    """End-point to send the mail.

    Generates the security-code and then calls the send_email function.

    Parameters
    ----------
    background_tasks : BackgroudTasks
        For sending the mail in the background.
    request : Request
        For using JinJaTemplates as a response.
    email_schema : EmailSchema
        Schema to get the email of user.

    Returns
    -------
    template : Jinaja Template
        Calls the send_email funtion which returns the template.
    """

    #global code, Email#
    #print(email_schema.__dict__)
    email = email_schema.__dict__['email']
    code = get_random_alphanumeric_string(10)
    request.state.code = code
    crud.update_code(db, email, code)

    return send_email(background_tasks, email, code, request)


@security_router.get("/send_mail_again")
def send_mail_again(background_tasks: BackgroundTasks, request: Request):
    """Resends the mail when user clicks in the resend email button."""

    return send_email(background_tasks, request)

"""
Have to linkup with database...
users database has to be updated with new columns
columns: is_active, recent_login, recovery_passcode, recovered_yn
once the user asks for recovery_passcode, the recovered_yn has to be set as False
and the new generated passcode will be updated at recovery_passcode field

when user changes the password successfully, recovered_yn has to be True


"""
@security_router.post("/account_recovery/")
async def verify_passcode(request: Request, passcode_schema: schemas.SentPasscode = Depends(), db: Session = Depends(get_db)):
    """Checks if the passcode entered by the user is correct or not.

    Parameters
    ----------
    request : Request
        For using JinJaTemplates as a response.
    passcode_schema : SentPasscode
        schema to get the passcode entered by the user.

    Returns
    -------
    template : Jinaja Template
        Returns the "failed_verification.html" or
        "successful_verification_result.html" templates.
    """

    result = ""
    email = 'krishnardt365@gmail.com'
    code = crud.get_code(db, email)
    if passcode_schema.passcode == code:
        result = "successful"

        # give the result of passcode validation
        return templates.TemplateResponse(
            "successful_verification_result.html",
            {"request": request, "result": result},
        )
    else:
        result = "failed"

        return templates.TemplateResponse(
            "failed_verification.html", {"request": request, "result": result}
        )


@security_router.get("/re_enter_passcode")
async def re_enter_passcode(request: Request):
    """Redirects to "after_email_sent_response.html for re-entering of the passcode."""

    return templates.TemplateResponse(
        "after_email_sent_response.html", {"request": request}
    )


@security_router.get("/check_links")
async def check_links():
    return {"this is merge checking purpose"}


@security_router.get("/change_password")
async def after_successful_verification(request: Request):
    """Redirects to 'enter_new_password.html' for taking the new password
        of the user after forgot password email verification successful"""

    return templates.TemplateResponse("enter_new_password.html", {"request": request})


@security_router.post("/change_user_password")
async def update_password(new_password_schema: schemas.NewPassword = Depends(), db: Session = Depends(get_db)):
    """Calls the update function for the password from the crud module.

    Parameters
    ----------
    new_password_schema : NewPassword
        schema to get the password entered by the user.

    Returns
    -------
    For now just a json response to say updation successful.
    Later will be used to redirect it to the HOME PAGE of
    user's account at workeeper.
    """
    details = new_password_schema.__dict__
    print(details)
    recovery_status = crud.get_recovery_status(db, "krishnardt365@gmail.com")
    print(recovery_status)
    if details['password1'] == details['password2'] and recovery_status==False:
        password = get_password_hash(details['password1'])
        update_result = crud.change_user_password(db, "krishnardt365@gmail.com", password)
        return update_result
    else:
        return HTTPException(
                    status_code=HTTP_403_FORBIDDEN,  detail="not updated successfully"
                )
    #event_dict = {}
    #event_dict['Email']=Email
    #event_processor("PasswordUpdation",event_dict)

    return {"password updation": "successful"}




###########################################################################
'''
update password is working fine..
Except only thing has to be changed is get_current user...
Once the custom login works fine...we can get the current active user..
'''

@security_router.get("/update_password")
async def after_successful_verification(request: Request):
    """Redirects to 'enter_new_password.html' for taking the new password
        of the user after forgot password email verification successful"""

    return templates.TemplateResponse("enter_new_password.html", {"request": request})


@security_router.post("/update_user_password")
async def update_password(new_password_schema: schemas.NewPassword = Depends(), db: Session = Depends(get_db)):
    """Calls the update function for the password from the crud module.

    Parameters
    ----------
    new_password_schema : NewPassword
        schema to get the password entered by the user.

    Returns
    -------
    For now just a json response to say updation successful.
    Later will be used to redirect it to the HOME PAGE of
    user's account at workeeper.
    """
    details = new_password_schema.__dict__
    print(details)
    if details['password1'] == details['password2']:
        password = get_password_hash(details['password1'])
        update_result = crud.update_user_password(db, "krishnardt365@gmail.com", password)
        return update_result
    else:
        return HTTPException(
                    status_code=HTTP_403_FORBIDDEN,  detail="updated successfully"
                )
    #event_dict = {}
    #event_dict['Email']=Email
    #event_processor("PasswordUpdation",event_dict)

    return {"password updation": "successful"}
