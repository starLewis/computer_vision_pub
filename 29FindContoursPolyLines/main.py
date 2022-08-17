import numpy as np
import cv2
from scipy.ndimage.filters import gaussian_filter
import math
import copy

USESMOOTH = False

def changeAngleTo180(angle):
    if angle == None:
        return 0
    while angle < 0:
        angle += 180

    while angle >= 180:
        angle -= 180

    return angle

if __name__ == "__main__":
    #* find contours
    imgPath = "pic/DSC05845.png"
    storePath = "pic/hullLine_011.jpg"
    imgRotation = -60
    img = cv2.imread(imgPath)
    img = cv2.resize(img, (1200, 800))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # img = cv2.erode(img, (5,5), 5)
    # img = cv2.medianBlur(img,5)

    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    image, contours, hierarchy = cv2.findContours(thresh, 3, 2)
    
    maxSize = 0
    cnt = None
    for cntI in contours:
        if len(cntI) > maxSize:
            maxSize = len(cntI)
            cnt = copy.deepcopy(cntI)

    cntBlur = []
    if USESMOOTH:
        #* smooth contours
        filterRadius = 1
        filterSize = 2*filterRadius + 1
        sigma = 1
        lenCC = len(cnt) + 2 * filterRadius
        idx = len(cnt) - filterRadius
        xCnt = []
        yCnt = []
        for i in range(lenCC):
            xCnt.append(cnt[(idx + i)%len(cnt)][0][0])
            yCnt.append(cnt[(idx + i)%len(cnt)][0][1])

        #* filter 1-D signals
        xCntBlur = None
        yCntBlur = None
        # cv2.GaussianBlur(np.array(xCnt), (3 ,3), sigma)
        # cv2.GaussianBlur(np.array(yCnt), (3, 3), sigma)
        # xCntBlur = cv2.medianBlur(np.array(xCnt), 3)
        # yCntBlur = cv2.medianBlur(np.array(yCnt), 3)
        xCntBlur = gaussian_filter(xCnt, sigma)
        yCntBlur = gaussian_filter(yCnt, sigma)

        #* build smoothed contour
        for i in range(len(cnt) + filterRadius):
            cntBlur.append([[xCntBlur[i], yCntBlur[i]]])

        print len(cntBlur)
    # print cntBlur
    else:
        cntBlur = copy.deepcopy(cnt)

    #* find hull
    hull = cv2.convexHull(np.array(cntBlur))
    # print(hull)

    #* filter lines by rotation
    targetR = 90 - imgRotation
    targetR = changeAngleTo180(targetR)
    gabAngle = 35

    refPt = None
    curPt = None
    candidateLines = []
    for i in range(len(hull)):
        if i == 0:
            refPt = hull[len(hull)-1][0]
            curPt = hull[0][0]
        else:
            refPt = hull[i-1][0]
            curPt = hull[i][0]

        curAngle = math.atan2(curPt[1]-refPt[1], curPt[0]-refPt[0])
        curAngle *= (180/math.pi)
        curAngle = changeAngleTo180(curAngle)

        if abs(curAngle - targetR) <= gabAngle:
            distance = np.sqrt((curPt[0]-refPt[0])*(curPt[0]-refPt[0]) + (curPt[1]-refPt[1])*(curPt[1]-refPt[1]))
            candidateLines.append([refPt, curPt, distance, curAngle])
    sortedCandidates = sorted(candidateLines,key = lambda candi: candi[2], reverse = True)
    # print len(sortedCandidates)

    # curAngle = math.atan2(1.753, 1)
    # curAngle *= (180/math.pi)
    # curAngle = changeAngleTo180(curAngle)
    # print("curAngle:%d"%curAngle)

    #* draw hull
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    cv2.polylines(image, [hull], True, (0, 255, 0), 8)

    candidateTargetAngle = 0
    num = 0
    for i in range(len(sortedCandidates)):
        if i <= 1:
            print(sortedCandidates[i])
            cv2.line(image, tuple(sortedCandidates[i][0]), tuple(sortedCandidates[i][1]), (0,0,255),5)
            candidateTargetAngle += sortedCandidates[i][3]
            num += 1
    if num > 0:
        candidateTargetAngle /= num

    # curGabAngle = candidateTargetAngle - targetRotation
    # curFittedLineAngle = targetR + curGabAngle
    print("imgRotation: %.3f, curFittedLineAngle: %.3f"%(imgRotation, candidateTargetAngle))
    text = "curFittedLineAngle: %.3f Degree" % candidateTargetAngle
    cv2.putText(image, text, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 2)

    cv2.imshow("hullImg", image)
    cv2.imwrite(storePath, image)
    cv2.waitKey()

    print("hello world")