import cv2
import numpy as np

imgPath = "/media/lewisliu/HDD/Clobotics/WindPower/Defect/DefectInfo/data/673-211-1/defect_ccc85730-e423-11e8-a798-5bd13af6cc32.jpg"

img = cv2.imread(imgPath)
print img.shape

point1 = [0, 0]
point2 = [5, 0]
paintColor = (0, 0, 255)
cv2.line(img, tuple(point1), tuple(point2), paintColor, 1)
point1[1] = 3
point2[1] = 3
cv2.line(img, tuple(point1), tuple(point2), paintColor, 1)

font = cv2.FONT_HERSHEY_SIMPLEX
i = 3
unitSize = 6
while i < 400:
    i += 3
    point1[0] = 0
    point1[1] = i
    point2[0] = 5
    point2[1] = i
    currentValue = i * unitSize
    if currentValue % 180 == 0:
        point2[0] = 10
        cv2.line(img, tuple(point1), tuple(point2), paintColor, 1)
        point2[0] = 12
        point2[1] += 4
        text = "%d"%(currentValue/10)
        cv2.putText(img, text, tuple(point2),font, 0.4, (0,0,255), 1)
        
        if currentValue == 2340:
            point2[0] = 40
            cv2.putText(img, 'cm', tuple(point2),font, 0.4, (0,0,255), 1)
    else:
        cv2.line(img, tuple(point1), tuple(point2), paintColor, 1)
    
##* draw vertical line
i = 3
while i < 600:
    i += 3
    point1[0] = i
    point1[1] = 0
    point2[0] = i
    point2[1] = 5
    currentValue = i * unitSize
    if currentValue % 180 == 0:
        point2[1] = 10
        cv2.line(img, tuple(point1), tuple(point2), paintColor, 1)
        # point2[0] += 4
        point2[0] -= 8
        point2[1] = 20
        text = "%d"%(currentValue/10)
        cv2.putText(img, text, tuple(point2), font, 0.4, (0, 0, 255), 1)
        # img += textImg
        if currentValue == 3420:
            point2[1] = 32
            cv2.putText(img, 'cm', tuple(point2),font, 0.4, (0,0,255), 1)
    else:
        
        cv2.line(img, tuple(point1), tuple(point2), paintColor, 1)


cv2.imshow('image', img)
cv2. waitKey(0)