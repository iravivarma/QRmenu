# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 00:09:10 2020

@author: Ravi Varma Injeti
"""
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

import qrcode
import uvicorn

app = FastAPI()


class User(BaseModel):
    id : int
    hotel_name : str
    location_name : str
    email_id : str
    contact : int


external_data = {
    'id' : '12',
    'hotel_name' : 'santosh',
    'location_name' : 'kukatpally',
    'email_id' : 'rvarmainjeti@gmail.com',
    'contact' : '9492770572',
    
}

# user = User(**external_data)
# print(user.id)
# #> 123
# print(repr(user.hotel_name))
# #> datetime.datetime(2019, 6, 1, 12, 22)
# print(user.location_name)
# #> [1, 2, 3]
# print(user.dict())


@app.get("/items")
async def update_item(request: Request):

    json_compatible_item_data = external_data#jsonable_encoder(item)
    print(json_compatible_item_data)
    qr_code = qrcode.QRCode(version = 1,
                        box_size=10,
                        border = 4)
    print(qr_code)

    qr_code.add_data(json_compatible_item_data)
    qr_code.make(fit = True)
    print('image')

    qr_image = qr_code.make_image(fill = 'black', back_color = 'yellow')
    print("some")
    # print(dict(User)
    return external_data

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)

