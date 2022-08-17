# -*- coding: utf-8 -*-
#!/usr/bin/env python

import numpy as np
import cv2
import os

img = np.ones((1000, 1800, 3), np.uint8)

ix, iy = -1, -1

writeX = 1520
writeY = 20

def markPoint(event, x, y, flags, param):
    global ix, iy, writeX, writeY

    if event == cv2.EVENT_LBUTTONDOWN:
        ix, iy = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        xPosRatio = 1.0 * ix / 1500
        yPosRatio = 1.0 * iy / 1000

        rectName = "x, y:" + str(ix) + " " + str(iy)
        cv2.putText(img, rectName, (writeX, writeY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        writeY += 20

        rectName = "xRatio, yRatio:%.3f, %.3f\r\n"%(xPosRatio, yPosRatio)
        cv2.putText(img, rectName, (writeX, writeY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        writeY += 20

if __name__ == "__main__":
    # cv2.namedWindow('image')
    # cv2.setMouseCallback('image', markPoint)

    originImgPath = "/home/lewisliu/Clobotics/Data/CvDataOwnCloud/AutoFlight/TurbineData/SGRE/TurbineData/75_B16_20190807T161816/20190807T161816/picture/C/1_SS_LE_View/DSC05534.JPG"
    # originImgPath = "/home/lewisliu/Clobotics/Data/CvDataOwnCloud/AutoFlight/TurbineData/SGRE/TurbineData/11_M14_20190711T093810/20190711T101647/picture/C/4_PS_LE_View/DSC06061.JPG"
    imgName = originImgPath.split('/')[-1]
    originImg = cv2.imread(originImgPath)
    originImg = cv2.resize(originImg, (1500, 1000), 0.5, 0.5, cv2.INTER_CUBIC)
    img[0:1000, 0:1500] = originImg

    cv2.namedWindow(imgName)
    cv2.setMouseCallback(imgName, markPoint)

    while(1):
        cv2. imshow(imgName, img)
        k = cv2.waitKey(1) & 0xFF

        if k == ord('q'):
            break
        elif k == 27:
            break

    cv2.destroyAllWindows()