# -*- coding: utf-8 -*-
import os
import time
import sys
import json
import numpy as np
import cv2
import math
import base64
import traceback
import copy
from concurrent import futures
from util import Util
import random
import pickle
from scipy.ndimage.filters import gaussian_filter
from logInfo import Logger
import tensorflow as tf

# log = Logger('all.log',level='debug')
# log = Logger('all.log',level='info')
log = Logger('all.log',level='warning')

configData = Util().fileToJson("config.json")

#* standard image size
STANDARDIMGWIDTH = configData['standardImgWidth']
STANDARDIMGHEIGHT = configData['standardImgHeight']
K_IMG_WIDTH = 640
K_IMG_HEIGHT = 426
K_PIX_PER_METER = 300 #* from 3D part
MINFEATNUM = configData['minFeatNum']

BLADELENTH = configData['bladeLen']

debug = False
# debug = True
debugShowImg = False
debugShowImg = True
debugShowImgDetails = False
debugShowImgDetails = True
index = 0

MINITRAINGRATIO = 0.005
# TRAININGRATIO = configData['trainingRatio']
MAXITERATIONS = configData['maxIteratons']
INF = 1000000
MAXITERATIONNUMFORSINGLEIMG = 1000

BLADEROOTLIDAR = 14.0
BLADETIPLIDAR = 8.0
LIDAROTSUTHRESHOLD = (BLADEROOTLIDAR+BLADETIPLIDAR)/2

temp = 0

gradientMethod = {
    "all": "all",
    "bladeLen": "bladeLen",
    "bladeLenGDirect":"bladeLenGDirect",
    "bladeLenGValue":"bladeLenGValue"
}

GradientParamMethod = {
    "all": "all",
    "x": "x",
    "y": "y",
    "rotation": "rotation",
    "xy": "xy",
    "xRotation": "xRotation",
    "yRotation": "yRotation"
}

optimizataionStatus = {
    "init":"init",
    "localGradient":"localGradient",
    "lenthGradient":"lenthGradient",
    "imgsGapGradient":"imgsGapGradient",
    "globalGradient":"globalGradient"
}

bldErrorRange = {
    "allPath":"allPath",
    "1stHalfPath":"1stHalfPath",
    "2ndHalfPath":"2ndHalfPath"
}

debugInterIndex = -1

class Stitcher:
    def __init__(self, originalData, bladeIndex, pathIndex, rootTipMarkerData):
        #* input data
        if debugInterIndex >= 0:
            output = open("originData.pkl", "rb")
            self.originalData = pickle.load(output)
            output.close

            output = open("curData_"+str(debugInterIndex) + "_.pkl", "rb")
            self.curData = pickle.load(output)
            output.close
        else:
            self.originalData = copy.deepcopy(originalData)
            self.curData = copy.deepcopy(originalData)

        #* for inital position
        self.initOriginalData = copy.deepcopy(originalData)

        #* adjust image rotation by blade fitted line
        self.bladeLineAngleDataInImg = []
        self.bladeLineAngleDataInPanorama = []

        #* this is to record cur data after local error descent and blade lenth error descent
        self.curDataBeforeAllGD = copy.deepcopy(originalData)

        self.numData = len(self.curData)
        self.bladeIndex = bladeIndex
        self.pathIndex = pathIndex
        self.rootTipMarkerData = rootTipMarkerData

        self.curBladeRootPT = [0,0]
        self.curBladeTipPT = [0,0]

        self.originalTipToRootD = self.calOriginalRootToTipD()

        #* current image(s) for gradient, if value < 0 , then do gradient descent for all images, if value >= 0 , do the value_th image
        if debugInterIndex > 0:
            self.curGradientImgIndex = debugInterIndex - 1
        else:
            self.curGradientImgIndex = -1
        self.curImgIterationNum = 0
        self.curBndBoxRef = None
        self.curBndBoxCur = None

        #* training ratio
        self.trainingRatio = configData['trainingRatio']
        self.convergedNum = 0

        #* optimization status
        self.optStatus = optimizataionStatus['init']
        self.isBladeB = (abs(self.curData[0]['tf']['rotation']) < 210 and abs(self.curData[0]['tf']['rotation']) > 150) or (abs(self.curData[0]['tf']['rotation']) < 30)
        #* for imgsGapDistance error optimization
        self.targetImgsGap = np.zeros(self.numData)
        self.curImgsGap = np.zeros(self.numData)
        self.curImgsCenterPt = np.zeros((self.numData, 2))
        self.targetImgsCenterYAfterGapsSmooth = np.zeros(self.numData)

        #* find the two switcher images
        self.switcherImgIndex = -1
        self.findSwitcherImgs()
        self.firstHalfPathTargetLen = 0
        self.secondHalfPathTargetLen = 0
        # Util().jsonToFile("curDataRes.json", self.curData[])
        # log.logger.debug(self.curData[0])

        #* adjust sawtooth
        self.curEdge4Points = []

        #* output data
        self.panormamaImg = None
        self.panoTx = 0
        self.panoTy = 0
        self.panoWidth = 0
        self.panoHeight = 0
        self.averageOverLap = 0
        self.eachMaskImgToPano = [None for i in range(self.numData)]
        self.overlapArr = [0 for i in range(self.numData)]

        self.gradient = self.initGradientVect()
        self.maxScaleStep = 0.1*self.trainingRatio
        self.maxRotationStep = 0.5*self.trainingRatio
        self.maxTransferStep = 3*self.trainingRatio
        self.curLoss = 0

        self.preImgOverlapRatio = 0.5

        self.curShapeMatchError = 0
        self.curOrbDisError = 0
        self.curOverlapError = 0
        self.curBladeLengthError = 0
        self.curImgsGapError = 0
        
        #* debug
        self.showPanoramaImgIndex = 0
        self.keyPTs = []
        # Util().jsonToFile("origindata.json", self.originalData)
        # output = open('originData.pkl', 'wb')
        # pickle.dump( self.originalData, output)
        # output.close

        log.logger.info("****************A new stitcher instance****************")

    '''
    find lidar distance swither images, two continous images, one's lidar is 14m(now) and other is 8m, or one is 8m and other is 14m
    '''
    def findSwitcherImgs(self):
        for i in range(self.numData):
            self.curData[i]['isSwitcherImg'] = False
            self.originalData[i]['isSwitcherImg'] = False
            if i > 0 and self.curData[i-1]['lidar'] > LIDAROTSUTHRESHOLD and self.curData[i]['lidar'] < LIDAROTSUTHRESHOLD:
                self.curData[i-1]['isSwitcherImg'] = True
                self.curData[i]['isSwitcherImg'] = True
                self.originalData[i-1]['isSwitcherImg'] = True
                self.originalData[i]['isSwitcherImg'] = True
                self.switcherImgIndex = i
                log.logger.info("switcherImgIndex: %d"%self.switcherImgIndex)

        #* here, it is better we use smooth array to find switcher images, as OTSU idea

    def getPanoramaImg(self):
        res = self.panormamaImg.copy()
        return res

    def getPanoramaOffset(self):
        return [self.panoTx, self.panoTy]

    # def updateImgSizeByTFInfo(self):
        # for curImgInfo in self.curData:

    def resetTrainingRatio(self):
        self.trainingRatio = configData['trainingRatio']
        self.updateTrainingStep()

    def isConveraged(self, preLoss, curLoss, curIter, miniGapValue, iterNumThreshold = 10):
        if preLoss <= curLoss:
            self.trainingRatio = max(self.trainingRatio/2, MINITRAINGRATIO)
            self.updateTrainingStep()
        
        if self.convergedNum < 0 and curLoss <= preLoss and curLoss > 10 and (preLoss - curLoss)*100 < curLoss:
            self.trainingRatio = min(self.trainingRatio*2, configData['maxTrainingRatio'])
            self.updateTrainingStep()

        if curIter <= iterNumThreshold:
            self.convergedNum = -1
            return False
        else:
            if preLoss <= curLoss and self.convergedNum < 0:
                self.convergedNum = 0
            if (abs(preLoss - curLoss) < miniGapValue or preLoss <= curLoss) and self.convergedNum >= 0:
                self.convergedNum += 1
                # log.logger.debug("convergedNum: %d"%self.convergedNum)
                if self.convergedNum > iterNumThreshold:
                    return True
        return False

    def updateTrainingStep(self):
        self.maxScaleStep = 0.1*self.trainingRatio
        self.maxRotationStep = 0.5*self.trainingRatio
        self.maxTransferStep = 3*self.trainingRatio
        log.logger.info("trainingRatio: %.4f"%self.trainingRatio)

    def calOriginalRootToTipD(self):
        if self.numData <= 0:
            return 0
        # dx = self.originalData[self.numData - 1]['tf']['x'] - self.originalData[0]['tf']['x']
        # dy = self.originalData[self.numData - 1]['tf']['y'] - self.originalData[0]['tf']['y']
        # originalD = np.sqrt(dx*dx + dy*dy)
        
        #* fix blade length by 34m
        originalD = BLADELENTH * K_PIX_PER_METER * STANDARDIMGWIDTH / K_IMG_WIDTH
        log.logger.info("bladeLength original: %.3f"%originalD)
        return originalD

    def initGradientVect(self):
        grd = []
        for i in range(self.numData):
            grd.append({"scale":0.0, "rotation":0.0, "x": 0.0, "y": 0.0})
        return grd

    #* merge cur panorama image to self.panorama image
    def transparentMerge(self, panoramaImg, curWarpImg, curWarpMaskImg, useTransparent = True):        
        tmp = panoramaImg.copy()
        tmp[tmp == 0] = 0
        tmp[curWarpImg == 0] = 0

        if useTransparent:
            panoramaImg[tmp != 0] = 0.5*tmp[tmp!=0] + 0.5*curWarpImg[tmp != 0]
        else:
            panoramaImg[tmp != 0] = curWarpImg[tmp != 0]
        curWarpImg[tmp != 0] = 0
        panoramaImg[curWarpImg != 0] = curWarpImg[curWarpImg != 0]

        return panoramaImg

    #* calculate curBladeInRefImg, refBladeInCurImg, and intersection of two blades
    def calShapeIntersectionOfImgI(self, i):
        if i <= 0:
            return 1, 1, 1
        refImgInfo = self.curData[i-1]
        curImgInfo = self.curData[i]

        refMaskImg = refImgInfo['mask']
        curMaskImg = curImgInfo['mask']

        refTF = copy.deepcopy(refImgInfo['tf'])
        refTF['x'] += self.panoTx
        refTF['y'] += self.panoTy
        refM = self.T2M(refTF)
        curTF = copy.deepcopy(curImgInfo['tf'])
        curTF['x'] += self.panoTx
        curTF['y'] += self.panoTy
        curM = self.T2M(curTF)

        refRect = np.full((int(refImgInfo['tf']['imgHeight']), int(refImgInfo['tf']['imgWidth'])), 255, np.uint8)
        curRect = np.full((int(curImgInfo['tf']['imgHeight']), int(curImgInfo['tf']['imgWidth'])), 255, np.uint8)

        #* refMask img in panorama
        refMaskImgInPanorama = cv2.warpPerspective(refMaskImg, refM, (self.panoWidth, self.panoHeight))
        #* ref rect in panorama
        refRectImgInPanorama = cv2.warpPerspective(refRect, refM, (self.panoWidth, self.panoHeight))
        #* cur mask img in panorama
        curMaskImgInPanorama = cv2.warpPerspective(curMaskImg, curM, (self.panoWidth, self.panoHeight))
        #* cur rect in panorama
        curRectImgInPanorama = cv2.warpPerspective(curRect, curM, (self.panoWidth, self.panoHeight))

        #* cur blade in ref image
        curBladeInRefImg = refRectImgInPanorama.copy()
        curBladeInRefImg[curMaskImgInPanorama == 0] = 0
        curBladeInRefImgArea = cv2.countNonZero(curBladeInRefImg)

        #* ref blade in cur image
        refBladeInCurImg = curRectImgInPanorama.copy()
        refBladeInCurImg[refMaskImgInPanorama == 0] = 0
        refBladeInCurImgArea = cv2.countNonZero(refBladeInCurImg)

        #* intersection of cur blade and ref blade
        intersectionImg = refMaskImgInPanorama.copy()
        intersectionImg[curMaskImgInPanorama == 0] = 0
        intersectionArea = cv2.countNonZero(intersectionImg)

        return curBladeInRefImgArea, refBladeInCurImgArea, intersectionArea

    #* calculate curBladeInRefImg, refBladeInCurImg, and intersection of two blades by relative tf matrix
    def calShapeIntersectionOfImgI_quick(self, i):
        if i <= 0:
            return 1, 1, 1

        refImgInfo = self.curData[i-1]
        curImgInfo = self.curData[i]
        refMaskImg = refImgInfo['mask']
        curMaskImg = curImgInfo['mask']

        # imgStoreName = "refMaskImg_" + str(i) + ".jpg"
        # cv2.imwrite(imgStoreName, refMaskImg)
        # imgStoreName = "curMaskImg" + str(i) + ".jpg"
        # cv2.imwrite(imgStoreName, curMaskImg)

        #* Elimiate boundary
        cv2.line(refMaskImg, (int(refImgInfo['tf']['imgWidth']), 0), (int(refImgInfo['tf']['imgWidth']), int(refImgInfo['tf']['imgHeight'])), 0, 10)
        cv2.line(refMaskImg, (0, int(refImgInfo['tf']['imgHeight'])), (0, 0), 0, 10)
        cv2.line(curMaskImg, (int(curImgInfo['tf']['imgWidth']), 0), (int(curImgInfo['tf']['imgWidth']), int(curImgInfo['tf']['imgHeight'])), 0, 10)
        cv2.line(curMaskImg, (0, int(curImgInfo['tf']['imgHeight'])), (0, 0), 0, 10)

        #* calculate the relative transformation from reference image to current image
        refT = copy.deepcopy(refImgInfo['tf'])
        # refT['rotation'] = np.radians(refT['rotation'])
        curT = copy.deepcopy(curImgInfo['tf'])
        # curT['rotation'] = np.radians(curT['rotation'])

        refT['x'] += self.panoTx
        refT['y'] += self.panoTy
        curT['x'] += self.panoTx
        curT['y'] += self.panoTy

        refM = self.T2M(refT)
        curM = self.T2M(curT)
        relM = refM.I * curM
        relTF = self.M2T(relM)
        # log.logger.debug("scale:%.3f, rotation:%.3f,x:%.3f,y:%.3f"%(relTF['scale'], relTF['rotation'], relTF['x'], relTF['y']))
        # log.logger.debug("tf:", self.M2T(relM))
        # log.logger.debug("curTf:", curImgInfo['tf'])
        # log.logger.debug("refTF:", refImgInfo['tf'])

        #* current blade in reference image
        # maskCurBladeInRef = cv2.warpPerspective(curMaskImg, relM, (STANDARDIMGWIDTH, STANDARDIMGHEIGHT))
        maskCurBladeInRef = cv2.warpPerspective(curMaskImg, relM, (int(refImgInfo['tf']['imgWidth']), int(refImgInfo['tf']['imgHeight'])))
        areaCurBladeInRefImg = cv2.countNonZero(maskCurBladeInRef)
        # if areaCurBladeInRefImg == 0:
            # return INF + abs(refImgInfo['tf']['x'] - curImgInfo['tf']['x'])

        # imgStoreName = "maskCurBladeInRef_" + str(i) +"_.jpg"
        # cv2.imwrite(imgStoreName, maskCurBladeInRef)

        #* Reference blade in current image
        maskRefBladeInCur = refMaskImg.copy()
        # rect = np.full((STANDARDIMGHEIGHT, STANDARDIMGWIDTH), 255, np.uint8)
        # rectCur = cv2.warpPerspective(rect, relM, (STANDARDIMGWIDTH, STANDARDIMGHEIGHT))
        rect = np.full((int(curImgInfo['tf']['imgHeight']), int(curImgInfo['tf']['imgWidth'])), 255, np.uint8)
        rectCur = cv2.warpPerspective(rect, relM, (int(refImgInfo['tf']['imgWidth']), int(refImgInfo['tf']['imgHeight'])))
        rect = None
        maskRefBladeInCur[rectCur == 0] = 0
        rectCur = None
        areaRefBladeInCurImg = cv2.countNonZero(maskRefBladeInCur)
        # if areaRefBladeInCurImg == 0:
            # return INF + abs(refImgInfo['tf']['x'] - curImgInfo['tf']['x'])

        # imgStoreName = "maskRefBladeInCur_" + str(i) + "_.jpg"
        # cv2.imwrite(imgStoreName, maskRefBladeInCur)

        #* Find intersection
        maskIntersect = maskRefBladeInCur.copy()
        maskIntersect[maskCurBladeInRef == 0] = 0
        areaIntersect = cv2.countNonZero(maskIntersect)
        # if areaIntersect == 0:
            # return INF + abs(refImgInfo['tf']['x'] - curImgInfo['tf']['x'])

        return areaCurBladeInRefImg, areaRefBladeInCurImg, areaIntersect

    #* build panorama img and show it from images group with tf info
    def showPanoramaImg(self,isCurData=True, curLoss = 666, isStorePanorama = False):
        panoData = self.curData
        # if not isCurData:
            # panoData = self.originalData

        #* calculate the panorama image of 
        if self.panoWidth <= 0 or self.panoHeight <= 0 or self.optStatus == optimizataionStatus['localGradient'] or self.optStatus == optimizataionStatus['lenthGradient']:
            panoRect = {'left':0.0, 'right':1.0 * STANDARDIMGWIDTH, 'top':0.0, 'bottom':1.0 * STANDARDIMGHEIGHT}
            #* find pano size
            # rect = [[0.0, 0.0], [1.0*STANDARDIMGWIDTH, 1.0*STANDARDIMGHEIGHT],[1.0*STANDARDIMGWIDTH, 0], [0, 1.0*STANDARDIMGHEIGHT]]

            for imgInfo in panoData:
                cos = math.cos(math.radians(imgInfo['tf']['rotation']))
                sin = math.sin(math.radians(imgInfo['tf']['rotation']))
                s = imgInfo['tf']['scale']
                tx = imgInfo['tf']['x']
                ty = imgInfo['tf']['y']
                rect = [[0.0, 0.0], [1.0*imgInfo['tf']['imgWidth'], 1.0*imgInfo['tf']['imgHeight']],[1.0*imgInfo['tf']['imgWidth'], 0], [0, 1.0*imgInfo['tf']['imgHeight']]]

                for pt in rect:
                    x = s * (pt[0]*cos - pt[1]*sin) + tx
                    y = s * (pt[0]*sin + pt[1]*cos) + ty
                    panoRect['left'] = min(panoRect['left'], x)
                    panoRect['right'] = max(panoRect['right'], x)
                    panoRect['top'] = min(panoRect['top'], y)
                    panoRect['bottom'] = max(panoRect['bottom'], y)

            #* Generate panorama
            self.panoWidth = int(math.ceil(panoRect['right'] - panoRect['left']) * 1.5)
            self.panoHeight = int(math.ceil(panoRect['bottom'] - panoRect['top'] + 2.0*K_PIX_PER_METER*STANDARDIMGWIDTH/K_IMG_WIDTH))
            memSize = 3.0 * self.panoWidth * self.panoHeight / 1024.0 / 1024.0 / 1024.0
            log.logger.info("Generating panorama (%d * %d pixel, %lf GB)."%(self.panoWidth, self.panoHeight,memSize))

            log.logger.info("panoRect left:%d, top:%d"%(panoRect['left'], panoRect['top']))
            # self.panoTx = -panoRect['left']
            # self.panoTy = -panoRect['top']
            self.panoTx = int(math.ceil(panoRect['right'] - panoRect['left'])*0.25) - panoRect['left']
            self.panoTy = -panoRect['top']

        self.panormamaImg = np.zeros((self.panoHeight, self.panoWidth, 3), np.uint8)
        for imgInfo in panoData:
            T = copy.deepcopy(imgInfo['tf'])
            # T['rotation'] = math.radians(T['rotation'])
            T['x'] += self.panoTx
            T['y'] += self.panoTy
            M = self.T2M(T)

            #* update imgSize and mask size
            # imgInfo['img'] = cv2.resize(imgInfo['img'], (int(imgInfo['tf']['imgWidth']), int(imgInfo['tf']['imgHeight'])), interpolation=cv2.INTER_CUBIC)
            # imgInfo['mask'] = cv2.resize(imgInfo['mask'], (int(imgInfo['tf']['imgWidth']), int(imgInfo['tf']['imgHeight'])), interpolation=cv2.INTER_CUBIC)

            # cv2.warpPerspective(imgInfo['img'], M, (self.panoWidth, self.panoHeight), self.panormamaImg, cv2.INTER_LINEAR, cv2.BORDER_TRANSPARENT)
            curWarpImg = cv2.warpPerspective(imgInfo['img'], M, (self.panoWidth, self.panoHeight))
            curWarpMaskImg = cv2.warpPerspective(imgInfo['mask'], M, (self.panoWidth, self.panoHeight))
            if debugShowImgDetails:
                self.panormamaImg = self.transparentMerge(self.panormamaImg, curWarpImg, curWarpMaskImg)
            else:
                self.panormamaImg = self.transparentMerge(self.panormamaImg, curWarpImg, curWarpMaskImg, False)

            if debug:
                log.logger.debug("imgName: %s, rotation: %.2f, scale: %.2f, x: %.2f, y: %.2f"%(imgInfo['imgName'], T['rotation'], T['scale'], T['x'], T['y']))
                cv2.circle(self.panormamaImg, (int(T['x'] ), int(T['y'] )), 5, (0,255,0), -1)

        # for imgInfo in panoData:
        if configData['storeMidPanoramaImg'] == True or isStorePanorama == True:
            imgName = "panoImg_blade_"+str(self.bladeIndex)+"_path_"+str(self.pathIndex)+"_"+str(self.showPanoramaImgIndex) + "_" + self.optStatus +"_.jpg"

            if debugShowImgDetails:
                try: 
                    if self.curGradientImgIndex > 0 and debugInterIndex <= 0:
                        # cv2.circle(self.panormamaImg,(int(self.curData[self.curGradientImgIndex]['tf']['x']+self.panoTx), int(self.curData[self.curGradientImgIndex]['tf']['y']+self.panoTy)), 15, (0, 0, 255), -1)
                        cv2.rectangle(self.panormamaImg,(self.curBndBoxRef[0] ,self.curBndBoxRef[1]), (self.curBndBoxRef[0] + self.curBndBoxRef[2], self.curBndBoxRef[1] + self.curBndBoxRef[3]), (0, 255, 0),2)
                        cv2.rectangle(self.panormamaImg,(self.curBndBoxCur[0], self.curBndBoxCur[1]), (self.curBndBoxCur[0] + self.curBndBoxCur[2], self.curBndBoxCur[1] + self.curBndBoxCur[3]), (255, 0, 0),2)

                    #* show each image's index in panorama image
                    for imgIndex in range(self.numData):
                        #* calculate each image's zero point to blade root distance
                        curRootM = None
                        rootPTInImg = [self.rootTipMarkerData['rootMark']['px']['x']*self.curData[0]['tf']['imgWidth'], self.rootTipMarkerData['rootMark']['px']['y']*self.curData[0]['tf']['imgHeight']]
                        rootPTAfterTF = None
                        rootPTInImgArr = np.array([np.array([rootPTInImg])])
                        rootImgName = self.rootTipMarkerData['rootMark']['img']
                        for imgInfo in self.curData:
                            if imgInfo['imgName'].split('/')[-1] == rootImgName:
                                curRootM = copy.deepcopy(self.T2M(imgInfo['tf']))
                        rootPTAfterTF = cv2.perspectiveTransform(rootPTInImgArr, curRootM)
                        self.curBladeRootPT = [rootPTAfterTF[0][0][0] + self.panoTx,rootPTAfterTF[0][0][1] + self.panoTy]

                        # deltY = self.curData[imgIndex]['tf']['y'] - self.curData[0]['tf']['y']
                        deltY = self.curData[imgIndex]['tf']['y'] + self.panoTy - self.curBladeRootPT[1]
                        deltY /= (K_PIX_PER_METER * STANDARDIMGWIDTH / K_IMG_WIDTH)
                        # log.logger.debug("deltY: %.3f"%deltY)
                        deltY = "%.1f"%deltY
                        strTxt = str(imgIndex) + " (" + str(deltY) + ")"

                        cv2.putText(self.panormamaImg, strTxt, (int(self.curData[imgIndex]['tf']['x']+self.panoTx), int(self.curData[imgIndex]['tf']['y']+self.panoTy)), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 3)

                    #* draw blade root and blade tip
                    # cv2.circle(self.panormamaImg, (int(self.curData[self.numData-1]['tf']['x'] + self.panoTx), int(self.curData[self.numData-1]['tf']['y'] + self.panoTy)), 50, (255, 0, 0), -1)
                    # cv2.circle(self.panormamaImg, (int(self.curData[0]['tf']['x'] + self.panoTx), int(self.curData[0]['tf']['y'] + + self.panoTy)), 50, (255, 0, 0), -1)
                    cv2.circle(self.panormamaImg, (int(self.curBladeRootPT[0]),int(self.curBladeRootPT[1])), 30, (255, 0, 0), -1)
                    cv2.circle(self.panormamaImg, (int(self.curBladeTipPT[0]),int(self.curBladeTipPT[1])), 30, (255, 0, 0), -1)

                    cv2.circle(self.panormamaImg, (int(self.originalData[self.numData-1]['tf']['x'] + self.panoTx), int(self.originalData[self.numData-1]['tf']['y'] + self.panoTy)), 50, (0, 0, 255), -1)
                    cv2.circle(self.panormamaImg, (int(self.originalData[0]['tf']['x'] + self.panoTx), int(self.originalData[0]['tf']['y'] + + self.panoTy)), 50, (0, 0, 255), -1)
                except:
                    log.logger.error("showPanoramaImg => error!")

                for pt in self.keyPTs:
                    # cv2.circle(self.panormamaImg, (int(pt[1][0]), int(pt[1][1])), 5, (255,255,0), -1)
                    cv2.line(self.panormamaImg, (int(pt[0][0]), int(pt[0][1])), (int(pt[1][0]), int(pt[1][1])),
                        (int(random.random()*255), int(random.random()*255), int(random.random()*255)), 2)
            cv2.imwrite(imgName,self.panormamaImg)
            # Util().jsonToFile("curData_"+str(self.showPanoramaImgIndex) + "_.json", self.curData)

            # output = open("curData_"+str(self.showPanoramaImgIndex) + "_.pkl", 'wb')
            # pickle.dump(self.curData, output)
            # output.close
            self.showPanoramaImgIndex += 1

    '''
    optimize
    '''
    def optimize(self):
        Loss = self.calLoss()
        self.curLoss = Loss

        log.logger.warning("optimize bladeIndex: %d, pathIndex: %d"%(self.bladeIndex, self.pathIndex))
        #* adjust rotation by each image blade's fitted line
        # if self.bladeIndex != 1:
        beginTime = time.time()
        fromTime = time.time()
        self.adjustRotationByBladeFittedLine()
        log.logger.warning("adjustRotationByBladeFittedLine duration time: %.3f s"%(time.time() - fromTime))

        # * local error optimization
        # * local error only based on x adjustment
        fromTime = time.time()
        self.curGradientImgIndex = 0
        self.localErrorOptimize(GradientParamMethod['x'])
        log.logger.warning("localErrorOptimize x, duration time: %.3f s"%(time.time() - fromTime))

        fromTime = time.time()
        self.curGradientImgIndex = 0
        self.localErrorOptimize(GradientParamMethod['xy'])
        log.logger.warning("localErrorOptimize xy, duration time: %.3f s"%(time.time() - fromTime))
        #* local error based on all
        fromTime = time.time()
        self.curGradientImgIndex = 0
        self.localErrorOptimize()
        log.logger.warning("localErrorOptimize all, duration time: %.3f s"%(time.time() - fromTime))
        self.curGradientImgIndex = -1

        #* blade length error optimization
        fromTime = time.time()
        self.bldLenErrorOptimize(errorRange=bldErrorRange['1stHalfPath'])
        log.logger.warning("bldLenErrorOptimize 1stHalfPath, duration time: %.3f s"%(time.time() - fromTime))
        fromTime = time.time()
        self.bldLenErrorOptimize(errorRange=bldErrorRange['2ndHalfPath'])
        log.logger.warning("bldLenErrorOptimize 2ndHalfPath, duration time: %.3f s"%(time.time() - fromTime))
        # self.bldLenErrorOptimize()

        #* if cur loss >= INF, run local gradient and blade length descent again
        self.curLoss = self.calLoss()
        if self.curLoss >= INF/self.numData or self.curShapeMatchError >= 15:
            fromTime = time.time()
            #* local error gradient descent
            #* local error only based on x adjustment
            self.curGradientImgIndex = 0
            self.localErrorOptimize(GradientParamMethod['x'])
            #* local error based on all
            self.curGradientImgIndex = 0
            self.localErrorOptimize()

            #* blade length gradient descent
            self.bldLenErrorOptimize(errorRange=bldErrorRange['1stHalfPath'])
            self.bldLenErrorOptimize(errorRange=bldErrorRange['2ndHalfPath'])
            self.bldLenErrorOptimize()
            log.logger.warning("one more Local and BldLen optimize, duration time: %.3f s"%(time.time() - fromTime))


        #* imgs Gap error gradient descent
        fromTime = time.time()
        if configData['useImgsGapE']:
            if self.switcherImgIndex <= 0 or self.switcherImgIndex >= self.numData - 1:
                self.switcherImgIndex = self.numData
                self.imgsGapErrorOptimize(bldErrorRange['1stHalfPath'])
            else:
                self.imgsGapErrorOptimize(bldErrorRange['1stHalfPath'])
                self.imgsGapErrorOptimize(bldErrorRange['2ndHalfPath'])
        log.logger.warning("imgsGapErrorOptimize, duration time: %.3f s"%(time.time() - fromTime))

        #* sawtooth adjustment
        fromTime = time.time()
        self.sawToothAdjustment()
        log.logger.warning("sawToothAdjustment, duration time: %.3f s"%(time.time() - fromTime))

        #* global error gradient descent
        fromTime = time.time()
        self.globalErrorOptimize()
        log.logger.warning("globalErrorOptimize, duration time: %.3f s"%(time.time() - fromTime))
        log.logger.warning("total optimization duration time: %.3f mins"%((time.time() - beginTime)/60.0))



    '''
    optimize
    '''
    def myoptimize(self):
        Loss=self.calLoss()

    #* optimize images one by one and followed by following images
    def localErrorOptimize(self, gradientParamMethod = GradientParamMethod["all"]):
        #* local gradient descent
        self.resetTrainingRatio()
        self.optStatus = optimizataionStatus['localGradient']
        while self.curGradientImgIndex >= 0:
            curIter = 0
            self.curLoss = self.calLoss()
            # if self.curLoss != 0:
            self.adjustOverlap(self.curGradientImgIndex)
            # else:
            #     log.logger.info("optimize(%s) => imgIndex: %d optimized, curLoss: %.3f, orbError: %.3f, shapeError: %.3f."%(gradientParamMethod, self.curGradientImgIndex, self.curLoss, self.curOrbDisError, self.curShapeMatchError))
            #     self.curGradientImgIndex += 1
            #     if self.curGradientImgIndex >= self.numData:
            #         self.curGradientImgIndex = -1
            #     continue
            # self.adjustOverlap(self.curGradientImgIndex)
            self.curLoss = self.calLoss()
            preLoss = INF
            #* reset trainning ratio
            self.resetTrainingRatio()
            log.logger.info("optimize(%s) => imgIndex: %d optimizing.., curLoss: %.3f, orbError: %.3f, shapeError: %.3f."%(gradientParamMethod, self.curGradientImgIndex, self.curLoss, self.curOrbDisError, self.curShapeMatchError))
            while curIter <= MAXITERATIONNUMFORSINGLEIMG and self.curLoss > 0.5:
                gradient = self.calGradient(gradientParamMethod)
                self.gradDescent()
                self.curLoss = self.calLoss()
                curIter += 1
                # if curIter > 10 and preLoss == self.curLoss and self.curLoss <= 2.0:
                    # break
                if self.isConveraged(preLoss, self.curLoss, curIter, 0.05, 20):
                    break
                preLoss = self.curLoss

                # log.logger.debug("optimized,curLoss:%.3f, x:%d, y:%d, rotation: %.3f"%(self.curLoss, self.curData[self.curGradientImgIndex]['tf']['x'], self.curData[self.curGradientImgIndex]['tf']['y'], self.curData[self.curGradientImgIndex]['tf']['rotation']))

            log.logger.info("optimize(%s) => imgIndex: %d optimized, curLoss: %.3f, orbError: %.3f, shapeError: %.3f."%(gradientParamMethod, self.curGradientImgIndex, self.curLoss, self.curOrbDisError, self.curShapeMatchError))
            # if self.curLoss >= 5:
                # self.showPanoramaImg()
            self.showPanoramaImg()
            self.curGradientImgIndex += 1
            if self.curGradientImgIndex >= self.numData:
            # if self.curGradientImgIndex >= 10:
                self.curGradientImgIndex = -1

        self.showPanoramaImg(isStorePanorama=True)

    '''
    ' here, we divide blade to 2 parts, the first part includes images with 14m lidar distance, the second part includes images with 8m lidar distance
    '''
    def bldLenErrorOptimize(self, errorRange = bldErrorRange['allPath']):
        #* blade length gradient descent
        log.logger.info("bldLenErrorOptimize() => error range: %s"%errorRange)
        self.curLoss = self.calLoss(method=gradientMethod['bladeLenGDirect'], errorRange = errorRange)
        log.logger.info("bladeLenth, curLoss:%.3f"%self.curLoss)
        curIter = 0
        self.optStatus = optimizataionStatus['lenthGradient']
        preLoss = INF
        miniLoss = INF
        miniIter = -1
        self.trainingRatio = min(self.curLoss/self.numData, configData['trainingRatio'] * 3)
        self.trainingRatio = max(self.trainingRatio, configData['trainingRatio'])
        self.resetTrainingRatio()
        while (self.curLoss > 2 and curIter <= MAXITERATIONS * 10) or self.curLoss <= 2:
            fromTime = time.time()
            gradient = self.calGradientForLenError(errorRange)
            self.gradDescent(gradientMethod['bladeLenGDirect'])
            self.curLoss = self.calLoss(method=gradientMethod['bladeLenGDirect'], errorRange = errorRange)

            # if preLoss < self.curLoss:
            #     self.trainingRatio = max(self.trainingRatio/2, MINITRAINGRATIO)
            #     self.updateTrainingStep()

            if self.isConveraged(preLoss, self.curLoss, curIter, 0.5, 15):
                break

            if curIter > 10 and miniLoss > self.curLoss:
                miniLoss = self.curLoss
                miniIter = 0

            if miniIter >= 0:
                miniIter += 1
            if miniIter > 10:
                break

            duration = time.time() - fromTime

            curIter += 1
            preLoss = self.curLoss
            log.logger.info("duration time: %.3f s"%duration)
            log.logger.info("optimize(%s) => blade Lenth, iter:%d, curLoss:%.3f, orbError: %.3f, shapeError: %.3f, overlapError: %.3f, bldLenError: %.3f"%(errorRange, curIter, self.curLoss, self.curOrbDisError, self.curShapeMatchError, self.curOverlapError, self.curBladeLengthError))
            if curIter % (int)(configData['storePanoramPerImgs']) == 0:
                self.showPanoramaImg()
        self.showPanoramaImg(isStorePanorama=True)

    '''
    ImgsGapDistance error optimization
    '''
    def imgsGapErrorOptimize(self, errorRange):
        self.optStatus = optimizataionStatus['imgsGapGradient']
        #* calculate the target imgs Gap
        startIndex = 0
        stopIndex = self.switcherImgIndex

        if errorRange == bldErrorRange['2ndHalfPath']:
            startIndex = self.switcherImgIndex
            stopIndex = self.numData

        #* calculate imgs gap target firstly
        self.calImgsTargetCenterAfterGapSmooth(startIndex, stopIndex)

        log.logger.info("imgsGapErrorOptimize() => error range: %s"%errorRange)
        self.curLoss = self.calLoss(errorRange = errorRange)
        log.logger.info("imgsGap, curLoss: %.3f, orbError: %.3f, shapeError: %.3f, imgsGapError: %.3f"%(self.curLoss, self.curOrbDisError, self.curShapeMatchError, self.curImgsGapError))
        curIter = 0
        preLoss = INF
        miniLoss = INF
        miniIter = -1
        self.resetTrainingRatio()
        while self.curLoss > 2 and curIter <= MAXITERATIONS * 50:
            fromTime = time.time()
            # gradient = self.calGradient()
            # self.gradDescent(gradientMethod['-----'])
            self.calGradientForImgsGapError(errorRange = errorRange)
            self.gradDescent()
            self.curLoss = self.calLoss(errorRange = errorRange)

            if self.isConveraged(preLoss, self.curLoss, curIter, 0.5, 15):
                break

            if curIter > 10 and miniLoss > self.curLoss:
                miniLoss = self.curLoss
                miniIter = 0

            if miniIter >= 0:
                miniIter += 1
            if miniIter > 10:
                break

            duration = time.time() - fromTime

            curIter += 1
            preLoss = self.curLoss
            log.logger.info("duration time: %.3f s"%duration)
            log.logger.info("optimize(%s) => imgsGap, iter:%d, curLoss:%.3f, orbError: %.3f, shapeError: %.3f, imgsGapError: %.3f, bldLenError: %.3f"%(errorRange, curIter, self.curLoss, self.curOrbDisError, self.curShapeMatchError, self.curImgsGapError, self.curBladeLengthError))
            # if curIter % (int)(configData['storePanoramPerImgs']) == 0:
                # self.showPanoramaImg()
        self.showPanoramaImg(isStorePanorama=True)

    def calImgsTargetCenterAfterGapSmooth(self, beginIndex, endIndex):
        #* calculate current images gap
        self.calCurImgsCenterPt(beginIndex, endIndex)
        log.logger.debug("calImgsGapTarget() => beginIndex: %d, endIndex: %d" %(beginIndex, endIndex))

        for i in range(beginIndex, endIndex):
            if i == beginIndex:
                self.curImgsGap[beginIndex] = 0
                continue
            self.curImgsGap[i] = self.curImgsCenterPt[i][1] - self.curImgsCenterPt[i-1][1]
            # log.logger.debug("imgIndex: %d, curImgGap: %.2f"%(i, self.curImgsGap[i]))

        #* smooth current images gap to get target images gap
        smoothStep = 3 #* must be odd number
        curImgRatio = 0.5
        if smoothStep < 0:
            smoothStep = 1
        elif smoothStep % 2 == 0:
            smoothStep += 1
        smoothStep = (smoothStep - 1)/2
        for i in range(beginIndex, endIndex):
            if i == beginIndex:
                self.targetImgsGap[i] = 0
                continue

            if smoothStep <= 0:
                curGap = self.curImgsGap[i]
            else:
                curGap = curImgRatio * self.curImgsGap[i]
                curRatio = (1 - curImgRatio) / smoothStep

            for j in range(1, smoothStep+1):
                smoothIndex = i - j
                if smoothIndex > beginIndex:
                    curGap += curRatio * self.curImgsGap[smoothIndex]
                else:
                    curGap += curRatio * self.curImgsGap[i]
            
                smoothIndex = i + j
                if smoothIndex < endIndex:
                    curGap += curRatio * self.curImgsGap[smoothIndex]
                else:
                    curGap += curRatio * self.curImgsGap[i]

            self.targetImgsGap[i] = curGap
            # log.logger.debug("imgIndex: %d, targetImgsGap: %.2f"%(i, self.targetImgsGap[i]))

        #* normalize target imgs gap by equalling with cur imgs' all gap's distance
        targetImgsSumGap = 0
        curImgsSumGap = 0
        for i in range(beginIndex, endIndex):
            targetImgsSumGap += self.targetImgsGap[i]
            curImgsSumGap += self.curImgsGap[i]
        lenNormalizedRatio = 1.0 * curImgsSumGap / targetImgsSumGap
        for i in range(beginIndex, endIndex):
            self.targetImgsGap[i] *= lenNormalizedRatio
            # log.logger.debug("imgIndex: %d, targetImgsGap: %.2f"%(i, self.targetImgsGap[i]))

        #* calculate imgs' target center based on targetImgsGap
        for i in range(beginIndex, endIndex):
            if i == beginIndex or i == endIndex - 1:
                self.targetImgsCenterYAfterGapsSmooth[i] = self.curImgsCenterPt[i][1]
                continue
            self.targetImgsCenterYAfterGapsSmooth[i] = self.targetImgsCenterYAfterGapsSmooth[i-1] + self.targetImgsGap[i]

        return self.targetImgsCenterYAfterGapsSmooth[i]

    def calCurImgsCenterPt(self, beginIndex, endIndex):
        log.logger.debug("calCurImgsCenterPt() => beginIndex: %d, endIndex: %d"%(beginIndex, endIndex))
        for i in range(beginIndex, endIndex):
            curImgInfo = self.curData[i]
            self.curImgsCenterPt[i] = Util().calDstPTFromRefPT(curImgInfo['tf']['imgWidth'], curImgInfo['tf']['imgHeight'], curImgInfo['tf']['rotation'], [curImgInfo['tf']['x'], curImgInfo['tf']['y']], [0.5, 0.5], [0, 0])
            # log.logger.debug("imgIndex: %d, centerPt: [%.2f, %.2f]"%(i, self.curImgsCenterPt[i][0], self.curImgsCenterPt[i][1]))

    '''
    Global error for visualization optimization
    '''
    def globalErrorOptimize(self):
        self.resetTrainingRatio()
        self.curLoss = self.calLoss()
        curIter = 0
        preLoss = INF
        self.optStatus = optimizataionStatus['globalGradient']
        curMinLoss = 1000
        miniIter = -1
        miniData = copy.deepcopy(self.curData)
        self.curDataBeforeAllGD = copy.deepcopy(self.curData)
        while self.curLoss > configData['miniLossThreshold'] and curIter <= MAXITERATIONS/2 and self.curLoss < INF/self.numData:
            fromTime = time.time()
            gradient = self.calGradient()
            self.gradDescent()
            self.curLoss = self.calLoss()
            duration = time.time() - fromTime

            curIter += 1
            log.logger.info("duration time: %.3f s"%duration)
            log.logger.info("optimize() => all, iter:%d, curLoss:%.3f, orbError: %.3f, shapeError: %.3f, overlapError: %.3f, bldLenError: %.3f"%(curIter, self.curLoss, self.curOrbDisError, self.curShapeMatchError, self.curOverlapError, self.curBladeLengthError))
            if curIter % (int)(configData['storePanoramPerImgs']) == 0:
                self.showPanoramaImg()

            if miniIter >= 0:
                miniIter += 1
            if miniIter >= 10:
                break
            if curIter > 10 and curMinLoss > self.curLoss:
                # self.showPanoramaImg(curMinLoss)
                curMinLoss = self.curLoss
                miniIter = 0
                miniData = copy.deepcopy(self.curData)
            
            if self.isConveraged(preLoss, self.curLoss, curIter, 0.1, 10):
                break

            preLoss = self.curLoss

        self.curData = copy.deepcopy(miniData)
        self.showPanoramaImg(isStorePanorama=True)

    '''
    Calculate each image's blade's fitted line, and algin all images to a fitted line
    '''
    def adjustRotationByBladeFittedLine(self):
        #* calculate blade fitted line angle in each image
        if len(self.bladeLineAngleDataInImg) <= 0:
            self.calBladeLineAngleDataInImage()
        
        #* calculate blade fitted line angle in panorama image
        if len(self.bladeLineAngleDataInPanorama) <= 0:
            for imgIndex in range(self.numData):
                curValue = self.bladeLineAngleDataInImg[imgIndex] + self.curData[imgIndex]['tf']['rotation']
                self.bladeLineAngleDataInPanorama.append(curValue)

        #* parameters setting
        ignoreImagesNum = 0 #* ignore images whose toRootdistance < 5m
        ignoreImgsPixelHeight = 5 * K_PIX_PER_METER * STANDARDIMGWIDTH / K_IMG_WIDTH
        # bufferImagesNum = 0 #* buffer images whos toRootDistance [5, 10)
        bufferImgsPixelHeight = 10 * K_PIX_PER_METER * STANDARDIMGWIDTH / K_IMG_WIDTH
        # ignoreImgsIndex = [self.numData-1]
        ignoreImgsIndex = []

        deltAngleForIgnoreImages = 0
        deltAngleForIgnoreImagesNum = 0
        for imgIndex in range(self.numData):
            #* skip ignoring images at the beginning of the blade
            # if imgIndex < ignoreImagesNum:
                # continue
            if self.curData[imgIndex]['tf']['y'] - self.curData[0]['tf']['y'] < ignoreImgsPixelHeight:
                ignoreImagesNum = imgIndex+1
                continue

            if imgIndex in ignoreImgsIndex:
                if imgIndex > 0:
                    curDeltAngle = 90 - Util().changeAgnleBetween180(self.bladeLineAngleDataInPanorama[imgIndex-1])
                else:
                    curDeltAngle = 90 - Util().changeAgnleBetween180(self.bladeLineAngleDataInPanorama[imgIndex+1])
            else:
                curDeltAngle = 90 - Util().changeAgnleBetween180(self.bladeLineAngleDataInPanorama[imgIndex])
            self.curData[imgIndex]['tf']['rotation'] += curDeltAngle
            if self.curData[imgIndex]['tf']['y'] - self.curData[0]['tf']['y'] < bufferImgsPixelHeight:
                deltAngleForIgnoreImages += curDeltAngle
                deltAngleForIgnoreImagesNum += 1

        #* change the rotation of ignored images besed on the deltAngle of the ignoreImagesNum-th image
        log.logger.info("deltAngleForIgnoreImages: %.3f"%deltAngleForIgnoreImages)
        if deltAngleForIgnoreImagesNum > 0:
            deltAngleForIgnoreImages /= deltAngleForIgnoreImagesNum
        for imgIndex in range(ignoreImagesNum):
            self.curData[imgIndex]['tf']['rotation'] += deltAngleForIgnoreImages

        #* the rotation adjustment should be based on the center of images
        #* so, we need calculate the left-top points of images after rotation
        for imgIndex in range(self.numData):
            #* calculate the original center point of image
            imgCurInfo = self.curData[imgIndex]
            imgOriInfo = self.originalData[imgIndex]
            centerPt = Util().calDstPTFromRefPT(imgCurInfo['tf']['imgWidth'],imgCurInfo['tf']['imgHeight'],imgOriInfo['tf']['rotation'],[imgCurInfo['tf']['x'], imgCurInfo['tf']['y']],[0.5, 0.5], [0, 0])

            #* calculate the adjusted left-top point
            leftTopPt = Util().calDstPTFromRefPT(imgCurInfo['tf']['imgWidth'],imgCurInfo['tf']['imgHeight'],imgCurInfo['tf']['rotation'],centerPt)

            self.curData[imgIndex]['tf']['x'] = leftTopPt[0]
            self.curData[imgIndex]['tf']['y'] = leftTopPt[1]

            self.originalData[imgIndex]['tf']['rotation'] = imgCurInfo['tf']['rotation']
            self.originalData[imgIndex]['tf']['x'] = leftTopPt[0]
            self.originalData[imgIndex]['tf']['y'] = leftTopPt[1]
            log.logger.info("imgIndex:%d, adjusted rotation:%.3f"%(imgIndex, self.curData[imgIndex]['tf']['rotation']))

        #* show adjusted panorama
        self.showPanoramaImg()

        return True

    def calBladeLineAngleDataInImage(self):
        for imgIndex in range(self.numData):
            angle = self.calFittedLineAngleInImg(imgIndex)
            self.bladeLineAngleDataInImg.append(angle)

    def calFittedLineAngleInImg(self, imgIndex):
        maskImg = self.curData[imgIndex]['mask']
        imgRotation = self.curData[imgIndex]['tf']['rotation']

        _, thresh = cv2.threshold(maskImg, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        if configData['OpenCV'] < 4.0:
            image, contours, hierarchy = cv2.findContours(thresh, 3, 2)
        else:
            contours, hierarchy = cv2.findContours(thresh, 3, 2)
        
        if len(contours) <= 0:
            return 90 - imgRotation

        maxSize = 0
        cnt = None
        for cntI in contours:
            if len(cntI) > maxSize:
                maxSize = len(cntI)
                cnt = copy.deepcopy(cntI)

        #* find convex hull
        hull = cv2.convexHull(np.array(cnt))

        #* filter lines by img rotation
        targetAngle = 90 - imgRotation
        targetAngle = Util().changeAgnleBetween180(targetAngle)
        availableGapAngle = 20

        refPt = None
        curPt = None
        candidateLines = []
        # angleArr = 
        for i in range(len(hull)):
            if i == 0:
                refPt = hull[len(hull)-1][0]
                curPt = hull[0][0]
            else:
                refPt = hull[i-1][0]
                curPt = hull[i][0]

            curAngle = math.atan2(curPt[1]- refPt[1], curPt[0] - refPt[0])
            curAngle *= (180/math.pi)
            curAngle = Util().changeAgnleBetween180(curAngle)

            if abs(curAngle - targetAngle) <= availableGapAngle:
                distance = np.sqrt((curPt[0]-refPt[0])*(curPt[0]-refPt[0]) + (curPt[1]-refPt[1])*(curPt[1]-refPt[1]))
                candidateLines.append([refPt, curPt, distance, curAngle])

        sortedCandidates = sorted(candidateLines, key = lambda candi: candi[2], reverse = True)

        candidateTargetAngle = 0
        num = 0
        #* caculate blade's fitted line angle
        for i in range(len(sortedCandidates)):
            if i <= 1:
                candidateTargetAngle += sortedCandidates[i][3]
                num += 1
                # log.logger.debug(sortedCandidates[i])
        if num <= 0:
            return 90 - imgRotation

        candidateTargetAngle /= num

        # curGabAngle = targetAngle - candidateTargetAngle
        # curFittedLineAngle = imgRotation + curGabAngle
        log.logger.info("imgIndex: %d, imgRotation: %3f, orignalFittedLineAngle: %.3f"%(imgIndex, imgRotation, candidateTargetAngle))

        return candidateTargetAngle

    '''
    calculate gradient for ith image
    '''
    def calScaleGradient(self, imgIndex):
        res = 0
        if imgIndex == 0:
            res = 0
        else:
            curImgInfo = copy.deepcopy(self.curData[imgIndex]['tf'])
            #* calculte i's scale's gradient
            self.curData[imgIndex]['tf']['scale'] += 0.05
            proLoss01 = self.calLoss()
            deltLoss01 = proLoss01 - self.curLoss
            self.curData[imgIndex]['tf']['scale'] -= 0.1
            proLoss02 = self.calLoss()
            deltLoss02 = proLoss02 - self.curLoss

            if deltLoss01 * deltLoss02 >= 0 or proLoss01 >= INF/self.numData or proLoss02 >= INF/self.numData:
                res = 0
            else:
                g = 0.05/deltLoss01
                if g > self.maxScaleStep: g = self.maxScaleStep
                if g < -self.maxScaleStep: g = -self.maxScaleStep
                res = g
            self.curData[imgIndex]['tf'] = copy.deepcopy(curImgInfo)
            log.logger.debug("calScaleGradient() => imgIndex: %d, scale: %.3f, deltLoss01: %.3f"%(imgIndex, res, deltLoss01))

        return res
    def calRotationGradient(self, imgIndex):
        res = 0
        if imgIndex == 0:
            res = 0
        else:
            curImgInfo = copy.deepcopy(self.curData[imgIndex]['tf'])
            self.curData[imgIndex]['tf']['rotation'] += 0.5
            proLoss01 = self.calLoss()
            deltLoss01 = proLoss01 - self.curLoss
            self.curData[imgIndex]['tf']['rotation'] -= 1
            proLoss02 = self.calLoss()
            deltLoss02 = proLoss02 - self.curLoss
            if deltLoss01 * deltLoss02 >= 0  or proLoss01 >= INF/self.numData or proLoss02 >= INF/self.numData:
                res = 0
            else:
                g = 0.5/deltLoss01
                if g > self.maxRotationStep: g = self.maxRotationStep
                if g < -self.maxRotationStep: g = -self.maxRotationStep
                res = g
            self.curData[imgIndex]['tf'] = copy.deepcopy(curImgInfo)
            # log.logger.debug("calRotationGradient() => imgIndex: %d, rotation: %.3f, deltLoss01: %.3f"%(imgIndex, res, deltLoss01))

        return res
    def calXGradient(self, imgIndex):
        res = 0
        if imgIndex == 0:
            res = 0
        else:
            curImgInfo = copy.deepcopy(self.curData[imgIndex]['tf'])
            self.curData[imgIndex]['tf']['x'] += 1
            proLoss01 = self.calLoss()
            deltLoss01 = proLoss01 - self.curLoss
            self.curData[imgIndex]['tf']['x'] -= 2
            proLoss02 = self.calLoss()
            deltLoss02 = proLoss02 - self.curLoss
            if deltLoss01 * deltLoss02 >= 0 or proLoss01 >= INF/self.numData or proLoss02 >= INF/self.numData:
                res = 0
            else:
                g = 1/deltLoss01
                if g > self.maxTransferStep: g = self.maxTransferStep
                if g < -self.maxTransferStep: g = -self.maxTransferStep
                res = g
            self.curData[imgIndex]['tf'] = copy.deepcopy(curImgInfo)
            # log.logger.debug("calXGradient() => imgIndex: %d, X: %.3f, deltLoss01: %.3f"%(imgIndex, res, deltLoss01))

            #* try res
            originalX = self.curData[imgIndex]['tf']['x']
            self.curData[imgIndex]['tf']['x'] -= res
            if self.ShapeMatchEi(imgIndex) >= INF:
                res = 1
                if deltLoss01 < 0: res = -1
            self.curData[imgIndex]['tf']['x'] = originalX

        return res
    def calYGradient(self,imgIndex):
        res = 0
        if imgIndex == 0:
            res = 0
        else:
            curImgInfo = copy.deepcopy(self.curData[imgIndex]['tf'])
            self.curData[imgIndex]['tf']['y'] += 1
            proLoss01 = self.calLoss()
            deltLoss01 = proLoss01 - self.curLoss
            self.curData[imgIndex]['tf']['y'] -= 2
            proLoss02 = self.calLoss()
            deltLoss02 = proLoss02 - self.curLoss
            if deltLoss01 * deltLoss02 >= 0 or proLoss01 >= INF/self.numData or proLoss02 >= INF/self.numData:
                res = 0
            else:
                g = 1/deltLoss01
                if g > self.maxTransferStep: g = self.maxTransferStep
                if g < -self.maxTransferStep: g = -self.maxTransferStep
                res = g
            self.curData[imgIndex]['tf'] = copy.deepcopy(curImgInfo)

            #* try res
            originalY = self.curData[imgIndex]['tf']['y']
            self.curData[imgIndex]['tf']['y'] -= res
            if self.ShapeMatchEi(imgIndex) >= INF:
                res = 1
                if deltLoss01 < 0: res = -1
            self.curData[imgIndex]['tf']['y'] = originalY

        return res
    def calGradient(self, gradientParamMethod = GradientParamMethod["all"]):
        #* for single image's gradient
        if self.curGradientImgIndex >= 0:
            for i in range(self.numData):
                self.gradient[i]['scale'] = 0
                self.gradient[i]['rotation'] = 0
                self.gradient[i]['x'] = 0
                self.gradient[i]['y'] = 0

            if self.calOvrlapRatioI(self.curGradientImgIndex) < 0.08 and self.isBladeB:
                self.gradient[self.curGradientImgIndex]['scale'] = 0
                self.gradient[self.curGradientImgIndex]['x'] = 0
                self.gradient[self.curGradientImgIndex]['y'] = 0
                self.gradient[self.curGradientImgIndex]['rotation'] = 0
                # log.logger.debug("imgIndex:%d, Blade B, overlap: %.3f"%(imgIndex, self.calOvrlapRatioI(imgIndex)))
            elif self.calOvrlapRatioI(self.curGradientImgIndex) < 0.25 and not self.isBladeB:
                self.gradient[self.curGradientImgIndex]['scale'] = 0
                self.gradient[self.curGradientImgIndex]['x'] = 0
                self.gradient[self.curGradientImgIndex]['y'] = 0
                self.gradient[self.curGradientImgIndex]['rotation'] = 0
            else:
                if configData['useScale']:
                    self.gradient[self.curGradientImgIndex]['scale'] = self.calScaleGradient(self.curGradientImgIndex)
                else:
                    self.gradient[self.curGradientImgIndex]['scale'] = 0
                
                #* open the rotation gradient descent when the local error becomes smaller
                #* open the rotation gradient descent when there is no orb feature matching
                if configData['useRotatation']:
                    if self.curOrbDisError <= 0 and self.curLoss <= 30 and (gradientMethod == GradientParamMethod['all'] or gradientMethod == GradientParamMethod['xRotation'] or gradientMethod == GradientParamMethod['yRotation']):
                        self.gradient[self.curGradientImgIndex]['rotation'] = self.calRotationGradient(self.curGradientImgIndex)

                if gradientParamMethod == GradientParamMethod['all'] or gradientParamMethod == GradientParamMethod['x'] or gradientParamMethod == GradientParamMethod['xy'] or gradientParamMethod == GradientParamMethod['xRotation']:
                    self.gradient[self.curGradientImgIndex]['x'] = self.calXGradient(self.curGradientImgIndex)
                if gradientParamMethod == GradientParamMethod['all'] or gradientParamMethod == GradientParamMethod['y'] or gradientParamMethod == GradientParamMethod['xy'] or gradientParamMethod == GradientParamMethod['yRotation']:
                    self.gradient[self.curGradientImgIndex]['y'] = self.calYGradient(self.curGradientImgIndex)
        else:
            # imgsInfo = copy.deepcopy(self.curData)
            fromTime = time.time()
            for i in range(self.numData):
                # log.logger.debug("gradient %d/%d.., duration: %.3f s"%(i, self.numData, (time.time()-fromTime)))
                # curImgInfo = copy.copy(self.curData[i]['tf'])
                #* calculte i's scale's gradient
                if configData['useScale']:
                    self.gradient[i]['scale'] = self.calScaleGradient(i)
                else:
                    self.gradient[i]['scale'] = 0

                # self.gradient[i]['scale'] = self.calScaleGradient(i)
                # self.gradient[i]['scale'] = 0  

                #* calculate i's rotation's gradient
                if configData['useRotatation'] and (gradientParamMethod == GradientParamMethod['all'] or gradientParamMethod == GradientParamMethod['rotation'] or gradientParamMethod == GradientParamMethod['xRotation'] or gradientParamMethod == GradientParamMethod['yRotation']):
                    self.gradient[i]['rotation'] = self.calRotationGradient(i)

                #* calculate i's x's gradient
                if gradientParamMethod == GradientParamMethod['all'] or gradientParamMethod == GradientParamMethod['x'] or gradientParamMethod == GradientParamMethod['xy'] or gradientParamMethod == GradientParamMethod['xRotation']:
                    self.gradient[i]['x'] = self.calXGradient(i)

                #* calculate i's y's gradient
                if gradientParamMethod == GradientParamMethod['all'] or gradientParamMethod == GradientParamMethod['y'] or gradientParamMethod == GradientParamMethod['xy'] or gradientParamMethod == GradientParamMethod['yRotation']:
                    self.gradient[i]['y'] = self.calYGradient(i)

        return self.gradient

    def traverseRestImgs(self, i, x, y):
        for j in range(i, self.numData):
            self.curData[j]['tf']['x'] += x
            self.curData[j]['tf']['y'] += y

    '''
    Calculate gradient just for blade length error's gradient descent
    '''
    def calGradientForLenError(self, errorRange = bldErrorRange['allPath']):
        bladeRootTPX = self.curData[0]['tf']['x'] + self.panoTx
        bladeRootTPY = self.curData[0]['tf']['y'] + self.panoTy
        bladeTipTPX = self.curData[self.numData-1]['tf']['x'] + self.panoTx
        bladeTipTPY = self.curData[self.numData-1]['tf']['y'] + self.panoTy
        dltaX = abs(bladeTipTPX - bladeTipTPX)
        dltaY = abs(bladeTipTPY - bladeRootTPY)
        # bladeLen = np.sqrt(dltaX*dltaX + dltaY*dltaY)
        #* here, we just use abs(delt(y)) as blade length
        bladeLen = abs(dltaY)
        vector = [1.0*dltaX/bladeLen, 1.0*dltaY/bladeLen]
        # log.logger.debug("vector: %.3f, %.3f" %(vector[0], vector[1]))

        for imgIndex in range(self.numData):
            self.gradient[imgIndex]['rotation'] = 0.0
            if imgIndex <=2:
                self.gradient[imgIndex]['x'] = 0.0
                self.gradient[imgIndex]['y'] = 0.0
                self.gradient[imgIndex]['rotation'] = 0.0
            else:
                if  self.calOvrlapRatioI(imgIndex) < 0.08 and self.isBladeB:
                    self.gradient[imgIndex]['x'] = 0.0
                    self.gradient[imgIndex]['y'] = 0.0
                    self.gradient[imgIndex]['rotation'] = 0.0
                    # log.logger.debug("imgIndex:%d, Blade B, overlap: %.3f"%(imgIndex, self.calOvrlapRatioI(imgIndex)))
                elif self.calOvrlapRatioI(imgIndex) < 0.25 and not self.isBladeB:
                    self.gradient[imgIndex]['x'] = 0.0
                    self.gradient[imgIndex]['y'] = 0.0
                    self.gradient[imgIndex]['rotation'] = 0.0
                    # log.logger.debug("imgIndex:%d, Blade A, C, overlap: %.3f"%(imgIndex, self.calOvrlapRatioI(imgIndex)))
                else:
                    curImgInfo = copy.deepcopy(self.curData[imgIndex]['tf'])
                    self.curData[imgIndex]['tf']['x'] += vector[0]
                    self.curData[imgIndex]['tf']['y'] += vector[1]
                    self.traverseRestImgs(imgIndex+1, vector[0], vector[1])
                    proLoss01 = self.calLoss(gradientMethod['bladeLenGDirect'], errorRange)
                    log.logger.debug("imgIndex: %d, proLoss01:%.3f"%(imgIndex, proLoss01))
                    deltLoss01 = proLoss01 - self.curLoss
                    log.logger.debug("deltLoss01:%.3f"%deltLoss01)
                    self.curData[imgIndex]['tf']['x'] -= 2*vector[0]
                    self.curData[imgIndex]['tf']['y'] -= 2*vector[1]
                    self.traverseRestImgs((imgIndex+1), (-2.0*vector[0]), (-2.0*vector[1]))
                    proLoss02 = self.calLoss(gradientMethod['bladeLenGDirect'], errorRange)
                    deltLoss02 = proLoss02 - self.curLoss
                    if deltLoss01 * deltLoss02 >= 0 or proLoss01 >= INF/self.numData or proLoss02 >= INF/self.numData:
                        self.gradient[imgIndex]['x'] = 0.0
                        self.gradient[imgIndex]['y'] = 0.0
                        self.traverseRestImgs((imgIndex+1), vector[0], vector[1])
                    else:
                        valueLoss = self.calLoss(gradientMethod['bladeLenGValue'], errorRange)
                        self.curData[imgIndex]['tf']['x'] += vector[0]
                        self.curData[imgIndex]['tf']['y'] += vector[1]
                        self.traverseRestImgs((imgIndex+1), vector[0], vector[1])
                        valueCur = self.calLoss(gradientMethod['bladeLenGValue'], errorRange)

                        dltaValueLoss = abs(valueLoss - valueCur)*1000
                        # log.logger.debug("dltaValueLoss:%.3f"%dltaValueLoss)
                        if dltaValueLoss <= 0.1:
                            dltaValueLoss = 0.1
                        gX = 1.0*vector[0]/dltaValueLoss
                        gY = 1.0*vector[1]/dltaValueLoss
                        if deltLoss01 < 0:
                            gX = -gX
                            gY = -gY
                        if gX > self.maxTransferStep: gX = self.maxTransferStep
                        if gX < -self.maxTransferStep: gX = -self.maxTransferStep
                        if gY > self.maxTransferStep: gY = self.maxTransferStep
                        if gY < -self.maxTransferStep: gY = -self.maxTransferStep      
                        # log.logger.debug('gX,gY:%.3f, %.3f'%(gX, gY))
                        self.gradient[imgIndex]['x'] = gX
                        self.gradient[imgIndex]['y'] = gY
                    self.gradient[imgIndex]['rotation'] = 0.0
                    # log.logger.debug("calGradientForLenError() => imgIndex: %d, gx: %.3f, gy: %.3f"%(imgIndex, self.gradient[imgIndex]['x'], self.gradient[imgIndex]['y']))
                    self.curData[imgIndex]['tf'] = copy.deepcopy(curImgInfo)

        #* normalize the max gradient step to [1.0, self.maxTransferStep]
        maxStep = 0.0
        normalizeRatio = 1.0
        for imgIndex in range(self.numData):
            if maxStep < abs(self.gradient[imgIndex]['x']):
                maxStep = abs(self.gradient[imgIndex]['x'])
            if maxStep < abs(self.gradient[imgIndex]['y']):
                maxStep = abs(self.gradient[imgIndex]['y'])
        if maxStep > 0.001 and maxStep < 1.0:
            normalizeRatio = 1.0/maxStep
        log.logger.info("calGradientForLenError, maxStep: %.5f, normalizeRatio: %.3f"%(maxStep, normalizeRatio))

        if normalizeRatio != 1.0:
            for imgIndex in range(self.numData):
                self.gradient[imgIndex]['x'] *= normalizeRatio
                self.gradient[imgIndex]['y'] *= normalizeRatio

        return self.gradient

    '''
    Calculate gradient just for images' gap error's gradient descent
    '''
    def calGradientForImgsGapError(self, errorRange):
        bladeRootTPX = self.curData[0]['tf']['x'] + self.panoTx
        bladeRootTPY = self.curData[0]['tf']['y'] + self.panoTy
        bladeTipTPX = self.curData[self.numData-1]['tf']['x'] + self.panoTx
        bladeTipTPY = self.curData[self.numData-1]['tf']['y'] + self.panoTy
        dltaX = abs(bladeTipTPX - bladeTipTPX)
        dltaY = abs(bladeTipTPY - bladeRootTPY)
        # bladeLen = np.sqrt(dltaX*dltaX + dltaY*dltaY)
        #* here, we just use abs(delt(y)) as blade length
        bladeLen = abs(dltaY)
        vector = [1.0*dltaX/bladeLen, 1.0*dltaY/bladeLen]
        # log.logger.debug("vector: %.3f, %.3f" %(vector[0], vector[1]))

        for imgIndex in range(self.numData):
            self.gradient[imgIndex]['scale'] = 0
            self.gradient[imgIndex]['x'] = 0
            self.gradient[imgIndex]['y'] = 0
            self.gradient[imgIndex]['rotation'] = 0

        startIndex = 0
        stopIndex = self.switcherImgIndex

        if errorRange == bldErrorRange['2ndHalfPath']:
            startIndex = self.switcherImgIndex
            stopIndex = self.numData

        for imgIndex in range(startIndex, stopIndex):
            if imgIndex == 0 or imgIndex == self.switcherImgIndex - 1 or imgIndex == self.switcherImgIndex or imgIndex == self.numData-1:
                self.gradient[imgIndex]['scale'] = 0
                self.gradient[imgIndex]['x'] = 0
                self.gradient[imgIndex]['y'] = 0
                self.gradient[imgIndex]['rotation'] = 0
                continue

            # if  self.calOvrlapRatioI(imgIndex) < 0.08 and self.isBladeB:
            #     self.gradient[imgIndex]['x'] = 0
            #     self.gradient[imgIndex]['y'] = 0
            #     self.gradient[imgIndex]['rotation'] = 0
            #         # log.logger.debug("imgIndex:%d, Blade B, overlap: %.3f"%(imgIndex, self.calOvrlapRatioI(imgIndex)))
            # elif self.calOvrlapRatioI(imgIndex) < 0.25 and not self.isBladeB:
            #     self.gradient[imgIndex]['x'] = 0
            #     self.gradient[imgIndex]['y'] = 0
            #     self.gradient[imgIndex]['rotation'] = 0

            curImgInfo = copy.deepcopy(self.curData[imgIndex]['tf'])
            self.curData[imgIndex]['tf']['x'] += vector[0]
            self.curData[imgIndex]['tf']['y'] += vector[1]
            # self.traverseRestImgs(imgIndex+1, vector[0], vector[1])
            proLoss01 = self.calLoss(errorRange = errorRange)
            log.logger.debug("imgIndex: %d, proLoss01:%.3f"%(imgIndex, proLoss01))
            deltLoss01 = proLoss01 - self.curLoss
            log.logger.debug("deltLoss01:%.3f"%deltLoss01)
            self.curData[imgIndex]['tf']['x'] -= 2*vector[0]
            self.curData[imgIndex]['tf']['y'] -= 2*vector[1]
            # self.traverseRestImgs((imgIndex+1), (-2.0*vector[0]), (-2.0*vector[1]))
            proLoss02 = self.calLoss(errorRange = errorRange)
            deltLoss02 = proLoss02 - self.curLoss
            if deltLoss01 * deltLoss02 >= 0 or proLoss01 >= INF/self.numData or proLoss02 >= INF/self.numData:
                self.gradient[imgIndex]['x'] = 0
                self.gradient[imgIndex]['y'] = 0
                # self.traverseRestImgs((imgIndex+1), vector[0], vector[1])
            else:
                valueLoss = self.calLoss(errorRange = errorRange)
                self.curData[imgIndex]['tf']['x'] += vector[0]
                self.curData[imgIndex]['tf']['y'] += vector[1]
                # self.traverseRestImgs((imgIndex+1), vector[0], vector[1])
                valueCur = self.calLoss(errorRange = errorRange)

                dltaValueLoss = abs(valueLoss - valueCur)*1000
                # log.logger.debug("dltaValueLoss:%.3f"%dltaValueLoss)
                if dltaValueLoss <= 0.1:
                    dltaValueLoss = 0.1
                gX = 1.0*vector[0]/dltaValueLoss
                gY = 1.0*vector[1]/dltaValueLoss
                if deltLoss01 < 0:
                    gX = -gX
                    gY = -gY
                if gX > self.maxTransferStep: gX = self.maxTransferStep
                if gX < -self.maxTransferStep: gX = -self.maxTransferStep
                if gY > self.maxTransferStep: gY = self.maxTransferStep
                if gY < -self.maxTransferStep: gY = -self.maxTransferStep      
                # log.logger.debug('gX,gY:%.3f, %.3f'%(gX, gY))
                self.gradient[imgIndex]['x'] = gX
                self.gradient[imgIndex]['y'] = gY
            self.gradient[imgIndex]['rotation'] = 0
            # log.logger.debug("calGradientForLenError() => imgIndex: %d, gx: %.3f, gy: %.3f"%(imgIndex, self.gradient[imgIndex]['x'], self.gradient[imgIndex]['y']))
            self.curData[imgIndex]['tf'] = copy.deepcopy(curImgInfo)

        return self.gradient

    def gradDescent(self, method = gradientMethod['all']):
        #* for single image's gradient descent
        # if self.curGradientImgIndex >= 0:
        if self.optStatus == optimizataionStatus['localGradient']:
            j = self.curGradientImgIndex
            oRefM = self.T2M(self.curData[j]['tf'])

            if configData['useScale']:
                self.curData[j]['tf']['scale'] -= self.gradient[j]['scale']
            if configData['useRotatation']:
                self.curData[j]['tf']['rotation'] -= self.gradient[j]['rotation']

            self.curData[j]['tf']['x'] -= self.gradient[j]['x']
            # self.adjustCurEdge4Points(j, -self.gradient[j]['x'])
            if self.curData[j]['isSwitcherImg'] == False:
                self.curData[j]['tf']['y'] -= self.gradient[j]['y']
                # self.adjustCurEdge4Points(j, -self.gradient[j]['y'])

                #* protect over optimized case that j's y becomes smaller than j-1's y
                if j > 0 and self.curData[j]['tf']['y'] <= self.curData[j-1]['tf']['y']:
                    self.curData[j]['tf']['y'] += self.gradient[j]['y']
                    # self.adjustCurEdge4Points(j, self.gradient[j]['y'])

            #* protect scale
            if self.curData[j]['tf']['scale'] >= self.originalData[j]['tf']['scale'] + configData['maxDeltaScale']:
                self.curData[j]['tf']['scale'] = self.originalData[j]['tf']['scale'] + configData['maxDeltaScale']
            elif self.curData[j]['tf']['scale'] <= self.originalData[j]['tf']['scale'] - configData['maxDeltaScale']:
                self.curData[j]['tf']['scale'] = self.originalData[j]['tf']['scale'] - configData['maxDeltaScale']
            #* protect rotation
            if self.curData[j]['tf']['rotation'] >= self.originalData[j]['tf']['rotation'] + configData['maxDeltaRotation']:
                self.curData[j]['tf']['rotation'] = self.originalData[j]['tf']['rotation'] + configData['maxDeltaRotation']
            elif self.curData[j]['tf']['rotation'] <= self.originalData[j]['tf']['rotation'] - configData['maxDeltaRotation']:
                self.curData[j]['tf']['rotation'] = self.originalData[j]['tf']['rotation'] - configData['maxDeltaRotation']

            for i in range(j+1, self.numData):
                curM = self.T2M(self.curData[i]['tf'])
                relM = oRefM.I * curM
                oRefM = copy.deepcopy(curM)
                refM = self.T2M(self.curData[i-1]['tf'])
                curM = refM * relM
                curTF = copy.deepcopy(self.M2T(curM))
                self.curData[i]['tf']['x'] = curTF['x']
                self.curData[i]['tf']['y'] = curTF['y']
                self.curData[i]['tf']['scale'] = curTF['scale']
                self.curData[i]['tf']['rotation'] = curTF['rotation']

        #* for all images' gradient descent
        # elif self.curGradientImgIndex < 0:
        elif self.optStatus == optimizataionStatus['lenthGradient'] or self.optStatus == optimizataionStatus['imgsGapGradient']:
            # for i in range(self.numData):
                # log.logger.debug("index:%d, gradientY:%.3f"%(i, self.gradient[i]['y']))

            for i in range(self.numData):
                # self.curData[i]['tf']['scale'] -= self.gradient[i]['scale']
                # if configData['useRotatation'] and self.optStatus == optimizataionStatus['lenthGradient']:
                    # self.curData[i]['tf']['rotation'] -= self.gradient[i]['rotation']
                self.curData[i]['tf']['x'] -= self.gradient[i]['x']

                deltY = self.gradient[i]['y']

                #* don't do y graident descent for switcher images
                # if self.curData[i]['isSwitcherImg'] == False:
                    # deltY = 0

                self.curData[i]['tf']['y'] -= deltY
                #* protect over optimized case that j's y becomes smaller than j-1's y
                if i > 0 and self.curData[i]['tf']['y'] <= self.curData[i-1]['tf']['y']:
                    self.curData[i]['tf']['y'] += deltY
                    deltY = 0

                if self.optStatus == optimizataionStatus['lenthGradient']:
                    deltX = -self.gradient[i]['x']
                    deltY = -deltY
                    self.traverseRestImgs(i+1, deltX, deltY)

                # if self.curData[i]['tf']['rotation'] >= self.curDataBeforeAllGD[i]['tf']['rotation'] + configData['maxDeltaRotation']:
                #     self.curData[i]['tf']['rotation'] = self.curDataBeforeAllGD[i]['tf']['rotation'] + configData['maxDeltaRotation']
                # elif self.curData[i]['tf']['rotation'] <= self.curDataBeforeAllGD[i]['tf']['rotation'] - configData['maxDeltaRotation']:
                #     self.curData[i]['tf']['rotation'] = self.curDataBeforeAllGD[i]['tf']['rotation'] - configData['maxDeltaRotation']

        elif self.optStatus == optimizataionStatus['globalGradient']:
            for i in range(self.numData):
                if configData['useScale']:
                    self.curData[i]['tf']['scale'] -= self.gradient[i]['scale']

                if configData['useRotatation']:
                    self.curData[i]['tf']['rotation'] -= self.gradient[i]['rotation']
                self.curData[i]['tf']['x'] -= self.gradient[i]['x']

                deltY = self.gradient[i]['y']

                #* don't do y graident descent for switcher images
                if self.curData[i]['isSwitcherImg'] == True:
                    deltY = 0

                self.curData[i]['tf']['y'] -= deltY
                #* protect over optimized case that j's y becomes smaller than j-1's y
                if i > 0 and self.curData[i]['tf']['y'] <= self.curData[i-1]['tf']['y']:
                    self.curData[i]['tf']['y'] += deltY
                    deltY = 0

                # if method == gradientMethod['bladeLenGDirect']:
                #     self.traverseRestImgs(i, -self.gradient[i]['x'], - deltY)

                #* protect scale
                if self.curData[i]['tf']['scale'] >= self.originalData[i]['tf']['scale'] + configData['maxDeltaScale']:
                    self.curData[i]['tf']['scale'] = self.originalData[i]['tf']['scale'] + configData['maxDeltaScale']
                elif self.curData[i]['tf']['scale'] <= self.originalData[i]['tf']['scale'] - configData['maxDeltaScale']:
                    self.curData[i]['tf']['scale'] = self.originalData[i]['tf']['scale'] - configData['maxDeltaScale']

                #* protect rotation
                if self.curData[i]['tf']['rotation'] >= self.curDataBeforeAllGD[i]['tf']['rotation'] + configData['maxDeltaRotation']:
                    self.curData[i]['tf']['rotation'] = self.curDataBeforeAllGD[i]['tf']['rotation'] + configData['maxDeltaRotation']
                elif self.curData[i]['tf']['rotation'] <= self.curDataBeforeAllGD[i]['tf']['rotation'] - configData['maxDeltaRotation']:
                    self.curData[i]['tf']['rotation'] = self.curDataBeforeAllGD[i]['tf']['rotation'] - configData['maxDeltaRotation']

    '''
    Some extrame situations for gradient descent
    '''
    def hasSawTooth(self, imgIndex):
        if imgIndex <= 0:
            return False

        if imgIndex >= len(self.curEdge4Points):
            return False

        deltLeftY =  self.curEdge4Points[imgIndex][0][0][1] - self.curEdge4Points[imgIndex-1][0][1][1]
        deltRightY = self.curEdge4Points[imgIndex][1][0][1] - self.curEdge4Points[imgIndex-1][1][1][1]
        if deltLeftY > 0 or deltRightY > 0:
            return True
        else:
            return False

    def adjustCurEdge4Points(self, imgIndex, deltX, deltY, reversed = False):
        if imgIndex >= len(self.curEdge4Points):
            return False
        #* adjust x
        self.curEdge4Points[imgIndex][0][0][0] += deltX
        self.curEdge4Points[imgIndex][0][1][0] += deltX
        self.curEdge4Points[imgIndex][1][0][0] += deltX
        self.curEdge4Points[imgIndex][1][1][0] += deltX

        #* adjust y
        self.curEdge4Points[imgIndex][0][0][1] += deltY
        self.curEdge4Points[imgIndex][0][1][1] += deltY
        self.curEdge4Points[imgIndex][1][0][1] += deltY
        self.curEdge4Points[imgIndex][1][1][1] += deltY

        # if reversed == False:
        #     for j in range(imgIndex, self.numData):
        #         if j >= len(self.curEdge4Points):
        #             self.curEdge4Points.append(self.find4EdgePointsOfImg(j))
        #         #* adjust x
        #         self.curEdge4Points[j][0][0][0] += deltX
        #         self.curEdge4Points[j][0][1][0] += deltX
        #         self.curEdge4Points[j][1][0][0] += deltX
        #         self.curEdge4Points[j][1][1][0] += deltX

        return True

    '''
    Calculate The Loss of current panorama data
    '''
    def calLoss(self, method = gradientMethod['all'], errorRange = bldErrorRange['allPath']):
        loss = 0

        if self.optStatus == optimizataionStatus["imgsGapGradient"]:
            if configData['useImgsGapE'] and configData["addShapeMatchEToImgsGapE"]:
                self.curShapeMatchError = self.ShapeMatchE()
                loss += self.curShapeMatchError
        elif configData['useShapeMatch'] == True and (method == gradientMethod['all'] or method == gradientMethod['bladeLenGValue']):
            #* calculate shape matching error of all images.
            self.curShapeMatchError = self.ShapeMatchE()
            loss += self.curShapeMatchError

        if self.optStatus == optimizataionStatus["imgsGapGradient"]:
            if configData['useImgsGapE'] and configData["addOrbEToImgsGapE"]:
                self.curOrbDisError = self.ORBDisE()
                loss += self.curOrbDisError
        elif configData['useOrbMatch'] == True and (method == gradientMethod['all'] or method == gradientMethod['bladeLenGValue']):
            #* calculate orb feature distance error of all images,
            self.curOrbDisError = self.ORBDisE()
            loss += self.curOrbDisError

        # if configData['useOverlapMatch'] == True:
        #     self.curOverlapError = self.OverLapE(gradient)
        #     loss += self.curOverlapError

        if self.optStatus == optimizataionStatus["imgsGapGradient"]:
            if configData['useImgsGapE'] and configData['addLenEToImgsGapE']:
                self.curBladeLengthError = self.calBladeLengthE(errorRange)
                loss += self.curBladeLengthError
        #* add the blade length error
        elif configData['useBladeLengthE'] == True and ((self.curGradientImgIndex < 0 and method == gradientMethod['bladeLenGDirect']) or self.optStatus == optimizataionStatus['globalGradient']):
            self.curBladeLengthError = self.calBladeLengthE(errorRange)
            loss += self.curBladeLengthError

        #* add the imgsGap error
        if configData['useImgsGapE'] == True and self.optStatus == optimizataionStatus["imgsGapGradient"]:
            self.curImgsGapError = self.calImgsGapError(errorRange)
            # smooth gap
            loss += self.curImgsGapError

        return loss

    '''
    the blade length error from blade root to blade tip
    '''
    def calBladeLengthE(self, errorRange = bldErrorRange['allPath']):
        #* calculate current blade root
        log.logger.debug("calBladeLengthE() => errorRange: %s"%(errorRange))
        curRootM = None
        rootPTInImg = [self.rootTipMarkerData['rootMark']['px']['x']*self.curData[0]['tf']['imgWidth'], self.rootTipMarkerData['rootMark']['px']['y']*self.curData[0]['tf']['imgHeight']]
        rootPTAfterTF = None
        rootPTInImgArr = np.array([np.array([rootPTInImg])])
        imgName = self.rootTipMarkerData['rootMark']['img']
        for imgInfo in self.curData:
            if imgInfo['imgName'].split('/')[-1] == imgName:
                curRootM = copy.deepcopy(self.T2M(imgInfo['tf']))
        rootPTAfterTF = cv2.perspectiveTransform(rootPTInImgArr, curRootM)
        self.curBladeRootPT = [rootPTAfterTF[0][0][0] + self.panoTx,rootPTAfterTF[0][0][1] + self.panoTy]

        #* calculate current blade tip
        curTipM = None
        tipPTInImg = [self.rootTipMarkerData['tipMark']['px']['x']*self.curData[self.numData - 1]['tf']['imgWidth'], self.rootTipMarkerData['tipMark']['px']['y']*self.curData[self.numData - 1]['tf']['imgHeight']]
        tipPTAfterTF = None
        tipPTInImgArr = np.array([np.array([tipPTInImg])])
        imgName = self.rootTipMarkerData['tipMark']['img']
        for imgInfo in self.curData:
            if imgInfo['imgName'].split('/')[-1] == imgName:
                curTipM = copy.deepcopy(self.T2M(imgInfo['tf']))
        tipPTAfterTF = cv2.perspectiveTransform(tipPTInImgArr, curTipM)
        self.curBladeTipPT = [tipPTAfterTF[0][0][0] + self.panoTx, tipPTAfterTF[0][0][1] + self.panoTy]

        deltD = 0
        # 14m height
        if errorRange == bldErrorRange['1stHalfPath'] and self.switcherImgIndex > 0:
            #* found switcher img index, and calculate 1st half path blade length error

            #* calculate the center point of switcherImg-th img
            imgOriginalData = self.originalData[self.switcherImgIndex]
            imgCurData = self.curData[self.switcherImgIndex]
            originalPT = Util().calDstPTFromRefPT(imgOriginalData['tf']['imgWidth'], imgOriginalData['tf']['imgHeight'], imgOriginalData['tf']['rotation'],[imgOriginalData['tf']['x'], imgOriginalData['tf']['y']],[0,0],[0.5, 0.5])
            curPT = Util().calDstPTFromRefPT(imgCurData['tf']['imgWidth'], imgCurData['tf']['imgHeight'], imgCurData['tf']['rotation'], [imgCurData['tf']['x'], imgCurData['tf']['y']], [0, 0], [0.5, 0.5])


            originalDx = originalPT[0] - self.curBladeRootPT[0]
            originalDy = originalPT[1] - self.curBladeRootPT[1]
            self.firstHalfPathTargetLen = originalDy
            curDx = curPT[0] - self.curBladeRootPT[0]
            curDy = curPT[1] - self.curBladeRootPT[1]
            
            deltD = abs(abs(curDy) - abs(originalDy))
            # log.logger.debug("deltD: %.3f"%deltD)
            # 8m height
        elif errorRange == bldErrorRange['2ndHalfPath'] and self.switcherImgIndex > 0:
            #* found switcher img index, and calculate 2nd half path blade length error

            #* calculate the center point of switcherImg-th img
            imgOriginalData = self.originalData[self.switcherImgIndex]
            imgCurData = self.curData[self.switcherImgIndex]
            originalPT = Util().calDstPTFromRefPT(imgOriginalData['tf']['imgWidth'], imgOriginalData['tf']['imgHeight'], imgOriginalData['tf']['rotation'],[imgOriginalData['tf']['x'], imgOriginalData['tf']['y']],[0,0],[0.5, 0.5])
            curPT = Util().calDstPTFromRefPT(imgCurData['tf']['imgWidth'], imgCurData['tf']['imgHeight'], imgCurData['tf']['rotation'], [imgCurData['tf']['x'], imgCurData['tf']['y']], [0, 0], [0.5, 0.5])
            # firstHalfPathTargetLen = curPT[1] - self.curBladeRootPT[1]
            self.secondHalfPathTargetLen = self.originalTipToRootD - self.firstHalfPathTargetLen

            # originalDx = self.curBladeTipPT[0] - originalPT[0]
            # originalDy = self.curBladeTipPT[1] - originalPT[1]
            curDx = self.curBladeTipPT[0] - curPT[0]
            curDy = self.curBladeTipPT[1] - curPT[1]
            log.logger.debug("curBladeTipPT: [%.3f, %.3f]"%(self.curBladeTipPT[0], self.curBladeTipPT[1]))

            deltD = abs(abs(curDy) - abs(self.secondHalfPathTargetLen))


            # log.logger.debug("2nd, oriPT: [%.3f, %.3f], curPT: [%.3f, %.3f]"%(originalPT[0], originalPT[1], curPT[0], curPT[1]))
        else:
            #* calculate blade length error for whole path
            dx = self.curBladeTipPT[0] - self.curBladeRootPT[0]
            dy = self.curBladeTipPT[1] - self.curBladeRootPT[1]
            # distance = np.sqrt(dx*dx + dy*dy)
            #* here, we use abs(delt(y)) as distance
            distance = abs(dy)
            # log.logger.debug("current blade root to tip dis: %.3f"%distance)
            deltD = abs(distance - self.originalTipToRootD)

        return deltD*configData['bladeLengthWeight']
        # if deltD > -configData['rootToTipDistanceError']*self.originalTipToRootD and deltD < configData['rootToTipDistanceError']*self.originalTipToRootD:
        #     self.curData[i]['tf']['x'] -= self.gradient[i]['x']
        #     self.curData[i]['tf']['y'] -= self.gradient[i]['y']
        #     log.logger.debug("curD: %.3f, max: %.3f"%(deltD, configData['rootToTipDistanceError']*self.originalTipToRootD))

    '''
    calculate error based on ORB feature
    '''
    def ORBDisE(self):
        eSum = 0
        self.keyPTs = []
        # for i in range(self.numData):
            # sum += self.ORBDisEi(i)

        #*  for single image's error
        if self.curGradientImgIndex >= 0:
            # return self.ORBDisEi(self.curGradientImgIndex)
            return self.ORBDisEiWithRANSACFilter(self.curGradientImgIndex)
        
        #* for all images' error
        workers = configData['threadsNum']
        with futures.ThreadPoolExecutor(workers) as executor:
            # res = executor.map(self.ORBDisEi, range(self.numData))
            res = executor.map(self.ORBDisEiWithRANSACFilter, range(self.numData))

        for i in res:
            eSum += i

        if self.numData > 0:
            eSum /= self.numData

        return eSum

    #* calculate each image's ORB's distance error to its reference img
    def ORBDisEi(self, i):
        #* if the two continuous images haven't matching points, return 0 for this group
        if i <= 1:
            return 0

        refImgInfo = self.curData[i-1]
        curImgInfo = self.curData[i]

        kps = curImgInfo['kps']
        desc = curImgInfo['desc']
        refKps = refImgInfo['kps']
        refDesc = refImgInfo['desc']
        
        #* log.logger.debug num of kps, refKps
        if debug:
            log.logger.debug("ORBDisEi() => curImgId, kps num, refKps num:", curImgInfo['index'], len(kps), len(refKps))

        if len(kps) < MINFEATNUM or len(refKps) < MINFEATNUM:
            if debug:
                log.logger.info("ORBDisEi() => few kps:", len(kps), len(refKps))

            return 0

        #* match features
        bfm = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True)
        matches = bfm.match(refDesc, desc)

        #* log.logger.debug num of matches length
        if debug:
            log.logger.debug("ORBDisEi() => matches num:", len(matches))

        if len(matches) < MINFEATNUM:
            if debug:
                log.logger.debug("ORBDisEi() => few match: ", len(matches))
            return 0
        matches = sorted(matches, key = lambda x:x.distance)
        minDist = matches[0].distance
        # log.logger.debug("orb descriptor min dist: %.6f."%minDist)

        #* skip features with large descriptor distance
        ptsByDesc = []
        refPtsByDesc = []
        if minDist > 0.0:
            for m in matches:
                if m.distance < 3 * minDist and len(ptsByDesc) < MINFEATNUM:
                    ptsByDesc.append([kps[m.trainIdx][0], kps[m.trainIdx][1]])
                    refPtsByDesc.append([refKps[m.queryIdx][0], refKps[m.queryIdx][1]])
            else:
                for m in matches:
                    if len(ptsByDesc) < MINFEATNUM:
                        ptsByDesc.append([kps[m.trainIdx][0], kps[m.trainIdx][1]])
                        refPtsByDesc.append([refKps[m.queryIdx][0], refKps[m.queryIdx][1]])

        #* skip features by large location distance
        pts = copy.deepcopy(ptsByDesc)
        refPts = copy.deepcopy(refPtsByDesc)
        # log.logger.debug curImgInfo['tf']['rotation']
        curCos = math.cos(math.radians(curImgInfo['tf']['rotation']))
        curSin = math.sin(math.radians(curImgInfo['tf']['rotation']))
        refCos = math.cos(math.radians(refImgInfo['tf']['rotation']))
        refSin = math.sin(math.radians(refImgInfo['tf']['rotation']))

        curDSqr = 0
        minDSqr = INF
        keyPtsDis = []
        for j in range(len(pts)):
            curPt = pts[j]
            curX = curImgInfo['tf']['x'] + 1.0 * (curPt[0] * curCos - curPt[1] * curSin) * curImgInfo['tf']['scale'] + self.panoTx
            curY = curImgInfo['tf']['y'] + 1.0 * (curPt[0] * curSin + curPt[1] * curCos) * curImgInfo['tf']['scale'] + self.panoTy
            # curX = curImgInfo['tf']['x']
            # curY = curImgInfo['tf']['y']
            refPt = refPts[j]
            refX = refImgInfo['tf']['x'] + 1.0 * (refPt[0] * refCos - refPt[1] * refSin) * refImgInfo['tf']['scale'] + self.panoTx
            refY = refImgInfo['tf']['y'] + 1.0 * (refPt[0] * refSin + refPt[1] * refCos) * refImgInfo['tf']['scale'] + self.panoTy

            curDSqr = np.sqrt(((curX - refX) * (curX - refX) + (curY - refY)*(curY - refY)))
            minDSqr = min(minDSqr, curDSqr)
            keyPtsDis.append(([refX, refY], [curX, curY], curDSqr))

        sumDSqr = 0

        # minDSqr = max(minDSqr, STANDARDIMGWIDTH/100)
        averageW = (refImgInfo['tf']['imgWidth'] + curImgInfo['tf']['imgWidth'])/2
        minDSqr = max(minDSqr, averageW/100)
        for j in range(len(pts)):
            # if keyPtsDis[j][2] < 3 * minDSqr and keyPtsDis[j][2] < STANDARDIMGWIDTH/10:
            if keyPtsDis[j][2] < 3 * minDSqr and keyPtsDis[j][2] < averageW/10:
                self.keyPTs.append((keyPtsDis[j][0], keyPtsDis[j][1]))
                sumDSqr += keyPtsDis[j][2]
            # cv2.circle(self.panormamaImg,(int(curX), int(curY)), 6, (255, 255, 0), -1)

        if len(self.keyPTs) > 0:
            sumDSqr /= len(self.keyPTs)

        if debug:
            log.logger.debug("ORBDisEi() => ", sumDSqr)

        return sumDSqr*configData['orbMathWeight']

    #* calculate each image's ORB's distance error to its reference img based on RANSAC filter
    def ORBDisEiWithRANSACFilter(self, i):
        #* if the two continuous images haven't matching points, return 0 for this group
        if i <= 1:
            return 0

        refImgInfo = self.curData[i-1]
        curImgInfo = self.curData[i]

        kps = curImgInfo['kps']
        desc = curImgInfo['desc']
        refKps = refImgInfo['kps']
        refDesc = refImgInfo['desc']
        
        #* log.logger.debug num of kps, refKps
        if debug:
            log.logger.debug("ORBDisEi() => curImgId, kps num, refKps num:", curImgInfo['index'], len(kps), len(refKps))

        if len(kps) < MINFEATNUM or len(refKps) < MINFEATNUM:
            if debug:
                log.logger.debug("ORBDisEi() => few kps:", len(kps), len(refKps))

            return 0

        #* match features
        bfm = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = False)
        matches = bfm.knnMatch(refDesc, desc, 2)

        #* log.logger.debug num of matches length
        if debug:
            log.logger.debug("ORBDisEi() => matches num:", len(matches))

        if len(matches) < MINFEATNUM:
            if debug:
                log.logger.debug("ORBDisEi() => few match: ", len(matches))
            return 0
        
        candidate = []
        #* skip features with large descriptor distance
        for m, n in matches:
            if m.distance < 0.70 * n.distance:
                candidate.append(m)

        if len(candidate) < MINFEATNUM:
            if debug:
                log.logger.debug("ORBDisEi() => few match based on descriptor distance filter: ", len(candidate))
            return 0

        #* filter features by RANSAC
        ptsByDesc = []
        refPtsByDesc = []
        for m in candidate:
            ptsByDesc.append([kps[m.trainIdx][0], kps[m.trainIdx][1]])
            refPtsByDesc.append([refKps[m.queryIdx][0], refKps[m.queryIdx][1]])
        
        pts = []
        refPts = []
        curCos = math.cos(math.radians(curImgInfo['tf']['rotation']))
        curSin = math.sin(math.radians(curImgInfo['tf']['rotation']))
        refCos = math.cos(math.radians(refImgInfo['tf']['rotation']))
        refSin = math.sin(math.radians(refImgInfo['tf']['rotation']))
        #* calculate the position of points in panorama image
        for i in range(len(ptsByDesc)):
            curPt = ptsByDesc[i]
            curX = curImgInfo['tf']['x'] + 1.0 * (curPt[0] * curCos - curPt[1] * curSin) * curImgInfo['tf']['scale'] + self.panoTx
            curY = curImgInfo['tf']['y'] + 1.0 * (curPt[0] * curSin + curPt[1] * curCos) * curImgInfo['tf']['scale'] + self.panoTy
            pts.append([[curX, curY]])

            refPt = refPtsByDesc[i]
            refX = refImgInfo['tf']['x'] + 1.0 * (refPt[0] * refCos - refPt[1] * refSin) * refImgInfo['tf']['scale'] + self.panoTx
            refY = refImgInfo['tf']['y'] + 1.0 * (refPt[0] * refSin + refPt[1] * refCos) * refImgInfo['tf']['scale'] + self.panoTy
            refPts.append([[refX, refY]])

        homPts = np.array(pts)
        homRefPts = np.array(refPts)
        M, mask = cv2.findHomography(homRefPts, homPts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()

        sumDSqr = 0
        for i in range(len(matchesMask)):
            if matchesMask[i] > 0:
                curRefPT = [refPts[i][0][0], refPts[i][0][1]]
                curCurPT = [pts[i][0][0], pts[i][0][1]]
                curDisPT = np.sqrt((curCurPT[0] - curRefPT[0]) * (curCurPT[0] - curRefPT[0]) + (curCurPT[1] - curRefPT[1]) * (curCurPT[1] - curRefPT[1]))
                sumDSqr += curDisPT
                self.keyPTs.append((curRefPT, curCurPT))

        if len(self.keyPTs) > 0:
            sumDSqr /= len(self.keyPTs)

        if debug:
            log.logger.debug("ORBDisEi() => ", sumDSqr)

        return sumDSqr*configData['orbMathWeight']

    '''
    calculate error based on shape matching
    '''
    def ShapeMatchE(self):
        eSum = 0
        # for i in range(self.numData):
            # eSum += self.ShapeMatchEi(i)

        #*  for single image's error
        if self.curGradientImgIndex >= 0:
            return self.ShapeMatchEi(self.curGradientImgIndex)
        
        #* for all images' error
        workers = configData['threadsNum']
        with futures.ThreadPoolExecutor(workers) as executor:
            res = executor.map(self.ShapeMatchEi, range(self.numData))

        for i in res:
            eSum += i

        if self.numData > 0:
            eSum /= self.numData

        return eSum

    #* calculate each image's shape match error
    def ShapeMatchEi(self, i):
        global index
        index += 1
        if i == 0:
            return 0

        fromTime = time.time()
        areaCurBladeInRefImg, areaRefBladeInCurImg, areaIntersect = self.calShapeIntersectionOfImgI_quick(i)
        # log.logger.debug("calShapeIntersectionOfImgI duration: %.2f s"%(time.time() - fromTime))

        if areaCurBladeInRefImg <= 0 or areaRefBladeInCurImg <= 0 or areaIntersect <= 0:
            return INF+abs(self.curData[i]['tf']['x'] - self.curData[i-1]['tf']['x'])+abs(self.curData[i]['tf']['y'] - self.curData[i-1]['tf']['y'])
        #* Calculate loss
        curInRefRatio = 1.0 * areaIntersect / areaCurBladeInRefImg
        refInCurRatio = 1.0 * areaIntersect / areaRefBladeInCurImg
        loss = 0.5 * ((1 -curInRefRatio) ** 2 + (1 - refInCurRatio) ** 2 + (curInRefRatio - refInCurRatio) ** 2)

        return loss*configData['shapeMatchWeight']

    '''
    calculate the error of imgsGapDistance
    '''
    def calImgsGapError(self, errorRange):
        startIndex = 0
        stopIndex = self.switcherImgIndex

        if errorRange == bldErrorRange['2ndHalfPath']:
            startIndex = self.switcherImgIndex
            stopIndex = self.numData

        #* calculate current imgs gap
        self.calCurImgsCenterPt(startIndex, stopIndex)

        # for i in range(startIndex, stopIndex):
        #     if i == startIndex:
        #         self.curImgsGap[startIndex] = 0
        #         continue

        #     self.curImgsGap[i] = self.curImgsCenterPt[i][1] - self.curImgsCenterPt[i-1][1]

        #* error
        errorI = 0
        num = 0
        for i in range(startIndex, stopIndex):
            errorI += abs(self.curImgsCenterPt[i][1] - self.targetImgsCenterYAfterGapsSmooth[i])
            log.logger.debug("imgIndex:%d, curPtY: %.2f, targetPt: %.2f"%(i, self.curImgsCenterPt[i][1], self.targetImgsCenterYAfterGapsSmooth[i]))
            num += 1
        if num > 0:
            errorI /= num

        return errorI

    '''
    calculate the overlap ratio
    '''
    def calOvrlapRatioI(self, i):
        if i == 0:
            return 0
        #* map ref and mask img to panorama
        refImgInfo = self.curData[i-1]
        curImgInfo = self.curData[i]
        refMaskImg = refImgInfo['mask']
        curMaskImg = curImgInfo['mask']

        #* calculate transformation matrix
        refT = copy.deepcopy(refImgInfo['tf'])
        refT['x'] += self.panoTx
        refT['y'] += self.panoTy
        refM = self.T2M(refT)
        curT = copy.deepcopy(curImgInfo['tf'])
        curT['x'] += self.panoTx
        curT['y'] += self.panoTy
        curM = self.T2M(curT)

        refMaskImgToPano = cv2.warpPerspective(refMaskImg, refM, (self.panoWidth, self.panoHeight))
        curMaskImgToPano = cv2.warpPerspective(curMaskImg, curM, (self.panoWidth, self.panoHeight))

        #* calculate current overlap
        bndBoxRef = cv2.boundingRect(refMaskImgToPano)
        bndBoxCur = cv2.boundingRect(curMaskImgToPano)
        self.curBndBoxRef = copy.deepcopy(bndBoxRef)
        self.curBndBoxCur = copy.deepcopy(bndBoxCur)
        
        deltH = bndBoxRef[1] + bndBoxRef[3] - bndBoxCur[1]
        averageH = (bndBoxRef[3] + bndBoxCur[3])/2
        if averageH > 0:
            curRatio = 1.0 * deltH / averageH
        else:
            curRatio = 0.1

        return curRatio

    '''
    adjust overlap for i's image
    '''
    def findBestShapeMatchOffset(self, curImgIndex, deltX):
        step = 1
        if deltX < 0: step = -1
        resStep = 0

        log.logger.debug("step: %d"%step)

        originalX = self.curData[curImgIndex]['tf']['x']
        preShapeMatchE = INF
        curShapeMatchE = self.ShapeMatchEi(curImgIndex)
        while curShapeMatchE >= INF:
            resStep += step
            self.curData[curImgIndex]['tf']['x'] += step
            curShapeMatchE = self.ShapeMatchEi(curImgIndex)
            preShapeMatchE = curShapeMatchE
            if abs(resStep) > abs(deltX)*3: break

        self.curData[curImgIndex]['tf']['x'] += step
        curShapeMatchE = self.ShapeMatchEi(curImgIndex)
        while curShapeMatchE < preShapeMatchE:
            self.curData[curImgIndex]['tf']['x'] += step
            preShapeMatchE = curShapeMatchE
            curShapeMatchE = self.ShapeMatchEi(curImgIndex)

        if curShapeMatchE >= INF:
            resStep = deltX

        resStep = self.curData[curImgIndex]['tf']['x'] - originalX
        self.curData[curImgIndex]['tf']['x'] = originalX

        return resStep

    def adjustOverlap(self, i):
        if i == 0:
            if i >= len(self.curEdge4Points):
                self.curEdge4Points.append(self.find4EdgePointsOfImg(i))
            return 0
        
        #* map ref and mask img to panorama
        refImgInfo = self.curData[i-1]
        curImgInfo = self.curData[i]
        refMaskImg = refImgInfo['mask']
        curMaskImg = curImgInfo['mask']

        #* calculate transformation matrix
        refT = copy.deepcopy(refImgInfo['tf'])
        refT['x'] += self.panoTx
        refT['y'] += self.panoTy
        refM = self.T2M(refT)
        curT = copy.deepcopy(curImgInfo['tf'])
        curT['x'] += self.panoTx
        curT['y'] += self.panoTy
        curM = self.T2M(curT)

        refMaskImgToPano = cv2.warpPerspective(refMaskImg, refM, (self.panoWidth, self.panoHeight))
        curMaskImgToPano = cv2.warpPerspective(curMaskImg, curM, (self.panoWidth, self.panoHeight))

        #* calculate current overlap
        bndBoxRef = cv2.boundingRect(refMaskImgToPano)
        bndBoxCur = cv2.boundingRect(curMaskImgToPano)
        self.curBndBoxRef = copy.deepcopy(bndBoxRef)
        self.curBndBoxCur = copy.deepcopy(bndBoxCur)

        refMaskImgToPano = cv2.cvtColor(refMaskImgToPano, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(refMaskImgToPano,(self.curBndBoxRef[0] ,self.curBndBoxRef[1]), (self.curBndBoxRef[0] + self.curBndBoxRef[2], self.curBndBoxRef[1] + self.curBndBoxRef[3]), (0, 255, 0),2)
        # cv2.imwrite("refMaskImgToPano.jpg", refMaskImgToPano)
        # cv2.imwrite("curMaskImgToPano.jpg", curMaskImgToPano)

        deltH = bndBoxRef[1] + bndBoxRef[3] - bndBoxCur[1]
        # averageH = (bndBoxRef[3] + bndBoxCur[3])/2
        averageH = bndBoxRef[3]
        if averageH > 0:
            curRatio = 1.0 * deltH / averageH
        else:
            curRatio = 0.1
            cv2.imwrite("refMaskImg.jpg",refMaskImg)
            cv2.imwrite("curMaskImg.jpg",curMaskImg)
            cv2.imwrite("refMaskImgToPano.jpg",refMaskImgToPano)
            cv2.imwrite("curMaskImgToPano.jpg",curMaskImgToPano)
            log.logger.info("refBndBox:",bndBoxRef)
            log.logger.info("curBndBox:",bndBoxCur)

        log.logger.info("cur overlap ratio: %.3f"%(curRatio))
        log.logger.info("cur rotation: %.3f"%curT['rotation'])

        if self.preImgOverlapRatio > 0.6:
            self.preImgOverlapRatio = 0.6

        threshold = 0.3
        if (abs(curT['rotation']) < 190 and abs(curT['rotation']) > 170) or ( abs(curT['rotation']) < 10 ):
            threshold = 0.08
            if self.preImgOverlapRatio > 0.3:
                self.preImgOverlapRatio = 0.3

        if curRatio < threshold:
            # deltX = abs(curT['x'] - refT['x'])
            # deltY = abs(curT['y'] - refT['y'])
            deltX = abs(bndBoxCur[0] - bndBoxRef[0])
            deltY = abs(bndBoxCur[1] - bndBoxRef[1])
            log.logger.debug("bndBoxCur: [%.2f, %.2f], bndBoxRef: [%.2f, %.2f]"%(bndBoxCur[0], bndBoxCur[1], bndBoxRef[0], bndBoxRef[1]))
            unitX = 1.0 * deltX / np.sqrt(deltX*deltX + deltY*deltY)
            unitY = 1.0 * deltY / np.sqrt(deltX*deltX + deltY*deltY)
            # deltX = averageH * (1 - self.preImgOverlapRatio) * unitX
            # deltY = averageH * (1 - self.preImgOverlapRatio) * unitY
            deltX = averageH * (self.preImgOverlapRatio - curRatio) * unitX
            deltY = averageH * (self.preImgOverlapRatio - curRatio) * unitY
            log.logger.debug("bladeIndex: %d, pathIndex: %d, averageH: %.2f, curRatio:%.2f, unitY: %.2f"%(self.bladeIndex, self.pathIndex, averageH, curRatio, unitY))
            log.logger.info("moving, averageH:%.3f, preImgOverlapRatio:%.3f, deltY:%.3f"%(averageH, self.preImgOverlapRatio, deltY))

            curImgX = self.curData[i]['tf']['x']
            curImgY = self.curData[i]['tf']['y']
            oRefM = self.T2M(self.curData[i]['tf'])
            # self.curData[i]['tf']['x'] = self.curData[i-1]['tf']['x'] + deltX
            self.curData[i]['tf']['x'] += self.findBestShapeMatchOffset(i, bndBoxRef[0] - bndBoxCur[0])
            # self.curData[i]['tf']['y'] = self.curData[i-1]['tf']['y'] + deltY
            self.curData[i]['tf']['y'] -= deltY
            # deltX = self.curData[i]['tf']['x'] - curImgX
            # deltY = self.curData[i]['tf']['y'] - curImgY

            #* adjust x-cooridate overlap
            log.logger.debug("xoverlap, curX: %.3f, xWidth: %.3f, refX: %.3f, refXWidth: %.3f"%(self.curData[i]['tf']['x'], bndBoxCur[2],self.curData[i-1]['tf']['x'], bndBoxRef[2]))
            # if bndBoxCur[0] + bndBoxCur[2] < bndBoxRef[0] or bndBoxCur[0] > bndBoxRef[0] + bndBoxRef[2]:
                # self.curData[i]['tf']['x'] = self.curData[i-1]['tf']['x'] + (bndBoxRef[0] - bndBoxCur[0]) + (bndBoxRef[2] - bndBoxCur[2])/2

            # j = i
            for k in range(i+1, self.numData):
                # log.logger.debug("k:%d"%k)
                curM = self.T2M(self.curData[k]['tf'])
                relM = oRefM.I * curM
                oRefM = copy.deepcopy(curM)
                refM = self.T2M(self.curData[k-1]['tf'])
                curM = refM * relM
                curTF = copy.deepcopy(self.M2T(curM))
                # self.curData[k]['tf'] = self.M2T(curM)
                self.curData[k]['tf']['x'] = curTF['x']
                self.curData[k]['tf']['y'] = curTF['y']
                self.curData[k]['tf']['scale'] = curTF['scale']
                self.curData[k]['tf']['rotation'] = curTF['rotation']


            log.logger.info("adjustOverlap() => move %d img from [%.3f, %.3f] to [%.3f, %.3f]"%(i, curImgX, curImgY, self.curData[i]['tf']['x'], self.curData[i]['tf']['y'])) 
        else:
            self.preImgOverlapRatio = curRatio

            if self.ShapeMatchEi(i) >= INF:
                oRefM = self.T2M(self.curData[i]['tf'])
                self.curData[i]['tf']['x'] += self.findBestShapeMatchOffset(i, bndBoxRef[0] - bndBoxCur[0])
                log.logger.info("x:%d"%self.curData[i]['tf']['x'])
                for k in range(i+1, self.numData):
                    log.logger.debug("k:%d"%k)
                    curM = self.T2M(self.curData[k]['tf'])
                    relM = oRefM.I * curM
                    oRefM = copy.deepcopy(curM)
                    refM = self.T2M(self.curData[k-1]['tf'])
                    curM = refM * relM
                    curTF = copy.deepcopy(self.M2T(curM))
                    # self.curData[k]['tf'] = self.M2T(curM)
                    self.curData[k]['tf']['x'] = curTF['x']
                    self.curData[k]['tf']['y'] = curTF['y']
                    self.curData[k]['tf']['scale'] = curTF['scale']
                    self.curData[k]['tf']['rotation'] = curTF['rotation']

        #* adjust image whose bounding box's y is above than img-1's bounding box's y
        if bndBoxCur[1] < bndBoxRef[1] and i != self.switcherImgIndex:
            curImgX = self.curData[i]['tf']['x']
            curImgY = self.curData[i]['tf']['y']
            deltY = bndBoxRef[1] - bndBoxCur[1]

            for j in range(i, self.numData):
                self.curData[j]['tf']['y'] += deltY

        #* after above adjustment, check if there is sawtooth between current image and ref image
        if i >= len(self.curEdge4Points):
            self.curEdge4Points.append(self.find4EdgePointsOfImg(i))
            log.logger.debug("lenCurEdge:%d, imgIndex:%d"%(len(self.curEdge4Points), i))
            deltLeftY =  self.curEdge4Points[i][0][0][1] - self.curEdge4Points[i-1][0][1][1]
            deltRightY = self.curEdge4Points[i][1][0][1] - self.curEdge4Points[i-1][1][1][1]
            if deltLeftY > 0 or deltRightY > 0:
                curDelt = max(deltLeftY, deltRightY)
                for j in range(i, self.numData):
                    self.curData[j]['tf']['y'] -= curDelt

        return curRatio

    '''
    Check if there are sawteeth and ajust them if have
    '''
    def sawToothAdjustment(self):
        # self.curEdge4Points = []
        for i in range(self.numData):
            if i >= len(self.curEdge4Points):
                self.curEdge4Points.append(self.find4EdgePointsOfImg(i))
            else:
                self.curEdge4Points[i] = copy.deepcopy(self.find4EdgePointsOfImg(i))
            cv2.circle(self.panormamaImg, (int(self.curEdge4Points[i][0][0][0]), int(self.curEdge4Points[i][0][0][1])), 8, (255, 255, 0), -1)
            cv2.circle(self.panormamaImg, (int(self.curEdge4Points[i][0][1][0]), int(self.curEdge4Points[i][0][1][1])), 8, (255, 255, 0), -1)
            cv2.circle(self.panormamaImg, (int(self.curEdge4Points[i][1][0][0]), int(self.curEdge4Points[i][1][0][1])), 8, (255, 255, 0), -1)
            cv2.circle(self.panormamaImg, (int(self.curEdge4Points[i][1][1][0]), int(self.curEdge4Points[i][1][1][1])), 8, (255, 255, 0), -1)

        #* check and adjust sawtooth from 0 to self.num-1
        for i in range(1, self.numData):
            #* ignore images whose distance to blade root is smaller than 5m
            if self.curData[i]['tf']['y'] <= 5.0 * K_PIX_PER_METER * K_IMG_WIDTH / STANDARDIMGWIDTH:
                continue

            if self.curEdge4Points[i-1][0][1][1] < self.curEdge4Points[i][0][0][1] or self.curEdge4Points[i-1][1][1][1] < self.curEdge4Points[i][1][0][1]:
                log.logger.info("imgIndex: %d to %d has swatooth.."%(i-1, i))
                self.adjustSawtooth(i, reversed=False)
                # self.showPanoramaImg(isStorePanorama=True)

        #* check and adjust sawtooth from self.num-1 to 0
        for i in range(self.numData - 2, 0, -1):
            if self.curEdge4Points[i][0][1][1] < self.curEdge4Points[i+1][0][0][1] or self.curEdge4Points[i][1][1][1] < self.curEdge4Points[i+1][1][0][1]:
                log.logger.info("imgIndex: %d to %d has swatooth.."%(i, i+1))
                self.adjustSawtooth(i, reversed=True)
                # self.showPanoramaImg(isStorePanorama=True)

        for i in range(self.numData):
            cv2.circle(self.panormamaImg, (int(self.curEdge4Points[i][0][0][0]), int(self.curEdge4Points[i][0][0][1])), 8, (255, 255, 0), -1)
            cv2.circle(self.panormamaImg, (int(self.curEdge4Points[i][0][1][0]), int(self.curEdge4Points[i][0][1][1])), 8, (255, 255, 0), -1)
            cv2.circle(self.panormamaImg, (int(self.curEdge4Points[i][1][0][0]), int(self.curEdge4Points[i][1][0][1])), 8, (255, 255, 0), -1)
            cv2.circle(self.panormamaImg, (int(self.curEdge4Points[i][1][1][0]), int(self.curEdge4Points[i][1][1][1])), 8, (255, 255, 0), -1)
        self.showPanoramaImg()

    def adjustSawtooth(self, imgIndex, reversed = False):
        if imgIndex >= self.numData - 1 or imgIndex <= 0 or imgIndex == self.switcherImgIndex or imgIndex == self.switcherImgIndex - 1:
            return False
        moveStep = 2

        if reversed == False:
            #* from 0 to self.num
            #* adjust sawtooth for 1st blade part
            if imgIndex < self.switcherImgIndex-1:
                while self.curEdge4Points[imgIndex-1][0][1][1] < self.curEdge4Points[imgIndex][0][0][1] or self.curEdge4Points[imgIndex-1][1][1][1] < self.curEdge4Points[imgIndex][1][0][1]:
                    self.curData[imgIndex]['tf']['y'] -= moveStep
                    self.curEdge4Points[imgIndex][0][0][1] -= moveStep
                    self.curEdge4Points[imgIndex][0][1][1] -= moveStep
                    self.curEdge4Points[imgIndex][1][0][1] -= moveStep
                    self.curEdge4Points[imgIndex][1][1][1] -= moveStep
                    minLoss = self.calLoss()
                    minIndex = imgIndex

                    for i in range(imgIndex + 1, self.switcherImgIndex - 1):
                        self.curData[i]['tf']['y'] -= moveStep
                        self.curEdge4Points[i][0][0][1] -= moveStep
                        self.curEdge4Points[i][0][1][1] -= moveStep
                        self.curEdge4Points[i][1][0][1] -= moveStep
                        self.curEdge4Points[i][1][1][1] -= moveStep
                        curLoss = self.calLoss()
                        if minLoss > curLoss and self.curEdge4Points[i][0][1][1] > self.curEdge4Points[i+1][0][0][1] and self.curEdge4Points[i][1][1][1] > self.curEdge4Points[i+1][1][0][1]:
                            minLoss = curLoss
                            minIndex = i

                    for i in range(minIndex+1, self.switcherImgIndex - 1):
                        self.curData[i]['tf']['y'] += moveStep
                        self.curEdge4Points[i][0][0][1] += moveStep
                        self.curEdge4Points[i][0][1][1] += moveStep
                        self.curEdge4Points[i][1][0][1] += moveStep
                        self.curEdge4Points[i][1][1][1] += moveStep
                    log.logger.debug("minIndex: %d, minLoss: %.3f"%(minIndex, minLoss))
            elif imgIndex > self.switcherImgIndex:
            #* adjust sawtooth for 2nd blade part
                while self.curEdge4Points[imgIndex-1][0][1][1] < self.curEdge4Points[imgIndex][0][0][1] or self.curEdge4Points[imgIndex-1][1][1][1] < self.curEdge4Points[imgIndex][1][0][1]:
                    self.curData[imgIndex]['tf']['y'] -= moveStep
                    self.curEdge4Points[imgIndex][0][0][1] -= moveStep
                    self.curEdge4Points[imgIndex][0][1][1] -= moveStep
                    self.curEdge4Points[imgIndex][1][0][1] -= moveStep
                    self.curEdge4Points[imgIndex][1][1][1] -= moveStep
                    minLoss = self.calLoss()
                    minIndex = imgIndex

                    for i in range(imgIndex + 1, self.numData - 1):
                        self.curData[i]['tf']['y'] -= moveStep
                        self.curEdge4Points[i][0][0][1] -= moveStep
                        self.curEdge4Points[i][0][1][1] -= moveStep
                        self.curEdge4Points[i][1][0][1] -= moveStep
                        self.curEdge4Points[i][1][1][1] -= moveStep
                        curLoss = self.calLoss()
                        if minLoss > curLoss and self.curEdge4Points[i][0][1][1] > self.curEdge4Points[i+1][0][0][1] and self.curEdge4Points[i][1][1][1] > self.curEdge4Points[i+1][1][0][1]:
                            minLoss = curLoss
                            minIndex = i

                    for i in range(minIndex + 1, self.numData - 1):
                        self.curData[i]['tf']['y'] += moveStep
                        self.curEdge4Points[i][0][0][1] += moveStep
                        self.curEdge4Points[i][0][1][1] += moveStep
                        self.curEdge4Points[i][1][0][1] += moveStep
                        self.curEdge4Points[i][1][1][1] += moveStep
                    log.logger.debug("minIndex: %d, minLoss: %.3f"%(minIndex, minLoss))
        else:
            #* from self.num to 0
            #* adjust sawtooth for 1st blade part
            if imgIndex < self.switcherImgIndex - 1:
                pass
                while self.curEdge4Points[imgIndex][0][1][1] < self.curEdge4Points[imgIndex+1][0][0][1] or self.curEdge4Points[imgIndex][1][1][1] < self.curEdge4Points[imgIndex+1][1][0][1]:
                    self.curData[imgIndex]['tf']['y'] += moveStep
                    self.curEdge4Points[imgIndex][0][0][1] += moveStep
                    self.curEdge4Points[imgIndex][0][1][1] += moveStep
                    self.curEdge4Points[imgIndex][1][0][1] += moveStep
                    self.curEdge4Points[imgIndex][1][1][1] += moveStep
                    minLoss = self.calLoss()
                    minIndex = imgIndex
                    
                    for i in range(imgIndex - 1, 0, -1):
                        self.curData[i]['tf']['y'] += moveStep
                        self.curEdge4Points[i][0][0][1] += moveStep
                        self.curEdge4Points[i][0][1][1] += moveStep
                        self.curEdge4Points[i][1][0][1] += moveStep
                        self.curEdge4Points[i][1][1][1] += moveStep
                        curLoss = self.calLoss()
                        if minLoss > curLoss and self.curEdge4Points[i-1][0][1][1] > self.curEdge4Points[i][0][0][1] and self.curEdge4Points[i-1][1][1][1] > self.curEdge4Points[i][1][0][1]:
                            minLoss = curLoss
                            minIndex = i

                    for i in range(1, minIndex):
                        self.curData[i]['tf']['y'] -= moveStep
                        self.curEdge4Points[i][0][0][1] -= moveStep
                        self.curEdge4Points[i][0][1][1] -= moveStep
                        self.curEdge4Points[i][1][0][1] -= moveStep
                        self.curEdge4Points[i][1][1][1] -= moveStep
                    log.logger.debug("minIndex: %d, minLoss: %.3f"%(minIndex, minLoss))
            elif imgIndex > self.switcherImgIndex:
            #* adjust sawtooth for 2nd blade part
                while self.curEdge4Points[imgIndex][0][1][1] < self.curEdge4Points[imgIndex+1][0][0][1] or self.curEdge4Points[imgIndex][1][1][1] < self.curEdge4Points[imgIndex+1][1][0][1]:
                    self.curData[imgIndex]['tf']['y'] += moveStep
                    self.curEdge4Points[imgIndex][0][0][1] += moveStep
                    self.curEdge4Points[imgIndex][0][1][1] += moveStep
                    self.curEdge4Points[imgIndex][1][0][1] += moveStep
                    self.curEdge4Points[imgIndex][1][1][1] += moveStep
                    minLoss = self.calLoss()
                    minIndex = imgIndex

                    for i in range(imgIndex - 1, self.switcherImgIndex, -1):
                        self.curData[i]['tf']['y'] += moveStep
                        self.curEdge4Points[i][0][0][1] += moveStep
                        self.curEdge4Points[i][0][1][1] += moveStep
                        self.curEdge4Points[i][1][0][1] += moveStep
                        self.curEdge4Points[i][1][1][1] += moveStep
                        curLoss = self.calLoss()
                        if minLoss > curLoss and self.curEdge4Points[i-1][0][1][1] > self.curEdge4Points[i][0][0][1] and self.curEdge4Points[i-1][1][1][1] > self.curEdge4Points[i][1][0][1]:
                            minLoss = curLoss
                            minIndex = i

                    for i in range(self.switcherImgIndex + 1, minIndex):
                        self.curData[i]['tf']['y'] -= moveStep
                        self.curEdge4Points[i][0][0][1] -= moveStep
                        self.curEdge4Points[i][0][1][1] -= moveStep
                        self.curEdge4Points[i][1][0][1] -= moveStep
                        self.curEdge4Points[i][1][1][1] -= moveStep
            
                    log.logger.debug("minIndex: %d, minLoss: %.3f"%(minIndex, minLoss))

    def find4EdgePointsOfImg(self, imgIndex):
        curImgInfo = self.curData[imgIndex]
        curMaskImg = curImgInfo['mask']

        curTF = copy.deepcopy(curImgInfo['tf'])
        curTF['x'] += self.panoTx
        curTF['y'] += self.panoTy
        curM = self.T2M(curTF)

        #* cur mask img in panorama
        curMaskImgInPanorama = cv2.warpPerspective(curMaskImg, curM, (self.panoWidth, self.panoHeight))

        #* find bounding box of this mask img
        bndBoxCur = cv2.boundingRect(curMaskImgInPanorama)

        #* calculate 4 top points of this image
        rectPoints = [[0, 0], [curImgInfo['tf']['imgWidth'], 0], [0, curImgInfo['tf']['imgHeight']], [curImgInfo['tf']['imgWidth'], curImgInfo['tf']['imgHeight']]]

        curPts = cv2.perspectiveTransform(np.array([rectPoints]), curM)
        leftLine = [[bndBoxCur[0], bndBoxCur[1]], [bndBoxCur[0], bndBoxCur[1] + bndBoxCur[3]]]
        rightLine = [[bndBoxCur[0] + bndBoxCur[2], bndBoxCur[1]], [bndBoxCur[0] + bndBoxCur[2], bndBoxCur[1] + bndBoxCur[3]]]
        fourEdgeLines = [
            [curPts[0][0], curPts[0][1]],
            [curPts[0][1], curPts[0][3]],
            [curPts[0][2], curPts[0][3]],
            [curPts[0][2], curPts[0][0]]
        ]
        left2Points = self.findIntersectionPoints(leftLine, fourEdgeLines)
        right2Points = self.findIntersectionPoints(rightLine, fourEdgeLines)
        log.logger.debug("leftTopPt: [%.2f, %.2f]"%(left2Points[0][0], left2Points[0][1]))
        log.logger.debug("leftBottomPt: [%.2f, %.2f]"%(left2Points[1][0], left2Points[1][1]))
        log.logger.debug("rightTopPt: [%.2f, %.2f]"%(right2Points[0][0], right2Points[0][1]))
        log.logger.debug("rightBottomPt: [%.2f, %.2f]"%(right2Points[1][0], right2Points[1][1]))

        curMaskImgInPanorama = cv2.cvtColor(curMaskImgInPanorama, cv2.COLOR_GRAY2BGR)
        cv2.circle(curMaskImgInPanorama, (int(curPts[0][0][0]), int(curPts[0][0][1])), 5, (255, 0, 0), -1)
        cv2.circle(curMaskImgInPanorama, (int(curPts[0][1][0]), int(curPts[0][1][1])), 5, (0, 255, 0), -1)
        cv2.circle(curMaskImgInPanorama, (int(curPts[0][2][0]), int(curPts[0][2][1])), 5, (0, 0, 255), -1)
        cv2.circle(curMaskImgInPanorama, (int(curPts[0][3][0]), int(curPts[0][3][1])), 5, (255, 255, 0), -1)

        cv2.circle(curMaskImgInPanorama, (int(left2Points[0][0]), int(left2Points[0][1])), 5, (0, 0, 255), -1)
        cv2.circle(curMaskImgInPanorama, (int(left2Points[1][0]), int(left2Points[1][1])), 5, (0, 0, 255), -1)
        cv2.circle(curMaskImgInPanorama, (int(right2Points[0][0]), int(right2Points[0][1])), 5, (0, 0, 255), -1)
        cv2.circle(curMaskImgInPanorama, (int(right2Points[1][0]), int(right2Points[1][1])), 5, (0, 0, 255), -1)

        cv2.line(curMaskImgInPanorama, (bndBoxCur[0], bndBoxCur[1]), (bndBoxCur[0], bndBoxCur[1] + bndBoxCur[3]), (int(random.random()*255), int(random.random()*255), int(random.random()*255)), 2)
        cv2.line(curMaskImgInPanorama, (bndBoxCur[0] + bndBoxCur[2], bndBoxCur[1]), (bndBoxCur[0]  + bndBoxCur[2], bndBoxCur[1] + bndBoxCur[3]), (int(random.random()*255), int(random.random()*255), int(random.random()*255)), 2)
        # curMaskImgInPanorama = np.rot90(curMaskImgInPanorama)
        # cv2.imshow("panorama", curMaskImgInPanorama)
        # cv2.imwrite("panorama.jpg",curMaskImgInPanorama)

        return [left2Points, right2Points]
    
    def findIntersectionPoints(self, line, fourEdgeLines):
        intersectionPoint = None
        topPt = None
        bottomPt = None
        for i in fourEdgeLines:
            log.logger.debug("line: [[%.1f, %.1f], [%.1f, %.1f]], iLine: [[%.1f, %.1f],[%.1f, %.1f]]"%(
                line[0][0], line[0][1], line[1][0], line[1][1], i[0][0], i[0][1], i[1][0], i[1][1]))
            intersectionPoint = Util().twoLineIntersection(line, i)

            log.logger.debug("inter: %s"%intersectionPoint)
            if intersectionPoint != None:
                if topPt == None:
                    topPt = intersectionPoint
                elif topPt[1] > intersectionPoint[1]:
                    topPt = intersectionPoint
                if bottomPt == None:
                    bottomPt = intersectionPoint
                elif bottomPt[1] < intersectionPoint[1]:
                    bottomPt = intersectionPoint

        return [topPt, bottomPt]


    def T2M(self, T):
        scale = T['scale']
        rotation = T['rotation']
        rotation = np.radians(rotation)
        x = T['x']
        y = T['y']
        M = np.mat(np.identity(3))
        M[0, 0] = scale * math.cos(rotation)
        M[0, 1] = -scale * math.sin(rotation)
        M[0, 2] = x
        M[1, 0] = scale * math.sin(rotation)
        M[1, 1] = scale * math.cos(rotation)
        M[1, 2] = y
        return M

    def M2T(self,M):
        scale = math.sqrt(M[0, 0] ** 2 + M[0, 1] ** 2)
        rotation = math.atan2(M[1, 0], M[0, 0])
        rotation = np.degrees(rotation)
        x = M[0, 2]
        y = M[1, 2]
        return { 'scale': scale, 'rotation': rotation, 'x': x, 'y': y }