# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 18:51:28 2021

@author: Ravi Varma Injeti
"""


from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import crud, models, schemas
import uvicorn
from database import SessionLocal, engine
from fastapi import Request

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
@app.post("/users", response_model=schemas.Users)
async def create_user(user: schemas.NewUser, db: Session = Depends(get_db)):
    temp = user.__dict__
    print(temp)
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    insert_status = crud.create_user(db=db, user=user)
    print(insert_status)
    return insert_status
    

@app.post("/users/{user_name}/hotels/", response_model=schemas.Hotels)
async def create_item_for_user(
    user_name: str, item: schemas.HotelsCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_name=user_name)




# @app.post("/hotels/{hotel_name}/update",response=schemas.Hotels)
# async def update_menu_for_hotel(hotel_name:str)



@app.post("/hotels/delete/{hotel_name}")
async def delete_hotel(hotel_name: str, db: Session = Depends(get_db)):
    return crud.delete_hotel(db=db, hotel_name = hotel_name)


@app.post('/hotels/menu/{menu_id}')
async def delete_menu(menu_id: str, db: Session = Depends(get_db)):
    return crud.delete_menu(db=db, menu_id = menu_id)



@app.get("/users/", response_model=List[schemas.Users])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/hotels/", response_model=List[schemas.Hotels])
async def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.get("/users/{user_name}", response_model=schemas.Users)
async def read_user(user_name: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_name=user_name)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/add_hotel_to_favourites/{user_id}/{hotel_id}")
async def add_hotel_to_favourites(user_id: int, hotel_id: int, db: Session = Depends(get_db)):
    db_fav = crud.add_hotel_to_favourite(db, user_id, hotel_id)
    print(db_fav)
    



@app.post("/items/{user_id}")
async def insert_menu_items(user_id: int, menu_items: schemas.MenuItems, db: Session = Depends(get_db)):
    print(user_id)
    print(menu_items)
    print(type(menu_items))
    print(menu_items.items)

    inserting_menu_items = crud.insert_into_hotel_menu(db = db, menu_items = menu_items.items, user_id = user_id)
    print(inserting_menu_items)





if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)