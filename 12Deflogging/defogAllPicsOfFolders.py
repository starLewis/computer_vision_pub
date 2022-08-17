#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
from defog import defogOneImg
import time

#* find all pictures in parentPath, include sub folders' pictures
def findAllPics(parentPath):
    picsPath = []

    for i in os.walk(parentPath):
        for j in i[2]:
            picPath = i[0] + '/' + j
            picsPath.append(picPath)
        
    return picsPath

#* build the defogged picture's saved path
def buildSavedPathOfDefogged(imgPath):
    strlen = len(imgPath)
    resPath = ''
    # print("imgPath length: " + str(strlen))

    if strlen < 4:
        return resPath

    resPath = imgPath[0:strlen-4]+'_defogged.JPG'
    return resPath

#* defog one image and save the result
def defogOneImageAndSaved(imgPath, imgSavedPath):
    defogOneImg(imgPath, imgSavedPath)

#* defog one folder's images
def defogAllImgsOfFolders(parentPath):
    imgsPath = findAllPics(parentPath)

    print("images number is: " + str(len(imgsPath)))

    index = 0
    for imgPath in imgsPath:
        print('******')
        begin = time.time()
        imgSavedPath = buildSavedPathOfDefogged(imgPath)

        defogOneImageAndSaved(imgPath, imgSavedPath)
        end = time.time()
        index = index + 1
        print("defog img index:" + str(index) + '/' + str(len(imgsPath)) + " Done.")
        print("duration time: " + str(end-begin) + " s")
        print('********\n')

if __name__ == '__main__':
    parentPath = '/media/lewisliu/HDD/Clobotics/Data/CvDataOwnCloud/AutoFlight/TurbineData/foggingImage/21'
    # parentPath = '/media/lewisliu/HDD/Clobotics/Data/CvDataOwnCloud/AutoFlight/TurbineData/foggingImage/testFolder'
    defogAllImgsOfFolders(parentPath)
