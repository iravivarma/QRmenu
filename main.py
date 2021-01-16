# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 18:51:28 2021

@author: Ravi Varma Injeti
"""


from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session
import crud, models, schemas
import uvicorn
from database import SessionLocal, engine
from fastapi import Request
import time
import qrcode
import io, cv2
from starlette.responses import StreamingResponse, JSONResponse
from fastapi.responses import FileResponse
from PIL import Image
import logging, os


app = FastAPI()



filename = 'app.log'

if os.path.exists(filename):
    logging.basicConfig(filename=filename, filemode='a', format='%(name)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(filename=filename, filemode='w', format='%(name)s - %(levelname)s - %(message)s')


@app.on_event("shutdown")
async def on_shutdown():
    logging.warning("\n\n\n\n\n")
    logging.close()


# try:
#     logging.basicConfig(filename='app.log', filemode='w+', format='%(name)s - %(levelname)s - %(message)s')
# except:
#     logging.basicConfig(filename='app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

logging.getLogger(__name__)
logging.debug('This will get logged to a file')



models.Base.metadata.create_all(bind=engine)



@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    a middleware to find the time required for an api to process the data and
    getting the route of the api which is being executed...
    @parameters:
    request: contains all the details of the api requested
    ex:
        {'type': 'http', 'asgi': {'version': '3.0', 'spec_version': '2.1'}, 'http_version': '1.1', 
        'server': ('127.0.0.1', 5000), 'client': ('127.0.0.1', 61833), 'scheme': 'http', 'method': 'POST',
        'root_path': '', 'path': '/users', 'raw_path': b'/users', 'query_string': b'', 
        'headers': [(b'host', b'127.0.0.1:5000'), (b'connection', b'keep-alive'), (b'content-length', b'58'), 
        (b'accept', b'application/json'), (b'user-agent', b'Mozilla/5.0 (Windows NT 10.0; Win64; x64) 
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'), (b'content-type',
        b'application/json'), (b'origin', b'http://127.0.0.1:5000'), (b'sec-fetch-site', b'same-origin'), 
        (b'sec-fetch-mode', b'cors'), (b'sec-fetch-dest', b'empty'), (b'referer', b'http://127.0.0.1:5000/docs'),
        (b'accept-encoding', b'gzip, deflate, br'), (b'accept-language', b'en-US,en;q=0.9')], 
        'fastapi_astack': <contextlib.AsyncExitStack object at 0x00000185C3501088>, 
        'app': <fastapi.applications.FastAPI object at 0x00000185C08C2908>,
        'router': <fastapi.routing.APIRouter object at 0x00000185C33E8D88>, 
        'endpoint': <function create_user at 0x00000185C33CDE58>, 'path_params': {}}
    call_next: call_next starts analysing the request and the entire process of repsonse.

    @returns:
    response: just returns the api response and its execution time appended
    """
    start_time = time.time()
    response = await call_next(request)
    #print(request.body())
    #print(request.headers)
    #print("printing the scopes.......")
    #print(request.scope)
    path = [route for route in request.scope['router'].routes if route.endpoint == request.scope['endpoint']][0].path
    #this path variable derives the route of the api that is being accessed currently
    process_time = time.time() - start_time
    print(f'Path is: {path}\nexecution time is {process_time}')
    logging.warning(f'Path is: {path}\nexecution time is {process_time}')
    
    #print(process_time)
    response.headers["X-Process-Time"] = str(process_time)
    #adds the total execution time to the response
    #print(response)
    #print(response.headers)
    return response




def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        logging.info("database is closed.....")
        db.close()
        
        
@app.post("/users", response_model=schemas.Users)
async def create_user(user: schemas.NewUser, db: Session = Depends(get_db)):
    temp = user.__dict__
    print(temp)
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        logging.exception(f"email already registered for {user.email}")
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



@app.get("/display_qr/{hotel_id}")
async def get_menu_qr_code(hotel_id: str,  db: Session = Depends(get_db)):

    get_image = crud.get_qr_image(db=db, hotel_id = hotel_id)
    print(get_image)
    im = Image.open(get_image)  
    return StreamingResponse(im, media_type="image/png")


@app.get("/check_log")
async def check_log():
    try:
        x = 1/0
    except Exception as e:
        logging.error(repr(e))
        return JSONResponse(content={"code": 99, "message": repr(e)})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)