# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 23:18:21 2020

@author: Ravi Varma Injeti
"""

import qrcode
import matplotlib.pyplot as plt


code = {'breakfast': 'Dosa', 
        'Lunch': 'Rice',
        'Dinner' : 'chapati'}

##creating the Instance

qr_code = qrcode.QRCode(version = 1,
                        box_size=10,
                        border = 4)

qr_code.add_data(code)
qr_code.make(fit = True)

qr_image = qr_code.make_image(fill = 'black', back_color = 'yellow')

plt.imshow(qr_image)
plt.show








