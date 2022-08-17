#-*- coding: utf-8 -*-
import cv2
import numpy as np
import os

class MouseOp:
    def __init__(self,imgPath,storeImgPath):
        self.imgPath = imgPath
        self.storeImgPath = storeImgPath
        self.img = None
        self.points = []
        self.poly = []
        self.imgWindowName = "mask"

        cv2.namedWindow(self.imgWindowName)
        cv2.setMouseCallback(self.imgWindowName,self.mouseEvent)


    def mouseEvent(self,event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONUP:
            self.points.append([int(x), int(y)])
            print(self.points)
            self.poly = []
            self.poly.append(self.points)

    def extendRootFlange(self):
        self.img = cv2.imread(self.imgPath)
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        cv2.imshow("original", self.img)
        while(1):
            cv2.imshow(self.imgWindowName, self.img)

            #* draw poly and fill it
            # print self.poly
            cv2.polylines(self.img, np.array(self.poly), 1, 255)
            cv2.fillPoly(self.img, np.array(self.poly), 0)

            k = cv2.waitKey(30) & 0xFF
            if k == ord('u'):
                self.points = []
                self.img = cv2.imread(self.imgPath)
            elif k == ord('q'):
                break
            elif k == ord('s'):
                cv2.imwrite(self.storeImgPath, self.img)
        
if __name__ == "__main__":
    imgPath = "/home/lewisliu/Clobotics/Codes/Wind/WindProc/wiProc/data/wiData/samples/B16/i2/imgs_s/A/4_SS_LE_View/maskFolder/DSC05845.png"
    storeImgPath = "/home/lewisliu/Clobotics/Codes/Wind/WindProc/wiProc/data/wiData/samples/B16/i2/imgs_s/A/4_SS_LE_View/maskFolder/DSC05845_1.png"
    mouseOp = MouseOp(imgPath, storeImgPath)
    mouseOp.extendRootFlange()