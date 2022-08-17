# -*- coding: utf-8 -*-

# Standard imports
import cv2
import numpy as np;
 
# Read image
im = cv2.imread("/home/lewisliu/Downloads/1270922150.jpg", cv2.IMREAD_GRAYSCALE)
im = cv2.resize(im, (im.shape[1], im.shape[0]))
 
# params = cv2.SimpleBlobDetector_Params()
# params.filterByColor = True
# params.blobColor = 0

# params.filterByArea = True
# params.minArea = 0

# params.filterByCircularity = True
# params.minCircularity = 0.1

# params.filterByConvexity = True
# params.minConvexity = 0.87

# params.filterByInertia = True
# params.minInertiaRatio = 0.01


# Set up the detector with default parameters.
detector = cv2.SimpleBlobDetector_create()
# detector = cv2.ORB_create()
 
# Detect blobs.
keypoints = detector.detect(im)
print(keypoints[0])
 
# Draw detected blobs as red circles.
# cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
 
# Show keypoints
cv2.imshow("Keypoints", im_with_keypoints)
# cv2.imwrite("blob_orb.jpg",im_with_keypoints)
cv2.imwrite("blob_simple_h.jpg",im_with_keypoints)
cv2.waitKey(0)

# import cv2

# cap = cv2.VideoCapture(1)
# while True:
#     ret, frame = cap.read()
#     cv2.imshow("Video", frame)

#     if cv2.waitKey(10) == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()