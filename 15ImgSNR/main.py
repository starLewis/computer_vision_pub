# -*- coding: utf-8 -*-
#!/usr/bin/env python

import numpy as np
import cv2
from snr import SNR

drawing = False
mode = True
ix, iy = -1, -1
px, py = -1, -1
img = np.ones((1000, 1800, 3), np.uint8)

snrOp = SNR()

backImg = None
isNowBackImg = False
rectNum = 1
writeX = 1520
writeY = 20

def draw_rect(event, x, y, flags, param):
    global ix, iy, drawing, px, py
    global backImg
    global isNowBackImg, rectNum
    global writeX, writeY

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix,iy = x,y
    elif event == cv2.EVENT_MOUSEMOVE:
        # if drawing == True:
            # cv2.rectangle(img, (ix, iy), (px, py), (0,0,0),0)
            # cv2.rectangle(img, (ix, iy), (x, y), (0,255,0),0)
        px,py = x,y
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False

        #* draw forground rect and background rect with different Color
        if isNowBackImg:
            cv2.rectangle(img, (ix, iy), (x, y), (0,0,0),0)
            backImg = img[iy:y, ix:x]
            rectName = "b: rect_0"
            cv2.putText(img,rectName, (ix, iy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 1)
        elif backImg is not None:
            cv2.rectangle(img, (ix, iy), (x, y), (0,255,0),0)
            rectName = "f: rect_" + str(rectNum)        
            cv2.putText(img,rectName, (ix, iy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1)
            
            rectImgSNR = snrOp.calculateSNRByItSelf(img[iy:y,ix:x])
            rectImgSNRByBack = snrOp.calculateSNRByBackground(img[iy:y,ix:x],backImg)
            rectImgPSNRByBack = snrOp.calculatePSNRByBackground(img[iy:y,ix:x],backImg)

            cv2.putText(img,rectName, (writeX, writeY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1)
            writeY += 20
            curTxt = ("SNR: %.2f db"%rectImgSNR)
            print curTxt
            cv2.putText(img,curTxt, (writeX, writeY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1)
            writeY += 20
            curTxt = ("PSNR: %.2f db"%rectImgPSNRByBack)
            print curTxt
            cv2.putText(img,curTxt, (writeX, writeY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1)
            writeY += 30
            # curTxt = ("SNRByBack: %.2f db"%rectImgSNRByBack)
            # print curTxt
            # cv2.putText(img,curTxt, (writeX, writeY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1)
            # writeY += 20

            rectNum += 1

        px,py = -1,-1
        # 

if __name__ == '__main__':

    cv2.namedWindow('image')
    cv2.setMouseCallback('image', draw_rect)

    originImgPath = "/media/lewisliu/HDD/Clobotics/WindPower/ae/psnr/ISO100/Fine/DSC09746.JPG"
    lenstr = len(originImgPath)
    saveImgPath = originImgPath[0:lenstr-4] + "_SNR_PSNR.jpg"

    originImg = cv2.imread(originImgPath)
    originImg = cv2.resize(originImg, (1500, 1000), 0.5, 0.5, cv2.INTER_CUBIC)
    img[0:1000, 0:1500] = originImg

    originImgSNR = snrOp.calculateSNRByItSelf(originImg)
    print originImgSNR

    while(1):
        cv2.imshow('image', img)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        elif k == 27: 
            break
        elif k == ord('b'):
            isNowBackImg = True
            print "isNowBackImg: " + str(isNowBackImg)
        elif k == ord('f'):
            isNowBackImg = False
            print "isNowBackImg: " + str(isNowBackImg)
        elif k == ord('s'):
            cv2.imwrite(saveImgPath,img)
            break

    cv2.destroyAllWindows()