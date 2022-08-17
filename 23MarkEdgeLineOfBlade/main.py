# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import json
import os
import cv2
import copy

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

    #* find all targetFilesPaths from one folderPath
    def findTargetFilesInOneFolder(self, folderPath, targetFilesRelativePaths):
        targetFilesPaths = []
        for targetFileRelativePath in targetFilesRelativePaths:
            targetFileAbsolutePath = os.path.join(folderPath, targetFileRelativePath)
            if os.path.exists(targetFileAbsolutePath):
                targetFilesPaths.append(targetFileAbsolutePath)

        return targetFilesPaths

class MouseOP:
    def __init__(self):
        self.curLineIndex = 0
        self.curLine = {"x1":0.1, "y1":0.1, "x2":0.2, "y2":0.2}
        self.twoLines = {"l1":None,"l2":None}
        self.imgWindowName = 'image'
        self.drawing = False
        self.ix = 0
        self.iy = 0
        self.px = 0
        self.py = 0

        self.imgPath = None
        self.img = None
        self.imgWidth = 1
        self.imgHeight = 1

        cv2.namedWindow(self.imgWindowName)
        cv2.setMouseCallback(self.imgWindowName, self.drawTwoLine)

    #* define mouse event
    def drawTwoLine(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix,self.iy = x,y
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing == True:
                # cv2.line(self.img,(self.ix,self.iy),(self.px,self.py),(0,0,0),0)
                # cv2.line(self.img,(self.ix,self.iy),(x,y),(0,255,0),1)
                self.px,self.py = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            cv2.line(self.img,(self.ix,self.iy),(x,y),(0,255,0),2)
            cv2.putText(self.img,str(self.curLineIndex), (self.ix, self.iy), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 2)
            self.px = -1
            self.py = -1
            self.curLine={"x1":1.0*self.ix/self.imgWidth, "y1":1.0*self.iy/self.imgHeight,"x2":1.0*x/self.imgWidth,"y2":1.0*y/self.imgHeight}
            if self.curLineIndex == 0:
                self.twoLines["l1"] = self.curLine
            elif self.curLineIndex == 1:
                self.twoLines["l2"] = self.curLine
            else:
                print("warn: draw more than 2 lines!")
            self.curLineIndex += 1
            
    def showImg(self,imgPath):
        self.imgPath = imgPath
        self.img = cv2.imread(imgPath)
        self.img = cv2.resize(self.img,(self.img.shape[1]/4, self.img.shape[0]/4), interpolation=cv2.INTER_CUBIC)
        self.imgHeight = self.img.shape[0]
        self.imgWidth = self.img.shape[1]
        print(self.imgHeight, self.imgWidth)
        
        while(1):
            cv2.imshow(self.imgWindowName,self.img)
            key = cv2.waitKey(1)&0xFF
            if key == ord('s') or key == ord('S') or key == 27:
                self.curLineIndex = 0
                #* return json data to file
                return self.twoLines
            elif key == ord('u') or key == ord('U'):
                self.curLineIndex = 0
                self.showImg(self.imgPath)
            # else:
                # print("wrong Key!")
    
    def showImgWithEdgeLines(self,imgPath,edgeLines):
        self.imgPath = imgPath
        self.img = cv2.imread(imgPath)
        self.img = cv2.resize(self.img,(self.img.shape[1]/4, self.img.shape[0]/4), interpolation=cv2.INTER_CUBIC)
        self.imgHeight = self.img.shape[0]
        self.imgWidth = self.img.shape[1]

        #* drone line l1
        cv2.line(self.img,((int)(edgeLines["l1"]["x1"]*self.imgWidth),(int)(edgeLines["l1"]["y1"]*self.imgHeight)),((int)(edgeLines["l1"]["x2"]*self.imgWidth),(int)(edgeLines["l1"]["y2"]*self.imgHeight)),(255,0,0),3)
        cv2.putText(self.img,str(0), ((int)(edgeLines["l1"]["x1"]*self.imgWidth),(int)(edgeLines["l1"]["y1"]*self.imgHeight)), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 2)
  
        #* drone line l2
        cv2.line(self.img,((int)(edgeLines["l2"]["x1"]*self.imgWidth),(int)(edgeLines["l2"]["y1"]*self.imgHeight)),((int)(edgeLines["l2"]["x2"]*self.imgWidth),(int)(edgeLines["l2"]["y2"]*self.imgHeight)),(255,0,0),3)
        cv2.putText(self.img,str(1), ((int)(edgeLines["l2"]["x1"]*self.imgWidth),(int)(edgeLines["l2"]["y1"]*self.imgHeight)), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 2)

        cv2.imshow(self.imgWindowName,self.img)
        cv2.waitKey(1)


if __name__ == '__main__':
    #* set target folder for get metadata's json
    folderPath = "/home/lewisliu/Clobotics/Codes/Wind/WindProc/wiProc/data/wiData/samples/SGRE_02"
    targetFilesRelativePaths = ["Metadata/A/blade_A_picsMetdata.json","Metadata/B/blade_B_picsMetdata.json","Metadata/C/blade_C_picsMetdata.json"]
    # tmpPath = "/home/lewisliu/Clobotics/Codes/Wind/WindProc/wiProc/data/wiData/samples/SGRE_02/Metadata/A/blade_A_picsMetdata_tmp.json"

    utilInstance = Util()
    mouseOp = MouseOP()

    targetFilesPaths = utilInstance.findTargetFilesInOneFolder(folderPath, targetFilesRelativePaths)
    for targetFilePath in targetFilesPaths:
        jsonData = utilInstance.fileToJson(targetFilePath)
        bladeIndex = 0
        while bladeIndex < len(jsonData):
            imgIndex = 0
            while imgIndex < len(jsonData[bladeIndex]["imgs"]):
                if "bladeEdgeLines" in jsonData[bladeIndex]['imgs'][imgIndex]:
                    #*  has "bladeEdgeLines", then show
                    mouseOp.showImgWithEdgeLines(jsonData[bladeIndex]['imgs'][imgIndex]['imgPath'],jsonData[bladeIndex]['imgs'][imgIndex]['bladeEdgeLines'])
                else:
                    #* draw two line for each img and store it to imgInfo
                    twoLine = mouseOp.showImg(jsonData[bladeIndex]['imgs'][imgIndex]['imgPath'])
                    # print(twoLine)
                    jsonData[bladeIndex]['imgs'][imgIndex]['bladeEdgeLines'] = copy.copy(twoLine)
                    
                    # print(bladeIndex, imgIndex, jsonData[bladeIndex]['imgs'][imgIndex]['bladeEdgeLines'])
                    #* store result
                    # print(targetFilePath)
                    utilInstance.jsonToFile(jsonData,targetFilePath)

                imgIndex += 1
            bladeIndex += 1
