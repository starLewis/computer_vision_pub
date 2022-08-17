# -*- coding: utf-8 -*-
#!/usr/bin/env python
import cv2
import numpy as np
import math

class SNR:
    def __init__(self):
        return
    
    def getMeanY(self,yImg):
        height, width = yImg.shape
        sum = 0
        cnt = 0
        for x in range(width):
            for y in range(height):
                sum += int(yImg[y][x])
                cnt += 1
        
        if cnt <= 0:
            return sum
        else:
            return sum * 1.0 / cnt

    def getStandardDev(self, yImg):
        varianceValue = self.getVariance(yImg)

        return np.sqrt(varianceValue)
        
    def getVariance(self, yImg):
        height, width = yImg.shape
        meanY = self.getMeanY(yImg)
        subSum = 0
        cnt = 0
        for x in range(width):
            for y in range(height):
                sub = int(yImg[y][x]) - meanY
                subSum += (sub * sub)
                cnt += 1
        
        if cnt <= 0:
            return subSum
        else:
            return subSum*1.0/cnt

    def getMeanSumOfSquares(self, yImg):
        height, width = yImg.shape
        squreSum = 0
        cnt = 0
        for x in range(width):
            for y in range(height):
                squreSum += (int(yImg[y][x]) * int(yImg[y][x]))
                cnt += 1
        
        if cnt <= 0:
            return squreSum
        else:
            return squreSum * 1.0 / cnt

    def getMaxValue(self, yImg):
        height, width = yImg.shape
        maxValue = 0
        for x in range(width):
            for y in range(height):
                if maxValue < yImg[y][x]:
                    maxValue = yImg[y][x]

        return maxValue
        
    def calculateSNRByItSelf(self, img):
        yuvImg = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        yImg, uImg, vImg = cv2.split(yuvImg)
        yMean = self.getMeanY(yImg)
        yStandDev = self.getStandardDev(yImg)

        if yStandDev <= 0:
            return 0
        else:
            return yMean * 1.0 / yStandDev


    def calculateSNRByBackground(self, img, backImg):
        yuvImg = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
        yuvBackImg = cv2.cvtColor(backImg, cv2.COLOR_BGR2YUV)

        yImg, uImg, vImg = cv2.split(yuvImg)
        yBackImg, uBackImg, vBackImg = cv2.split(yuvBackImg)

        meanSumSquaresOfImg = self.getMeanSumOfSquares(yImg)
        varianceOfBackImg = self.getVariance(yBackImg)

        if varianceOfBackImg <= 0:
            return 0
        else:
            return 10*math.log10(meanSumSquaresOfImg * 1.0 / varianceOfBackImg)

    def calculatePSNRByBackground(self, img, backImg):
        yuvImg = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)

        yImg, uImg, vImg = cv2.split(yuvImg)

        meanSumSquaresOfImg = self.getMeanSumOfSquares(yImg)
        snr = self.calculateSNRByItSelf(img)
        subSnr = 10*math.log10(255*255*1.0/meanSumSquaresOfImg)
        return (snr + subSnr)