# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 18:51:28 2021

@author: Ravi Varma Injeti
@contributor: KrishNa
"""


from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session
import crud, models, schemas
import uvicorn
from database import SessionLocal, engine
from fastapi import Request, APIRouter
import time
import qrcode
import io
from starlette.responses import StreamingResponse, JSONResponse
from fastapi.responses import FileResponse
from PIL import Image
import logging, os, time
from qr_logger import create_or_get_logger, log_warning


#app = FastAPI()
menu_router = APIRouter()

filename = 'app.log'
logging = create_or_get_logger(filename)

logging.getLogger(__name__)
logging.debug('This will get logged to a file')



models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        logging.info("database is closed.....")
        db.close()
        

       
@menu_router.post("/users", response_model=schemas.Users)
async def create_user(user: schemas.NewUser, db: Session = Depends(get_db)):
    temp = user.__dict__
    print(temp)
    db_user = crud.get_user_by_email(db, email=user.email)
    print(db_user)
    if db_user:
        logging.exception(f"email already registered for {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    insert_status = crud.create_user(db=db, user=user)
    print(insert_status)
    return insert_status
    

@menu_router.post("/users/{user_name}/hotels/", response_model=schemas.Hotels)
async def create_hotel_for_user(
    user_name: str, item: schemas.HotelsCreate, db: Session = Depends(get_db)
):
    return crud.create_hotel(db=db, item=item, user_name=user_name)




# @app.post("/hotels/{hotel_name}/update",response=schemas.Hotels)
# async def update_menu_for_hotel(hotel_name:str)



@menu_router.post("/hotels/delete/{hotel_name}")
async def delete_hotel(hotel_name: str, db: Session = Depends(get_db)):
    return crud.delete_hotel(db=db, hotel_name = hotel_name)


@menu_router.post('/hotels/menu/{menu_id}')
async def delete_menu(menu_id: str, db: Session = Depends(get_db)):
    return crud.delete_menu(db=db, menu_id = menu_id)



@menu_router.get("/userbase", response_model=List[schemas.Users])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@menu_router.get("/hotels/", response_model=List[schemas.Hotels])
async def get_hotels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_hotels(db, skip=skip, limit=limit)
    return items

@menu_router.get("/users/{user_name}", response_model=schemas.Users)
async def read_user(user_name: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_name=user_name).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@menu_router.post("/add_hotel_to_favourites/{user_id}/{hotel_id}")
async def add_hotel_to_favourites(user_id: int, hotel_id: int, db: Session = Depends(get_db)):
    db_fav = crud.add_hotel_to_favourite(db, user_id, hotel_id)
    print(db_fav)
    



@menu_router.post("/items/{user_id}")
async def insert_menu_items(user_id: int, menu_items: schemas.MenuItems, db: Session = Depends(get_db)):
    print(user_id)
    print(menu_items)
    print(type(menu_items))
    print(menu_items.items)

    inserting_menu_items = crud.insert_into_hotel_menu(db = db, menu_items = menu_items.items, user_id = user_id)
    print(inserting_menu_items)



@menu_router.get("/display_qr/{hotel_id}")
async def get_menu_qr_code(hotel_id: str,  db: Session = Depends(get_db)):

    get_image = crud.get_qr_image(db=db, hotel_id = hotel_id)
    print(get_image)
    im = Image.open(get_image)  
    return StreamingResponse(im, media_type="image/png")


@menu_router.get("/check_log")
async def check_log():
    try:
        x = 1/0
    except Exception as e:
        logging.error(repr(e))
        return JSONResponse(content={"code": 99, "message": repr(e)})


@menu_router.get("/hotels/{location}")
async def get_hotels_of_given_location(request: Request, location: str,  db: Session = Depends(get_db)):
    print(location)
    details = crud.get_hotels_of_given_location(db=db, location=location)
    print(details)

    return details



@menu_router.get("/get_users")
async def get_all_users(request: Request,  db: Session = Depends(get_db)):
    print("getting all users.............")
    print(request.headers)
    print(await request.body())
    print(await request.form())
    all_users = crud.get_all_users(db = db)
    return None




@menu_router.post("/insert_hotel/{username}")
async def insert_hotel(username: str, item: schemas.HotelsCreate, db: Session = Depends(get_db)):
    crud.insert_hotel_menu(db, username, item)








