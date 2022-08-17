import numpy as np
import cv2

MINFEATNUM = 5

img1 = cv2.imread("pic/twoInsps/DSC00350.JPG", 0)
img2 = cv2.imread("pic/twoInsps/DSC00731.JPG", 0)
# mask1 = cv2.imread("pic/masker/DSC05424.png")
# mask2 = cv2.imread("pic/masker/DSC05947.png")

detector = cv2.ORB_create(nfeatures=300)

imgHeight, imgWidth  = img1.shape
print imgWidth, imgHeight

# mask1 = cv2.cvtColor(mask1, cv2.COLOR_BGR2GRAY)
# mask1 = cv2.resize(mask1, (imgWidth, imgHeight))
# mask2 = cv2.cvtColor(mask2, cv2.COLOR_BGR2GRAY)
# mask2 = cv2.resize(mask2,(imgWidth, imgHeight))
# cv2.imshow("mask1",mask1)
# cv2.imshow("img1", img1)
# cv2.waitKey()

# kernel = np.ones((5,5), np.uint8)
# roi = cv2.erode(mask1, kernel, iterations = 5)
# roi = mask1

# flann_params = dict(algorithm=6,
# table_number=6,  # 12
# key_size=12,  # 20
# multi_probe_level=1)  # 2

matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

# kp1, desc1 = detector.detectAndCompute(img1, mask1)
# kp2, desc2 = detector.detectAndCompute(img2, mask2)
img1 = cv2.resize(img1, (imgWidth/4, imgHeight/4))
img2 = cv2.resize(img2, (imgWidth/4, imgHeight/4))
kp1, desc1 = detector.detectAndCompute(img1, None)
kp2, desc2 = detector.detectAndCompute(img2, None)
print(len(kp1))
print(len(kp2))

raw_matches = matcher.knnMatch(desc1, desc2, 2)  # 2

good = []
print(len(raw_matches))


for m, n in raw_matches:
    if m.distance < 0.85*n.distance:
        good.append(m)

test = []
if len(good) >= MINFEATNUM:
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    # test.append([[0,0]])
    # test.append([[3.0, 3.0]])
    # test.append([[3.2, 3.2]])
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    # print(src_pts)
    # print(np.array(test))

    print("good len: %d"%len(good))
    print(good)
    matchesMask = mask.ravel().tolist()
    print(len(matchesMask))
    print(matchesMask)
else:
    print("Not enough matches are found - %d/%d" % (len(good),MINFEATNUM))
    matchesMask = None

# matchesMask = np.ones(MINFEATNUM)
print matchesMask
draw_params = dict(matchColor = (0,255,0), # draw matches in green color
    singlePointColor = (0,0,255),
    matchesMask = matchesMask, 
    flags = 2)# draw only inliers 

vis = cv2.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)   

cv2.imshow("", vis)
cv2.imwrite("pic/face_brisk_bf_ransac_002.jpg", vis)
cv2.waitKey()
cv2.destroyAllWindows()
