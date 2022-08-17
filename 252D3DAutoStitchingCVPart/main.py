# -*- coding: utf-8 -*-
#* Author: liuxun@2019.7.07
from util import Util
from stitchingTask import StitchingTask
from markerDistance import MarkerDistance
from crossOptimizeTest import CrossOptimize
import os
import argparse
from logInfo import Logger

log = Logger("main.log",level='info')

configData = Util().fileToJson("config.json")

# i1Path = "Clobotics/Codes/Wind/WindProc/wiProc/data/wiData/samples/insp2sets/i1"
# i2Path = "Clobotics/Codes/Wind/WindProc/wiProc/data/wiData/samples/insp2sets/i2"
i1Path = "Clobotics/Codes/Wind/WindProc/wiProc/data/wiData/samples/B16/i1"
i2Path = "Clobotics/Codes/Wind/WindProc/wiProc/data/wiData/samples/B16/i2"

interfaceFilesPath = [
    "cv2d/wipImgProj_A0.json",
    "cv2d/wipImgProj_A1.json",
    "cv2d/wipImgProj_A2.json",
    "cv2d/wipImgProj_A3.json",
    "cv2d/wipImgProj_B0.json",
    "cv2d/wipImgProj_B1.json",
    "cv2d/wipImgProj_B2.json",
    "cv2d/wipImgProj_B3.json",
    "cv2d/wipImgProj_C0.json",
    "cv2d/wipImgProj_C1.json",
    "cv2d/wipImgProj_C2.json",
    "cv2d/wipImgProj_C3.json"
]

markersPath = "Clobotics/Codes/Wind/WindProc/wiProc/data/wiData/samples/B16/marks"
markersFilePath = [
    "pair_marker_A0.json",
    "pair_marker_A1.json",
    "pair_marker_A2.json",
    "pair_marker_A3.json",
    "pair_marker_B0.json",
    "pair_marker_B1.json",
    "pair_marker_B2.json",
    "pair_marker_B3.json",
    "pair_marker_C0.json",
    "pair_marker_C1.json",
    "pair_marker_C2.json",
    "pair_marker_C3.json",
]

rootTipMarkersPath = [
    "Metadata/blade_A_inspectionInfo.json",
    "Metadata/blade_B_inspectionInfo.json",
    "Metadata/blade_C_inspectionInfo.json"
]

if __name__ == "__main__":
    print("hello world!")
    parser = argparse.ArgumentParser(usage="it's usage trip.", description="help info.")
    parser.add_argument("--insp", type=str, choices=['i1Path', 'i2Path'], default = 'i1Path', help = 'the inspection choice, default i1Path')
    args = parser.parse_args()
    inspType = args.insp
    if inspType == 'i1Path':
        curPath = i1Path
    else:
        curPath = i2Path

    bladeIndex = configData['bladeIndex']
    pathIndex = configData['pathIndex']

    paths = [[0,0],[0,1],[0,2],[0,3],[1,0],[1,1],[1,2],[1,3],[2,0],[2,1],[2,2],[2,3]]

    if bladeIndex >=0 and pathIndex < 0:
        if bladeIndex == 0:
            paths = [[0,0],[0,1],[0,2],[0,3]]
        elif bladeIndex == 1:
            paths = [[1,0],[1,1],[1,2],[1,3]]
        elif bladeIndex == 2:
             paths = [[2,0],[2,1],[2,2],[2,3]]

    if bladeIndex < 0 or pathIndex < 0:
        # for bladeIndex in range(3):
            # for pathIndex in range(4):
        for i in paths:
            bladeIndex = i[0]
            pathIndex = i[1]
            log.logger.info("****************")
            log.logger.info("augment insp: %s, bladeIndex: %d, pathIndex: %d"%(inspType, bladeIndex, pathIndex))
            homePath = os.path.expanduser('~')
            interfaceFilePath = os.path.join(homePath,curPath,interfaceFilesPath[bladeIndex*4+pathIndex])
            dataFolderPath = os.path.join(homePath, curPath, "imgs_s")
            util = Util()
            jsonData = util.fileToJson(interfaceFilePath)

            #* load rootTip marker
            rootTipMarkerFilePath = os.path.join(homePath, curPath, rootTipMarkersPath[bladeIndex])
            rootTipMarkersData = util.fileToJson(rootTipMarkerFilePath)
            rootTipMarkerData = rootTipMarkersData[pathIndex]

            #* save cvRes json file and original panorama img and result panorama img
            cvResJsonFileStorePath = interfaceFilePath.split(".")[0]
            cvResJsonFileStorePath += "_cvRes.json"
            originalPanoramaImgStorePath = interfaceFilePath.split(".")[0]
            originalPanoramaImgStorePath += "_original.jpg"
            resultPanoramaImgStorePath = interfaceFilePath.split(".")[0]
            resultPanoramaImgStorePath += "_result.jpg"

            if configData['callStitchingTask']:
                #* call stitching task
                stitchingtask = StitchingTask(jsonData, dataFolderPath, bladeIndex, pathIndex, interfaceFilePath, rootTipMarkerData)
                stitchingtask.load()
                stitchingtask.stitch()
                stitchingtask.save(cvResJsonFileStorePath, originalPanoramaImgStorePath, resultPanoramaImgStorePath)

            if configData['callMaskerDistanceTask']:
                #* call marker distance task
                markerFilePath = os.path.join(homePath, markersPath, markersFilePath[bladeIndex*4 + pathIndex])
                markerDistance = MarkerDistance()
                markerDistance.load(inspType, cvResJsonFileStorePath, resultPanoramaImgStorePath, markerFilePath, rootTipMarkerData)
                markerDistance.caculate()
                markerDistance.save()

            if configData['callCrossOptimizeTestTask']:
                i1InterfaceFilePath = os.path.join(homePath,i1Path,interfaceFilesPath[bladeIndex*4+pathIndex])
                i1CvResJsonFileStorePath = i1InterfaceFilePath.split(".")[0]
                i1CvResJsonFileStorePath += "_cvRes.json"
                i1CvResJsonData = Util().fileToJson(i1CvResJsonFileStorePath)

                i2InterfaceFilePath = os.path.join(homePath,i2Path,interfaceFilesPath[bladeIndex*4+pathIndex])
                i2CvResJsonFileStorePath = i2InterfaceFilePath.split(".")[0]
                i2CvResJsonFileStorePath += "_cvRes.json"
                i2CvResJsonData = Util().fileToJson(i2CvResJsonFileStorePath)

                #* load rootTip marker
                i1RootTipMarkerFilePath = os.path.join(homePath, i1Path, rootTipMarkersPath[bladeIndex])
                i1RootTipMarkersData = util.fileToJson(i1RootTipMarkerFilePath)
                i1rootTipMarkerData = i1RootTipMarkersData[pathIndex]

                i2RootTipMarkerFilePath = os.path.join(homePath, i2Path, rootTipMarkersPath[bladeIndex])
                i2RootTipMarkersData = util.fileToJson(i2RootTipMarkerFilePath)
                i2rootTipMarkerData = i2RootTipMarkersData[pathIndex]

                i1DataFolderPath = os.path.join(homePath, i1Path, "imgs_s")
                i2DataFolderPath = os.path.join(homePath, i2Path, "imgs_s")

                crossOptimizeInstance = CrossOptimize(bladeIndex, pathIndex, i1CvResJsonData, i2CvResJsonData, i1rootTipMarkerData, i2rootTipMarkerData, i1DataFolderPath, i2DataFolderPath)
                crossOptimizeInstance.load()
                crossOptimizeInstance.calLoss()

    else:
        log.logger.info("****************")
        log.logger.info("augment insp:%s, bladeIndex: %d, pathIndex: %d"%(inspType, bladeIndex, pathIndex))
        homePath = os.path.expanduser('~')
        interfaceFilePath = os.path.join(homePath,curPath,interfaceFilesPath[bladeIndex*4+pathIndex])
        dataFolderPath = os.path.join(homePath, curPath, "imgs_s")
        util = Util()
        jsonData = util.fileToJson(interfaceFilePath)

        #* load rootTip marker
        rootTipMarkerFilePath = os.path.join(homePath, curPath, rootTipMarkersPath[bladeIndex])
        rootTipMarkersData = util.fileToJson(rootTipMarkerFilePath)
        rootTipMarkerData = rootTipMarkersData[pathIndex]

        #* save cvRes json file and original panorama img and result panorama img
        cvResJsonFileStorePath = interfaceFilePath.split(".")[0]
        cvResJsonFileStorePath += "_cvRes.json"
        originalPanoramaImgStorePath = interfaceFilePath.split(".")[0]
        originalPanoramaImgStorePath += "_original.jpg"
        resultPanoramaImgStorePath = interfaceFilePath.split(".")[0]
        resultPanoramaImgStorePath += "_result.jpg"

        if configData['callStitchingTask']:
            #* call stitching task
            stitchingtask = StitchingTask(jsonData, dataFolderPath, bladeIndex, pathIndex, interfaceFilePath, rootTipMarkerData)
            stitchingtask.load()
            stitchingtask.stitch()
            stitchingtask.save(cvResJsonFileStorePath, originalPanoramaImgStorePath, resultPanoramaImgStorePath)

        if configData['callMaskerDistanceTask']:
            #* call marker distance task
            markerFilePath = os.path.join(homePath, markersPath, markersFilePath[bladeIndex*4 + pathIndex])
            markerDistance = MarkerDistance()
            markerDistance.load(inspType, cvResJsonFileStorePath, resultPanoramaImgStorePath, markerFilePath, rootTipMarkerData)
            markerDistance.caculate()
            markerDistance.save()

        if configData['callCrossOptimizeTestTask']:
            i1InterfaceFilePath = os.path.join(homePath,i1Path,interfaceFilesPath[bladeIndex*4+pathIndex])
            i1CvResJsonFileStorePath = i1InterfaceFilePath.split(".")[0]
            i1CvResJsonFileStorePath += "_cvRes.json"
            i1CvResJsonData = Util().fileToJson(i1CvResJsonFileStorePath)

            i2InterfaceFilePath = os.path.join(homePath,i2Path,interfaceFilesPath[bladeIndex*4+pathIndex])
            i2CvResJsonFileStorePath = i2InterfaceFilePath.split(".")[0]
            i2CvResJsonFileStorePath += "_cvRes.json"
            i2CvResJsonData = Util().fileToJson(i2CvResJsonFileStorePath)

            #* load rootTip marker
            i1RootTipMarkerFilePath = os.path.join(homePath, i1Path, rootTipMarkersPath[bladeIndex])
            i1RootTipMarkersData = util.fileToJson(i1RootTipMarkerFilePath)
            i1rootTipMarkerData = i1RootTipMarkersData[pathIndex]

            i2RootTipMarkerFilePath = os.path.join(homePath, i2Path, rootTipMarkersPath[bladeIndex])
            i2RootTipMarkersData = util.fileToJson(i2RootTipMarkerFilePath)
            i2rootTipMarkerData = i2RootTipMarkersData[pathIndex]

            i1DataFolderPath = os.path.join(homePath, i1Path, "imgs_s")
            i2DataFolderPath = os.path.join(homePath, i2Path, "imgs_s")

            crossOptimizeInstance = CrossOptimize(bladeIndex, pathIndex, i1CvResJsonData, i2CvResJsonData, i1rootTipMarkerData, i2rootTipMarkerData, i1DataFolderPath, i2DataFolderPath)
            crossOptimizeInstance.load()
            crossOptimizeInstance.calLoss()

            #* call cross optimize test task
            # crossOptimizeTaskInstance = crossOptimizeTaskInstance