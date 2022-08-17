# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sys
import json
import os
import cv2
import copy
import numpy as np

FPIndex = 0
FPPair = {}
FPPairs = []

IMGWIDTH = 1500
IMGHEIGHT = 1000
writeX = IMGWIDTH + 20
writeY = 20

pathsName = [
        "A_1_PS_LE_View","A_2_PS_TE_View","A_3_SS_TE_View","A_4_SS_LE_View",
        "B_1_PS_LE_View","B_2_PS_TE_View","B_3_SS_TE_View","B_4_SS_LE_View",
        "C_1_SS_LE_View","C_2_SS_TE_View","C_3_PS_TE_View","C_4_PS_LE_View"
    ]
pathsNameThumb = [
        "A_1","A_2","A_3","A_4",
        "B_1","B_2","B_3","B_4",
        "C_1","C_2","C_3","C_4"
    ]

class Util:
    def __init__(self):
        pass

    #* load json file to json data
    def fileToJson(self, filePath):
        jsonData = None
        with open(filePath, 'r') as jsonOpen:
            jsonData = json.load(jsonOpen)
        jsonOpen.close()
        return jsonData

    #* write json data to saving path
    def jsonToFile(self, jsonData, outFilePath):
        with open(outFilePath, 'w') as outFile:
            json.dump(jsonData,outFile)
        outFile.close()

#* the status of marking pair points
statusMarker = {
    'init':'init',
    'markRefImg':'markRefImg',
    'markCurImg':'markCurImg',
    'storeMaker':'storeMarker'
}

#* mark same marker in two different images
class PairMarker:
    def __init__(self, markerData, refMetaData, curMetaData, pathIndex):
        self.markerData = markerData
        self.refMetaData = refMetaData
        self.curMetaData = curMetaData
        self.curFlightPathIndex = pathIndex
        self.curMakerId = None
        self.curMakerIndex = 0

        self.refImgName = None
        self.refImgPT = [0.23, 0.24]
        self.refImgPath = None
        self.refImgIndex = 0

        self.curImgName = None
        self.curImgPath = None
        self.curImgIndex = 0
        self.curImgPT = [0.234, 0.243]

        self.curStatusMarker = statusMarker['init']

        self.imgWindowName = "pairPointsMarker"
        cv2.namedWindow(self.imgWindowName)
        cv2.setMouseCallback(self.imgWindowName,self.drawFP)

        self.img = np.ones((IMGHEIGHT, IMGWIDTH+300, 3), np.uint8)

    
    #* define mouse event
    def drawFP(self, event, x, y, flags, param):
        global writeX, writeY
        if event == cv2.EVENT_LBUTTONUP:
            xPosRatio = 1.0 * x / IMGWIDTH
            yPosRatio = 1.0 * y / IMGHEIGHT

            if self.curStatusMarker == statusMarker['init'] or self.curStatusMarker == statusMarker['markRefImg']:
                self.curStatusMarker = statusMarker['markRefImg']
                self.refImgPT[0] = xPosRatio
                self.refImgPT[1] = yPosRatio
                cv2.putText(self.img,"curMakerId: " + str(self.curMakerId), (writeX, writeY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1)
                writeY += 20
                cv2.putText(self.img,"status: " + str(self.curStatusMarker), (writeX, writeY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1)
                writeY += 20
                cv2.putText(self.img,"PT: " + str(self.refImgPT[0]) + ", " + str(self.refImgPT[1]), (writeX, writeY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1)
                writeY += 20
            elif self.curStatusMarker == statusMarker['markCurImg']:
                self.curImgPT[0] = xPosRatio
                self.curImgPT[1] = yPosRatio
                cv2.putText(self.img,"curMakerId: " + str(self.curMakerId), (writeX, writeY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1)
                writeY += 20
                cv2.putText(self.img,"status: " + str(self.curStatusMarker), (writeX, writeY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1)
                writeY += 20
                cv2.putText(self.img,"PT: " + str(self.curImgPT[0]) + ", " + str(self.curImgPT[1]), (writeX, writeY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1)
                writeY += 20            

    #* do marker
    def mark(self):

        self.curMakerIndex = 0
        for i in self.markerData['pairPoints']:
            self.refImgName = i['refImgName']
            self.refImgPath, self.refImgIndex = self.findImgPath(self.refImgName, self.refMetaData)

            self.curImgName = i['curImgName']
            self.curImgPath, self.curImgIndex = self.findImgPath(self.curImgName, self.curMetaData)

            self.curMakerId = str(pathsNameThumb[self.curFlightPathIndex]) + "_" + str(self.curMakerIndex)
            self.markCurrentPair()
            i['markerId'] = self.curMakerId
            i['refImgIndex'] = self.refImgIndex
            i['refPoint'][0] = self.refImgPT[0]
            i['refPoint'][1] = self.refImgPT[1]

            i['curImgIndex'] = self.curImgIndex
            i['curPoint'][0] = self.curImgPT[0]
            i['curPoint'][1] = self.curImgPT[1]
            self.curMakerIndex += 1


    def markCurrentPair(self):
        self.img = np.ones((IMGHEIGHT, IMGWIDTH+300, 3), np.uint8)
        global writeX, writeY
        writeX = IMGWIDTH + 20
        writeY = 20
        while(1):
            if self.curStatusMarker == statusMarker['init'] or self.curStatusMarker == statusMarker['markRefImg']:
                img = cv2.imread(self.refImgPath)
                img = cv2.resize(img, (IMGWIDTH, IMGHEIGHT), 0.5, 0.5, cv2.INTER_CUBIC)
                self.img[0:IMGHEIGHT, 0:IMGWIDTH] = img
                cv2.imshow(self.imgWindowName, self.img)
            elif self.curStatusMarker == statusMarker['markCurImg']:
                img = cv2.imread(self.curImgPath)
                img = cv2.resize(img, (IMGWIDTH, IMGHEIGHT), 0.5, 0.5, cv2.INTER_CUBIC)
                self.img[0:IMGHEIGHT, 0:IMGWIDTH] = img
                cv2.imshow(self.imgWindowName, self.img)

            k = cv2.waitKey(1) & 0xFF
            if k == ord('q') or k == ord('s'):
                self.curStatusMarker = statusMarker['init']
                break
            elif k == ord('r'):
                self.curStatusMarker = statusMarker['markRefImg']
            elif k == ord('c'):
                self.curStatusMarker = statusMarker['markCurImg']

            

    #* find img path from metadata
    def findImgPath(self,imgName, metadata):
        for pathInfo in metadata:
            for img in pathInfo['imgs']:
                if img['imgName'] == imgName:
                    return img['imgPath'], img['index']

        print("error! findImgPath() => doesn't find img from metadata")
        return None,None
            


if __name__ == '__main__':
    #* set target folder for get metadata's json
    folderPath = "/home/lewisliu/Clobotics/Data/CvDataOwnCloud/AutoFlight/TurbineData/SGRE/TurbineData/11_M14_20190711T093810"

    utilInstance = Util()

    pathIndex = 9
    curMarkFileName = "blade_" + pathsName[pathIndex] + "_Marker.json"
    curMarkDataJsonFilePath = os.path.join(folderPath, curMarkFileName)

    print curMarkDataJsonFilePath

    #* load
    markerData = utilInstance.fileToJson(curMarkDataJsonFilePath)
    print markerData

    #* find the metadata file path of current flight path
    refMetaFileName = "blade_A_picsMetdata.json"
    if markerData['bladeName'] == 'B':
        refMetaFileName = "blade_B_picsMetdata.json"
    elif markerData['bladeName'] == 'C':
        refMetaFileName = "blade_C_picsMetdata.json"
    curMetaFileName = refMetaFileName

    #* load ref metadata
    refMetaFilePath = os.path.join(markerData['refTurbinePicFolderPath'],markerData['bladeName'],refMetaFileName)
    refMetaData = utilInstance.fileToJson(refMetaFilePath)

    # print refMetaData
    #* load cur metadata
    curMetaFilePath = os.path.join(markerData['curTurbinePicFolderPath'],markerData['bladeName'],refMetaFileName)
    curMetaData = utilInstance.fileToJson(curMetaFilePath)


    marker = PairMarker(markerData, refMetaData, curMetaData, pathIndex)
    marker.mark()
    print("markerData")
    print(markerData)
    utilInstance.jsonToFile(markerData,curMarkDataJsonFilePath)



