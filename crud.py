# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 18:21:47 2021

@author: Ravi Varma Injeti
@contributor: KrishNa
"""

from sqlalchemy.orm import Session
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
import qrcode, os
import models, schemas
import qr_logger as qrl


filename = 'crud.log'
logging = qrl.create_or_get_logger(filename)


def get_user(db: Session, user_name: str):
    return db.query(models.Users).filter(models.Users.name == user_name)

def get_hotels(db: Session, name: str):
    return db.query(models.Hotels).filter(models.Hotels.name == name)



###may not work for HTTP 2 versions and above
# works for HTTP 1.1 version
def insert_request_response_data(db: Session, analysis_dict: dict):
    analysis_data = models.RequestResponseDetails(same_origin_yn = analysis_dict['same_origin_yn'],
        request_size = analysis_dict['request_size'], response_size = analysis_dict['response_size'],
        request_type = analysis_dict['request_type'], request_method = analysis_dict['request_method'],
        content_type = analysis_dict['content_type'], origin = analysis_dict['origin'],
        referrer = analysis_dict['referer'], browser_name= analysis_dict['browser'],
        destination_path = analysis_dict['destination_path'], device_name = analysis_dict['device_name'],
        ip_address = analysis_dict['ip_address'], datetime= str(analysis_dict['datetime']),
        execution_time = str(analysis_dict['execution_time']))
    db.add(analysis_data)
    db.commit()
    db.refresh(analysis_data)
    return analysis_data
    


def get_user_by_email(db: Session, email: str):
    return db.query(models.Users).filter(models.Users.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Users).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.NewUser):
    print(user.__dict__)
    secret_password = user.password
    db_user = models.Users(name=user.name, email=user.email, password=secret_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Hotels).offset(skip).limit(limit).all()


def get_qr_image(db: Session, hotel_id):
    menu_details= db.query(models.Menu).filter(models.Menu.hotel_id == hotel_id).first()
    menu_details = menu_details.qr_menu_path

    return menu_details



def create_user_item(db: Session, item: schemas.HotelsCreate, user_name: str):
    
    get_id = get_user(db, user_name)
    my_id = 0
    for ids in get_id:
        my_id = ids.id
    #print(db_item)
    #item.user_id = my_id
    #print(item.dict())
    print(item.__dict__)
    try:
        db_item = models.Hotels(name = item.name, user_id = my_id, contact_email = item.contact_email,
            location = item.location, pincode = item.pincode, city = item.city)
        
        print(item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        qrl.log_exception(logging, repr(e))
        return repr(e)
    



def insert_into_hotel_menu(db: Session, menu_items, user_id: int):


    print(menu_items)
    item = {}
    item['hotel_id'] = user_id
    item['items'] = menu_items
    print(item)
    qr_code = qrcode.QRCode(version = 1,
                        box_size=10,
                        border = 4)
    qr_code.add_data(menu_items)
    qr_code.make(fit = True)
    print('----------------------')
    dir_path = '/'.join(os.path.abspath(os.getcwd()).split('\\'))
    print(dir_path)
    folders = [x[0] for x in os.walk(dir_path)]
    print(folders)
    print('----------------------')
    qr_image = qr_code.make_image(fill = 'black', back_color = 'yellow')
    qr_image.save(dir_path+'/'+'qr_menus'+'/'+str(item['hotel_id'])+'_'+"menu.png")
    qr_path = dir_path+'/'+'qr_menus'+'/'+str(item['hotel_id'])+'_'+"menu.png"
    print(qr_image)
    
    print(os.getcwd())
    try:
        db_menu_item = models.Menu(hotel_id = user_id, items = menu_items, qr_menu_path = qr_path)
        qrl.log_info(logging, f'hotel_id: {user_id},\nmenu_items: {menu_items},\nqr_menu_path:{qr_path}')
        print(db_menu_item)
        db.add(db_menu_item)
        db.commit()
        db.refresh(db_menu_item)
        return db_menu_item
    except Exception as e:
        qrl.log_exception(logging, repr(e))
        return repr(e)


def add_hotel_to_favourite(db: Session, user_id, hotel_id):
    try:
        db_fav_hotel = models.CustomerFavMenu(user_id = user_id, hotel_id = hotel_id)
        qrl.log_info(f'user_id: {user_id} and hotel_id: {hotel_id}')
        db.add(db_fav_hotel)
        db.commit()
        db.refresh(db_fav_hotel)
        return db_fav_hotel

    except Exception as e:
        qrl_log_exception(logging, repr(e))
        return repr(e)



def delete_hotel(db: Session, hotel_name):
    result = db.query(models.Hotels).filter(models.Hotels.name==hotel_name).first()
    #print(result.id)

    if result is None:
        qrl.log_exception(logging, status.HTTP_404_NOT_FOUND)
        return HTTPException(status.HTTP_404_NOT_FOUND)
    else:

        print(result)
        print(result.id)
        db.delete(result)
        #result = db.commit()
        # result = db.commit()
        # print(result)
        del_menu = db.query(models.Menu).filter(models.Menu.hotel_id == result.id).delete()
        #print(del_menu.id)
        if del_menu is None:
            qrl.log_exception(logging, status.HTTP_404_NOT_FOUND)
            return HTTPException(status.HTTP_404_NOT_FOUND)
        else:
            #db.delete(del_menu)
            result = db.commit()

    return status.HTTP_200_OK


def delete_menu(db: Session, menu_id):
    try:
        db.query(models.Menu).filter(models.Menu.id == menu_id).delete()
        db.commit()
        qrl.log_info(logging, f'deleted records of menu records :{menu_id}')
        return status.HTTP_200_OK

    except:
        qrl.log_exception(logging, status.HTTP_404_NOT_FOUND)
        return HTTPException(status.HTTP_404_NOT_FOUND)




def authenticate_user_username_password(db: Session, username: str,password: str):
    """
    Authenticate user using username and password
    """

    get_my_details = get_user(db, username).first()
    
    if get_my_details is not None:
        my_username = get_my_details.name
        my_password = get_my_details.password

        print(my_password, password)

        if my_password == password:
            return get_my_details.__dict__
        else:
            return HTTPException(status=status.HTTP_500_NOT_FOUND, details='wrong password')
    else:
        return HTTPException(status=status.HTTP_404_NOT_FOUND, details='username not found')



def authenticate_user_email(db: Session, email: str):
    """
    useful when authenticating email to identify if the user is already present or not
    """

    details = db.query(models.Users).filter(models.Users.email == email).first()
    return details
