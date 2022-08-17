#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

path = '/media/lewisliu/HDD/Clobotics/Data/CvDataOwnCloud/AutoFlight/TurbineData/foggingImage/testFolder'

pics = []

for i in os.walk(path):
        # print(i[0])
        for j in i[2]:
            picPath = i[0]+'/'+j
            # print(picPath)
            pics.append(picPath)

print len(pics)

defogPics = []
for i in pics:
    stringLen = len(i)
    picssPath = i[0:stringLen-4] + "_defog.JPG"
    defogPics.append(picssPath)

print defogPics