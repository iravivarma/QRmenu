# import pickle
# import random
# import string
# import os
# import sys
# import json
# from datetime import datetime, timedelta
# from typing import Optional
# from urllib import parse

# # third party imports
# # -------------------
# from fastapi import APIRouter, status
# from fastapi import BackgroundTasks, Request, Form, Depends
# from fastapi_mail.fastmail import FastMail
# from fastapi import Header, File, Body, Query, UploadFile
# from fastapi.encoders import jsonable_encoder
# from fastapi.templating import Jinja2Templates
# from typing import Optional
# from fastapi.staticfiles import StaticFiles
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from fastapi.encoders import jsonable_encoder
# from fastapi.security.oauth2 import (
#     OAuth2,
#     OAuthFlowsModel,
#     get_authorization_scheme_param,
# )

# from starlette.status import HTTP_403_FORBIDDEN
# from starlette.responses import RedirectResponse, JSONResponse, HTMLResponse
# from starlette.requests import Request

# from jwt import PyJWTError
# from jose import JWTError, jwt


# from starlette.responses import JSONResponse, RedirectResponse, HTMLResponse

# from pydantic import BaseModel, EmailStr

# from passlib.context import CryptContext
# import requests as rq




# templates = Jinja2Templates(directory='/templates')



# SECRET_KEY = "7ff8f44c419861f95ff39d0f157d41f2446b92a9868df2501c2e66061cdd8c74"
# ALGORITHM = "HS256"

# # give the time for each token.
# # Note: it is in minutes.
# ACCESS_TOKEN_EXPIRE_MINUTES = 30


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# @security_router.get("/login")
# def login_user_page(request: Request, redirect_url: Optional[str]=None):
#     """Redirects to the user login or sign in page"""
#     if redirect_url is None:
#         redirect_url = "homepage"
#     auth_url = _build_auth_url(scopes=SCOPE,state="/"+redirect_url)
#     print("Redirect url",redirect_url)
#     return templates.TemplateResponse("User_Login.html", {"request": request, "redirect":redirect_url, "auth_url": auth_url})
    



# @security_router.get("/profile")
# async def get_profile(request : Request, username: str, current_user: User = Depends(get_current_active_user)):
#     if not current_user:
#         return "Not authorized"
#     data = current_user
#     return templates.TemplateResponse("User_Profile.html", {"request": request, "username": username, "position": data["position"],
#                                         "location": data["location"], "email": data["email"], "company": data["company"]})


# @security_router.post("/authenticate", response_model=Token, tags=["security"])
# async def check_user_and_make_token(request: Request):
#     formdata = await request.form()
#     print(request)
#     print(formdata)
#     authenticated_user = crud.authenticate_user_username_password(formdata["username"],formdata["password"])
#     if authenticated_user is None:
#         raise HTTPException(status_code=401, detail="Invalid username or password")

#     access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
#     access_token = create_access_token(
#         data={"sub": authenticated_user['_key']}, expires_delta=access_token_expires
#     )

#     #################### SUCCESSFULLY LOGED IN USING CUSTOM DETAILS ######################
#     crud.logged_in(authenticated_user["_key"],"custom",request)

#     token = jsonable_encoder(access_token)
#     response = JSONResponse({"access_token": token, "token_type": "bearer"})
    
#     response.set_cookie(
#         key=COOKIE_AUTHORIZATION_NAME,
#         value=f"Bearer {token}",
#         domain=COOKIE_DOMAIN,
#         httponly=True,
#         max_age=10800,          # 3 hours
#         expires=10800,          # 3 hours
#     )
#     return response

# @security_router.get("/logout")
# async def logout_and_remove_cookie(request: Request, current_user: User = Depends(get_current_active_user)) -> "RedirectResponse":
#     response = RedirectResponse(url="http://localhost:8000/api/v1/login", status_code=status.HTTP_303_SEE_OTHER)
#     if not current_user:
#         return response
#     usertype = crud.get_user_third_party(current_user.email)
#     if usertype=="google":
#         return templates.TemplateResponse("google_signout.html", {"request": request})
#     else:
#         response.delete_cookie(key=COOKIE_AUTHORIZATION_NAME, domain=COOKIE_DOMAIN)
#         crud.logged_out(current_user.email)
#         # return templates.TemplateResponse("logout.html",{"request":request, "instanceid":"13917092-3f6f-49e5-b39b-e21c89f24565"})
#         return response
