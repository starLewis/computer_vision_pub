# -*- coding: utf-8 -*-
#!/usr/bin/env python

import numpy as np
import cv2

drawing = False
mode = True
ix, iy = -1, -1
px, py = -1, -1

def draw_rect(event, x, y, flags, param):
    global ix, iy, drawing, px, py

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix,iy = x,y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            cv2.rectangle(img, (ix, iy), (px, py), (0,0,0),0)
            cv2.rectangle(img, (ix, iy), (x, y), (0,255,0),0)
            px,py = x,y
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.rectangle(img, (ix, iy), (x, y), (0,255,0),0)
        cv2.putText(img,'000', (ix, iy), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 2)
        px,py = -1,-1

img = np.zeros((512, 512, 3), np.uint8)
cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_rect)

while(1):
    cv2.imshow('image', img)
    k = cv2.waitKey(1) & 0xFF
    if k == ord('q'):
        break
    elif k == 27: 
        break

cv2.destroyAllWindows()