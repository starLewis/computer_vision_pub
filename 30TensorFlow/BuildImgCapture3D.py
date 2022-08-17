# -*- coding: utf-8 -*-
"""
Created on Sat Aug 31 14:53:22 2019

@author: lewisliu
"""

import csv
import numpy as np
from pyproj import Proj, transform  #sudo pip install pyproj
import math
import json

# load json
def loadJson(jsonPath):
    jsonData = None
    with open(jsonPath, 'r') as jsonOpen:
        jsonData = json.load(jsonOpen)
        
    jsonOpen.close()
    return jsonData

# load csv
def loadCsv(csvPath):
    resList = []
    with open(csvPath) as csvFile:
        reader = csv.DictReader(csvFile)
        for row in reader:
            resList.append({
                "BladePosition": row["BladePosition"],
                "BladeSide": row["BladeSide"],
                "ImageFilePath": row["ImageFilePath"],
                "GpsLatitude": row["GpsLatitude"],
                "GpsLongitude": row["GpsLongitude"],
                "GpsAltitude": row["GpsAltitude"],
                "Pitch": row["Pitch"],
                "Roll": row["Roll"],
                "Yaw": row["Yaw"],
                "SequenceDirection": row["SequenceDirection"],
                "MeasuredDistanceToBlade": row["MeasuredDistanceToBlade"],
                "Index": row["Index"]
            })
    
    return resList
    
#    build 12 paths' data from csv data
def buildPaths(resList):
    turbineData = [ [ [], [], [], [] ], [ [], [], [], [] ], [ [], [], [], [] ] ]
#    turbineData = [[]*4]
    print turbineData
#    turbineData = np.array().reshape(3,4)
    
#    map 12 paths
    for unitData in resList:
#        BladePosition A, Blade Side LeadingEdge -> A_PS_LE -> A0 -> [0][0]
        if unitData["BladePosition"] == "A" and unitData["BladeSide"] == "LeadingEdge":
            turbineData[0][0].append(unitData)
#        BladePosition A, Blade Side PressureSide -> A_PS_TE -> A1 -> [0][1]
        elif unitData["BladePosition"] == "A" and unitData["BladeSide"] == "PressureSide":
            turbineData[0][1].append(unitData)
#        BladePosition A, Blade Side TrailingEdge -> A_SS_TE -> A2 -> [0][2]
        elif unitData["BladePosition"] == "A" and unitData["BladeSide"] == "TrailingEdge":
            turbineData[0][2].append(unitData)
#        BladePosition A, Blade Side SuctionSide -> A_SS_LE -> A3 -> [0][3]
        elif unitData["BladePosition"] == "A" and unitData["BladeSide"] == "SuctionSide":
            turbineData[0][3].append(unitData)
        
#        BladePosition B, Blade Side LeadingEdge -> B_PS_LE -> B0 -> [1][0]
        elif unitData["BladePosition"] == "B" and unitData["BladeSide"] == "LeadingEdge":
            turbineData[1][0].append(unitData)
#        BladePosition B, Blade Side PressureSide -> B_PS_TE -> B1 -> [1][1]
        elif unitData["BladePosition"] == "B" and unitData["BladeSide"] == "PressureSide":
            turbineData[1][1].append(unitData)
#        BladePosition B, Blade Side TrailingEdge -> B_SS_TE -> B2 -> [1][2]
        elif unitData["BladePosition"] == "B" and unitData["BladeSide"] == "TrailingEdge":
            turbineData[1][2].append(unitData)
#        BladePosition B, Blade Side SuctionSide -> B_SS_LE -> B3 -> [1][3]
        elif unitData["BladePosition"] == "B" and unitData["BladeSide"] == "SuctionSide":
            turbineData[1][3].append(unitData)
            
#        BladePosition C, Blade Side SuctionSide -> C_SS_LE -> C0 -> [2][0]
        elif unitData["BladePosition"] == "C" and unitData["BladeSide"] == "SuctionSide":
            turbineData[2][0].append(unitData)
#        BladePosition C, Blade Side TrailingEdge -> C_SS_TE -> C1 -> [2][1]
        elif unitData["BladePosition"] == "C" and unitData["BladeSide"] == "TrailingEdge":
            turbineData[2][1].append(unitData)
#        BladePosition C, Blade Side PressureSide -> C_PS_TE -> C2 -> [2][2]
        elif unitData["BladePosition"] == "C" and unitData["BladeSide"] == "PressureSide":
            turbineData[2][2].append(unitData)
#        BladePosition C, Blade Side LeadingEdge -> C_PS_LE -> C3 -> [2][3]
        elif unitData["BladePosition"] == "C" and unitData["BladeSide"] == "LeadingEdge":
            turbineData[2][3].append(unitData)


    return turbineData
    
# convert GPS to ECEF
def gpsToEcef(gpsLongitude, gpsLatitude, gpsAltitude):
    ecef = Proj(proj = 'geocent', ellps = 'WGS84', datum='WGS84')
    lla = Proj(proj = 'latlong', ellps = 'WGS84', datum='WGS84')
    x,y,z = transform(lla, ecef, gpsLongitude, gpsLatitude, gpsAltitude, radians=False)
    
    return (x, y, z)
    
# convert GPS to ENU
def gpsToEnu02(gpsLongitude, gpsLatitude, gpsAltitude, gpsLongitudePOI, gpsLatitudePOI, gpsAltitudePOI):
    ECEFValue = gpsToEcef(gpsLongitude, gpsLatitude, gpsAltitude)
    ECEFValuePOI = gpsToEcef(gpsLongitudePOI, gpsLatitudePOI, gpsAltitudePOI)
    
    cosLatRad = math.cos(math.radians(gpsLatitude))
    cosLongiRad = math.cos(math.radians(gpsLongitude))
    sinLatRad = math.sin(math.radians(gpsLatitude))
    sinLongiRad = math.sin(math.radians(gpsLongitude))
    
    v = np.zeros(3)
    v[0] = ECEFValue[0] - ECEFValuePOI[0]
    v[1] = ECEFValue[1] - ECEFValuePOI[1]
    v[2] = ECEFValue[2] - ECEFValuePOI[2]
#    print("v:{},{},{}".format(v[0], v[1], v[2]))
    
    e = v[0]*(-sinLongiRad) + v[0]*cosLongiRad
    n = v[0]*(-sinLatRad)*(cosLongiRad) + v[1]*(-sinLatRad)*sinLongiRad + v[2]*cosLatRad
    u = v[0]*cosLatRad*cosLongiRad + v[1]*cosLatRad*sinLongiRad + v[2]*sinLatRad
    
    return e, n, u


#    map img in 3D space
def img3DMap(imgData, imgDataPOI):
    DroneX, DroneY, DroneZ = gpsToEnu02(float(imgData["GpsLongitude"]), float(imgData["GpsLatitude"]), float(imgData["GpsAltitude"]), 
                                        float(imgDataPOI["GpsLongitude"]), float(imgDataPOI["GpsLatitude"]), float(imgDataPOI["GpsAltitude"]))
    
    xyDegree = math.radians(90 - float(imgData["Yaw"]))
    zDegree = math.radians(float(imgData["Pitch"]))

    unitVector = (math.cos(zDegree)*math.cos(xyDegree), math.cos(zDegree)*math.sin(xyDegree), math.sin(zDegree))

    imgCenterX = DroneX + float(imgData["MeasuredDistanceToBlade"])*unitVector[0]
    imgCenterY = DroneY + float(imgData["MeasuredDistanceToBlade"])*unitVector[1]
    imgCenterZ = DroneZ + float(imgData["MeasuredDistanceToBlade"])*unitVector[2]

    return (DroneX, DroneY, DroneZ),(imgCenterX, imgCenterY, imgCenterZ)
    
# load and build blade root point and blade tip point data
def buildBldRootTipPointData():
    bldRootTipPointData = np.zeros((3,4,2,2))
    markersPaths = [
        "data/blade_A_inspectionInfo.json",
        "data/blade_B_inspectionInfo.json",
        "data/blade_C_inspectionInfo.json"
    ]
    
    for bldIndex in range(3):
        bldMarkers = loadJson(markersPaths[bldIndex])
        for pathIndex in range(4):
            marker = bldMarkers[pathIndex]
            pathRealIndex = 0
            if marker['bladeSide'].split("_")[0] == "1":
                pathRealIndex = 0
            elif marker['bladeSide'].split("_")[0] == "2":
                pathRealIndex = 1
            elif marker['bladeSide'].split("_")[0] == "3":
                pathRealIndex = 2
            elif marker['bladeSide'].split("_")[0] == "4":
                pathRealIndex = 3
            
#            root point, [xRatio, yRatio]
            bldRootTipPointData[bldIndex][pathRealIndex][0][0] = marker['rootMark']['px']['x']
            bldRootTipPointData[bldIndex][pathRealIndex][0][1] = marker['rootMark']['px']['y']
            
#            tip point, [xRatio, yRatio]
            bldRootTipPointData[bldIndex][pathRealIndex][1][0] = marker['tipMark']['px']['x']
            bldRootTipPointData[bldIndex][pathRealIndex][1][1] = marker['tipMark']['px']['y']
 
    return bldRootTipPointData

# calculate the distance from blade root point to blade root imageCener or blade tip point to blade tip imgCenter, then compensate them to bld lenth vlaue
def deltDistanceFromImgCenterToTargetPoint(bldIndex, pathIndex, imgData, targetPoint):
    cameraDistance = float(imgData['MeasuredDistanceToBlade'])
    cameraFOV = 18.2    #degree
    imgRealWidth = cameraDistance * math.tan(math.radians(cameraFOV/2))*3/math.sqrt(13)
    imgRealHight = cameraDistance * math.tan(math.radians(cameraFOV/2))*2/math.sqrt(13)
    
    deltXRatio = targetPoint[0] - 0.5
    deltYRatio = targetPoint[1] - 0.5
    
    deltX = imgRealWidth*deltXRatio
    deltY = imgRealHight*deltYRatio
    
    if (bldIndex == 0 and (pathIndex == 0 or pathIndex == 3)) or (bldIndex == 2 and (pathIndex == 1 or pathIndex == 2)):
        if deltX < 0:
            return -1 * math.sqrt(deltX*deltX + deltY*deltY)
        else:
            return math.sqrt(deltX*deltX + deltY*deltY)
    elif (bldIndex == 0 and (pathIndex == 1 or pathIndex == 2)) or (bldIndex == 2 and (pathIndex == 0 or pathIndex == 3)):
        if deltY < 0:
            return -1 * math.sqrt(deltX*deltX + deltY*deltY)
        else:
            return math.sqrt(deltX*deltX + deltY*deltY)
    elif bldIndex == 1:  #for, y's positive direction is from up to down
        if deltY < 0:
            return math.sqrt(deltX*deltX + deltY*deltY)
        else:
            return -1 * math.sqrt(deltX*deltX + deltY*deltY)

            
if __name__ == '__main__':
    print("hello world!")
    csvPath = "/home/lewisliu/Clobotics/Codes/CVTestCodes/30TensorFlow/data/Blade_Inspection_Upload_File_Insp01.csv"
    
    csvData = loadCsv(csvPath)
    print(csvData[0])
    
    turbineData = buildPaths(csvData)
#    print(turbineData)
    
    bldRootTipPointData =  buildBldRootTipPointData()

#    calculate bld lenth
    for bladeIndex in range(3):
        for pathIndex in range(4):
            print("***bld: {}, path: {}***".format(bladeIndex, pathIndex))
            pathData = turbineData[bladeIndex][pathIndex]
            numImgs = len(pathData)
            bldRootImgData = pathData[0]
            bldTipImgData = pathData[numImgs - 1]
            
            assert bldRootImgData["Index"] == str(0), "Root img index isn't 0 at bld {}, path {}, Index: {}".format(bladeIndex, pathIndex, bldRootImgData["Index"])
            assert bldTipImgData["Index"] == str(numImgs - 1), "Tip img index isn't {}".format(numImgs - 1)
            
#            if from tip to root, inverse root image and tip image
            if bldRootImgData["SequenceDirection"] == "TipToRoot":
                bldRootImgData = pathData[numImgs - 1]
                bldTipImgData = pathData[0]
                
#            find bldRoot img and bldTip img, map them in 3D space
            rootFlightXYZ, rootImgXYZ = img3DMap(bldRootImgData, bldRootImgData)
#            print("rootDroneXYZ: {}, {}, {}".format(rootFlightXYZ[0], rootFlightXYZ[1], rootFlightXYZ[2]))
            tipFlightXYZ, tipImgXYZ = img3DMap(bldTipImgData, bldRootImgData)
#            print("tipDroneXYZ: {}, {}, {}".format(tipFlightXYZ[0], tipFlightXYZ[1], tipFlightXYZ[2]))
            
            flightLen = np.sqrt(np.power(rootFlightXYZ[0]-tipFlightXYZ[0], 2) + np.power(rootFlightXYZ[1] - tipFlightXYZ[1], 2) + np.power(rootFlightXYZ[2] - tipFlightXYZ[2], 2))
            
            print("blade {}, path {} 's flight length value: {}".format(bladeIndex, pathIndex, flightLen))
            
            pathLenBasedOnImgCenter =  np.sqrt(np.power(rootImgXYZ[0]-tipImgXYZ[0], 2) + np.power(rootImgXYZ[1] - tipImgXYZ[1], 2) + np.power(rootImgXYZ[2] - tipImgXYZ[2], 2))
            print("blade {}, path {} 's path length value based on center point: {}".format(bladeIndex, pathIndex, pathLenBasedOnImgCenter))
            
            deltRootPointDistance = deltDistanceFromImgCenterToTargetPoint(bladeIndex, pathIndex, bldRootImgData, bldRootTipPointData[bladeIndex][pathIndex][0])
            deltTipPointDistance = deltDistanceFromImgCenterToTargetPoint(bladeIndex, pathIndex, bldRootImgData, bldRootTipPointData[bladeIndex][pathIndex][1])
            
            pathLen = pathLenBasedOnImgCenter - deltRootPointDistance + deltTipPointDistance
#            print("deltRoot: {}, deltTip: {}".format(deltRootPointDistance, deltTipPointDistance))
            print("blade {}, path {} 's path length value based on target point: {}".format(bladeIndex, pathIndex, pathLen))
            
            print("******bldLenth: {}******".format(pathLen))
        print("\n")
            
            

                
    
    
    
    