// build at 2018/2/3


#include <iostream>
#include <opencv2/opencv.hpp>
#include "../../AutoFlightCodes/catkin_ws/src/WindAppCore/DroneCVSDK/CvTask/Common/inc/CvLineOperator.hpp"
#include "../../AutoFlightCodes/catkin_ws/src/WindAppCore/CppFun/inc_pub/CUtil.h"

//** flip a image
//int main(int argc, char** argv)
//{
//    cv::Mat image;
//    std::string imagePath = "/home/liuxun/Clobotics/Data/CvDataOwnCloud/AutoFlight/AE/log_20180309/AE/cameraImage_928.jpg";
//
//    image = cv::imread(imagePath);
//    cv::flip(image,image,1);
//
////    int resizeWidth = 1018;
////    float ratio = resizeWidth / image.cols;
////    int resizeHeight = image.rows * ratio;
////    cv::resize(image,image,cv::Size(resizeWidth,resizeHeight));
//
//    cv::imshow("flip",image);
//    cv::waitKey();
//    cv::imwrite(imagePath,image);
//
//    return 0;
//}

//** test contours
std::string m_logChannel = "AE";
int fitLine2D(std::vector<cv::Point2f> &pointClouds, cv::Vec4f &line);
int findBladeCenterPointCooIndex(cv::Mat &image, cv::Mat &xyzdMat, cv::Point &bladeCenterPointCooIndex);
int fitBladeCenterPointLine(cv::Mat& xyzdMat, cv::Mat &distanceMark, cv::Point &boundingRectCenter, cv::Rect& boundingRect,
                            cv::Vec4f &bladeCenterPointLine);
float yCompFromLog = 0;

int main(int argc, char **argv) {

    cv::Mat src(20, 320, CV_8UC3);
//    std::cout<<src.type()<<std::endl;
    cv::Mat grey;
    std::string framePath = "/media/liuxun/HDD/Clobotics/Data/CvDataOwnCloud/AutoFlight/AE/log_20180320/AE_201803201445/cameraImage_997.jpg";
    std::string imagePath = "/media/liuxun/HDD/Clobotics/Data/CvDataOwnCloud/AutoFlight/AE/log_20180320/AE_201803201445/distanceMarker_997.jpg";
    yCompFromLog = 32.551567;
    src = cv::imread(imagePath);
    cv::Mat frameImage = cv::imread(framePath);

    cv::cvtColor(src, grey, CV_BGR2GRAY);
//    cv::erode(grey,grey,cv::Mat());
//    cv::erode(grey,grey,cv::Mat());

//    cv::dilate(grey,grey,cv::Mat());
//    cv::dilate(grey, grey, cv::Mat());
//    cv::dilate(grey, grey, cv::Mat());

    std::vector<std::vector<cv::Point2i>> contours;
    std::vector<cv::Vec4i> hierarchy;

    cv::findContours(grey, contours, hierarchy, CV_RETR_CCOMP, CV_CHAIN_APPROX_NONE);
    std::vector<cv::RotatedRect> minAreas;

    for (int i = 0; i < contours.size(); i++) {
        std::cout << "contours.size: " << contours.size() << std::endl;
        cv::RotatedRect tempRect = cv::minAreaRect(contours[i]);
        cv::drawContours(src, contours, i, cv::Scalar(255, 0, 0));
        minAreas.push_back(tempRect);
    }
    std::cout << "contours.size: " << contours.size() << std::endl;

    cv::Point bladeCenterPointIndex;
    findBladeCenterPointCooIndex(frameImage,grey, bladeCenterPointIndex);
    std::cout << bladeCenterPointIndex.x << " " << bladeCenterPointIndex.y << std::endl;

    //** draw contours

    //** draw minArea
    for (int i = 0; i < minAreas.size(); i++) {
        cv::rectangle(src, minAreas[i].boundingRect(), cv::Scalar(0, 0, 255));
        cv::Point center(minAreas[i].boundingRect().x+minAreas[i].boundingRect().width/2, minAreas[i].boundingRect().y+minAreas[i].boundingRect().height/2);
        std::cout<<"out,bladecenter: "<<center.x<<" "<<center.y<<std::endl;
        cv::circle(src,center,2,cv::Scalar(0,0,255));
    }


    cv::imshow("src", src);
    cv::waitKey(0);

    return 0;
}


int findBladeCenterPointCooIndex(cv::Mat &image, cv::Mat &xyzdMat, cv::Point &bladeCenterPointCooIndex) {
//** resize frameImage
    int cameraImageWidth = 320;
    int cameraImageHeight = 240;
    cv::resize(image,image,cv::Size(cameraImageWidth,cameraImageHeight));

    cv::Point cameraImageCenterPoint(cameraImageWidth/2, cameraImageHeight/2);
    cv::Point bladeCenterPoint = cameraImageCenterPoint;

//** build distanceMarker image for xyzdMat
    cv::Mat distanceMark(xyzdMat.rows, xyzdMat.cols, CV_8UC1, cv::Scalar(0));
//for(int i=0;i<xyzdMat.rows;i++)
//{
//for(int j=0;j<xyzdMat.cols;j++)
//{
//if(xyzdMat.at<cv::Vec4f>(i,j)[3] > 0.1 && xyzdMat.at<cv::Vec4f>(i,j)[3] <= 20)
//{
//distanceMark.at<uchar>(i,j) = 255;
//}f
//}
//}
////** erode to delete single points
//cv::erode(distanceMark,distanceMark,cv::Mat());
//cv::erode(distanceMark,distanceMark,cv::Mat());
////** dilate to smooth the link of two near contours
//cv::dilate(distanceMark,distanceMark,cv::Mat());
//cv::dilate(distanceMark,distanceMark,cv::Mat());
    xyzdMat.copyTo(distanceMark);

//** find the contours
    std::vector<std::vector<cv::Point> > contours;
    std::vector<cv::Vec4i> hierarchy;
    cv::findContours(distanceMark, contours, hierarchy, CV_RETR_CCOMP, CV_CHAIN_APPROX_NONE);

    double maxContourArea = 0;
    int maxAreaIndex = -1;
    for (int i = 0; i < contours.size(); i++) {
        double curArea = cv::contourArea(contours[i]);
        if (curArea > maxContourArea) {
            maxContourArea = curArea;
            maxAreaIndex = i;
        }
    }

    if (maxAreaIndex >= 0 && maxAreaIndex < contours.size()) {
        cv::Rect boundingRect = cv::boundingRect(contours[maxAreaIndex]);

        cv::Point boundingRectCenter;
        boundingRectCenter.x = boundingRect.x + boundingRect.width / 2;
        boundingRectCenter.y = boundingRect.y + boundingRect.height / 2;

        float FovWidthDegreeOfDepthMat = 60; //** degree
        float FovWidthDegreeOfCameraMat = 15.088549;  //**degree
        float FovHeightDegreeOfCameraMat = 11.345026;   //**degree
        float normalizationWidthOfDepthMat = FovWidthDegreeOfDepthMat*cameraImageWidth/FovWidthDegreeOfCameraMat;
        float normalizationRatioOfDepthMat = normalizationWidthOfDepthMat / 320;
        std::cout<<"normalizationRatioOfDepthMat: "<<normalizationRatioOfDepthMat<<std::endl;

        cv::Point depthMatCenterPoint(160,10);
        cv::Point2f degreeCalib(320/60,10/4);

        cv::Point2f compensationDegreeForLadar(-2,-1);
        std::cout<<"boundingRectCenter, x,y: "<<boundingRectCenter.x<<" "<<boundingRectCenter.y<<std::endl;

//        if(boundingRectCenter.x > 160)
//        {
//            compensationDegreeForLadar.x = 0;
//            compensationDegreeForLadar.y = 0;
//        }

        depthMatCenterPoint.x = depthMatCenterPoint.x + degreeCalib.x*compensationDegreeForLadar.x;
        depthMatCenterPoint.y = depthMatCenterPoint.y + degreeCalib.y*compensationDegreeForLadar.y;
        std::cout<<"depthMatCenterPoint: "<<depthMatCenterPoint.x<<" "<<depthMatCenterPoint.y<<std::endl;

//** calculate delt distance from the center of depth mat
        cv::Point deltDistance(boundingRectCenter.x - depthMatCenterPoint.x, boundingRectCenter.y - depthMatCenterPoint.y); //** the depth mat's 320x20
//** normalized to camera's image
        deltDistance.x *= normalizationRatioOfDepthMat;
        deltDistance.y *= normalizationRatioOfDepthMat;
        std::cout<<"deltDistance: "<<deltDistance.x<<" "<<deltDistance.y<<std::endl;

//** calculate the blade point center in camera's image
        bladeCenterPoint.x = cameraImageCenterPoint.x + deltDistance.x;
        bladeCenterPoint.y = cameraImageCenterPoint.y + deltDistance.y;

        //** ce30 at the 10cm down from the camera, calculate Y compensation for the 10cm installation position
        float positionInstall = 0.1; //unit: m
        float distanceToBlade = 10; //unit: m
        float yCompValue = positionInstall*cameraImageHeight / (distanceToBlade * tan(FovHeightDegreeOfCameraMat*3.14/180));
        yCompValue = yCompFromLog;
        std::cout<<"yCompValue: "<<yCompValue<<std::endl;
        bladeCenterPoint.y += yCompValue;

        //**calculate blade angle for bladeCenterPoint's value is beyond the image's size(cameraImageWidth/cameraImageHeight);
        cv::Vec4f bladeCenterPointLine;
        fitBladeCenterPointLine(xyzdMat,distanceMark,boundingRectCenter,boundingRect,bladeCenterPointLine);
        std::cout<<"bladeCenterPointLine: "<<bladeCenterPointLine[0]<<" "<<bladeCenterPointLine[1]<<" "<<bladeCenterPoint.x<<" "<<bladeCenterPoint.y<<std::endl;

        wicv::Line line = wicv::CvLineOperator::GetLineOfVxyXY0(bladeCenterPointLine[0],bladeCenterPointLine[1],bladeCenterPoint.x,bladeCenterPoint.y);

        wicv::Point crossLeftVerticalPoint;
        crossLeftVerticalPoint.x = 0;
        crossLeftVerticalPoint.y = UNKNOWNPARAM;
        wicv::CvLineOperator::GetPointInLine(line,crossLeftVerticalPoint.x,crossLeftVerticalPoint.y,crossLeftVerticalPoint);
        wicv::Point crossRightVerticalPoint;
        crossRightVerticalPoint.x = cameraImageWidth-1;
        crossRightVerticalPoint.y = UNKNOWNPARAM;
        wicv::CvLineOperator::GetPointInLine(line,crossRightVerticalPoint.x,crossRightVerticalPoint.y,crossRightVerticalPoint);

        wicv::Point crossTopHorizontalPoint;
        crossTopHorizontalPoint.x = UNKNOWNPARAM;
        crossTopHorizontalPoint.y = 0;
        wicv::CvLineOperator::GetPointInLine(line, crossTopHorizontalPoint.x, crossTopHorizontalPoint.y, crossTopHorizontalPoint);
        wicv::Point crossBottomHorizontalPoint;
        crossBottomHorizontalPoint.x = UNKNOWNPARAM;
        crossBottomHorizontalPoint.y = cameraImageHeight-1;
        wicv::CvLineOperator::GetPointInLine(line, crossBottomHorizontalPoint.x, crossBottomHorizontalPoint.y, crossBottomHorizontalPoint);

        bool isBladeCenterPointTempValid = false;
        cv::Point bladeCenterPointTemp(0,0);
        if(crossLeftVerticalPoint.y != UNKNOWNPARAM && crossRightVerticalPoint.y != UNKNOWNPARAM && crossTopHorizontalPoint.x != UNKNOWNPARAM && crossBottomHorizontalPoint.x != UNKNOWNPARAM)
        {
            int validNum = 0;
            if(crossLeftVerticalPoint.y >= 0 && crossLeftVerticalPoint.y < cameraImageHeight)
            {
                bladeCenterPointTemp.x += crossLeftVerticalPoint.x;
                bladeCenterPointTemp.y += crossLeftVerticalPoint.y;
                validNum++;
            }
            if(crossRightVerticalPoint.y >= 0 && crossRightVerticalPoint.y < cameraImageHeight)
            {
                bladeCenterPointTemp.x += crossRightVerticalPoint.x;
                bladeCenterPointTemp.y += crossRightVerticalPoint.y;
                validNum++;
            }
            if(crossTopHorizontalPoint.x >= 0 && crossTopHorizontalPoint.x < cameraImageWidth)
            {
                bladeCenterPointTemp.x += crossTopHorizontalPoint.x;
                bladeCenterPointTemp.y += crossTopHorizontalPoint.y;
                validNum++;
            }
            if(crossBottomHorizontalPoint.x >= 0 && crossBottomHorizontalPoint.x < cameraImageWidth)
            {
                bladeCenterPointTemp.x += crossBottomHorizontalPoint.x;
                bladeCenterPointTemp.y += crossBottomHorizontalPoint.y;
                validNum++;
            }
            if(validNum != 2)
            {
                isBladeCenterPointTempValid = false;
            }else
            {
                isBladeCenterPointTempValid = true;
                bladeCenterPointTemp.x /= 2;
                bladeCenterPointTemp.y /= 2;
            }
        }else if(crossLeftVerticalPoint.y != UNKNOWNPARAM && crossRightVerticalPoint.y != UNKNOWNPARAM)
        {
            isBladeCenterPointTempValid = true;
            bladeCenterPointTemp.x = (crossLeftVerticalPoint.x + crossRightVerticalPoint.x)/2;
            bladeCenterPointTemp.y = (crossLeftVerticalPoint.y + crossRightVerticalPoint.y)/2;
        }else if(crossTopHorizontalPoint.x != UNKNOWNPARAM && crossBottomHorizontalPoint.x != UNKNOWNPARAM)
        {
            isBladeCenterPointTempValid = true;
            bladeCenterPointTemp.x = (crossTopHorizontalPoint.x + crossBottomHorizontalPoint.x)/2;
            bladeCenterPointTemp.y = (crossTopHorizontalPoint.y + crossBottomHorizontalPoint.y)/2;
        }

        if(isBladeCenterPointTempValid)
        {
            bladeCenterPoint = bladeCenterPointTemp;
        }

        if(bladeCenterPoint.x < 0 || bladeCenterPoint.x >= cameraImageWidth || bladeCenterPoint.y < 0 || bladeCenterPoint.y >= cameraImageHeight)
        {
            bladeCenterPoint.x = cameraImageWidth>>1;
            bladeCenterPoint.y = cameraImageHeight>>1;
        }
//        cu::chlog::info(m_logChannel,std::string("bladeCenterPoint after line improvement: " + std::to_string(bladeCenterPoint.x) + ", " + std::to_string(bladeCenterPoint.y)));
        std::cout<<"bladeCenterPoint after line improvement: "<<bladeCenterPoint.x <<" "<<bladeCenterPoint.y<<std::endl;

        bladeCenterPointCooIndex.x = 16.0 * bladeCenterPoint.x / cameraImageWidth;
        bladeCenterPointCooIndex.y = 12.0 * bladeCenterPoint.y / cameraImageHeight;
    } else {
        bladeCenterPointCooIndex.x = 7;
        bladeCenterPointCooIndex.y = 5;
    }

#if 1
    float ratio = 1.0*cameraImageWidth / 16;

    cv::line(image,cv::Point(bladeCenterPointCooIndex.x*ratio,0),cv::Point(bladeCenterPointCooIndex.x*ratio,image.rows-1),cv::Scalar(255,0,0));
    cv::line(image,cv::Point(bladeCenterPointCooIndex.x*ratio+ratio-1,0),cv::Point(bladeCenterPointCooIndex.x*ratio+ratio-1,image.rows-1),cv::Scalar(255,0,0));
    cv::line(image,cv::Point(0,bladeCenterPointCooIndex.y*ratio),cv::Point(image.cols-1,bladeCenterPointCooIndex.y*ratio),cv::Scalar(255,0,0));
    cv::line(image,cv::Point(0,bladeCenterPointCooIndex.y*ratio+ratio-1),cv::Point(image.cols-1,bladeCenterPointCooIndex.y*ratio+ratio-1),cv::Scalar(255,0,0));

    cv::circle(image,bladeCenterPoint,2,cv::Scalar(0,0,255));
    cv::imshow("blade",image);
//    cv::waitKey();
#endif

#if 0
    //**store distanceMarker image
        std::string picName_sub = "distanceMarker_";
        std::stringstream ss00;
        ss00<<m_frameIndex;
        std::string picName = picName_sub + ss00.str() + ".jpg";

        std::string writePath = "/home/up2/CvTaskData/AE/" + picName;
    //    std::string writePath = "/media/liuxun/HDD/Clobotics/Data/CvDataOwnCloud/AutoFlight/Turbine/Images/" + picName;
        cv::imwrite(writePath,distanceMark);

        //** store camera image
        std::string picName_image = "cameraImage_";
        std::string picNameImage = picName_image + ss00.str() + ".jpg";
        std::string writePathImage = "/home/up2/CvTaskData/AE/" + picNameImage;

        cv::Mat curFrameTemp;
        cv::resize(m_curFrame,curFrameTemp,cv::Size(m_curFrame.cols/4,m_curFrame.rows/4));
        cv::imwrite(writePathImage,curFrameTemp);
#endif

    return 0;
}

int fitBladeCenterPointLine(cv::Mat& xyzdMat, cv::Mat &distanceMark, cv::Point &boundingRectCenter, cv::Rect& boundingRect,
                                                cv::Vec4f &bladeCenterPointLine)
{
    //** find the center line points

    //**find the center line of blade contour in distanceMark
    std::vector<cv::Point2f> centerLinePoints;
    int curY = boundingRectCenter.y;
    int curX = boundingRectCenter.x;
    int curXLeft = curX, curXRight = curX;
    for(curY = boundingRectCenter.y; curY >= boundingRect.y; curY--)
    {
        curXLeft = curX;
        curXRight = curX;
        while(curXLeft >= boundingRect.x && curXLeft >= 0 && distanceMark.at<uchar>(curY,curXLeft) >= 200)
        {
            curXLeft--;
        }
        curXLeft++;
        if(curXLeft < 2)
        {
            continue;
        }

        while(curXRight < boundingRect.x + boundingRect.width && curXRight < distanceMark.cols && distanceMark.at<uchar>(curY, curXRight) >= 200)
        {
            curXRight++;
        }
        curXRight--;
        if(curXRight > distanceMark.cols - 3)
        {
            continue;
        }

        int curWidthThreshold =  xyzdMat.at<cv::Vec4f>(curY,curX)[3]*0.00327; //one pixel->real size: 2*pi*distance/6/320
        if(curWidthThreshold > 0)
        {
            curWidthThreshold = 0.8/curWidthThreshold;
        }
        if(curWidthThreshold >15)
        {
            curWidthThreshold = 15;
        }
        if(curWidthThreshold < 5)
        {
            curWidthThreshold = 3;
        }
        if(curXRight - curXLeft >= curWidthThreshold)
        {
            curX = (curXLeft + curXRight)>>1;
            centerLinePoints.push_back(cv::Point2f(curX,curY));
        }
    }
    for(curY = boundingRectCenter.y + 1, curX = boundingRectCenter.x; curY < boundingRect.y + boundingRect.height;curY++)
    {
        curXLeft = curX;
        curXRight = curX;
        while(curXLeft >= boundingRect.x && curXLeft >= 0 && distanceMark.at<uchar>(curY, curXLeft) >= 200)
        {
            curXLeft--;
        }
        curXLeft++;
        if(curXLeft < 2)
        {
            continue;
        }
        while(curXRight < boundingRect.x + boundingRect.width && curXRight < distanceMark.cols && distanceMark.at<uchar>(curY, curXRight) >= 200)
        {
            curXRight++;
        }
        curXRight--;
        if(curXRight > distanceMark.cols - 3)
        {
            continue;
        }
        int curWidthThreshold =  xyzdMat.at<cv::Vec4f>(curY,curX)[3]*0.00327; //one pixel->real size: 2*pi*distance/6/320
        if(curWidthThreshold > 0)
        {
            curWidthThreshold = 0.8/curWidthThreshold;
        }
        if(curWidthThreshold >15)
        {
            curWidthThreshold = 15;
        }
        if(curWidthThreshold < 5)
        {
            curWidthThreshold = 5;
        }
        if(curXRight - curXLeft >= curWidthThreshold)
        {
            curX = (curXLeft + curXRight)>>1;
            centerLinePoints.push_back(cv::Point2f(curX,curY));
        }

    }

    if(centerLinePoints.size() >= 18)
    {
        cv::Vec4f line;
        fitLine2D(centerLinePoints, line);
        bladeCenterPointLine = line;
    }else
    {
        return 1000;
    }


    return 0;
}

int fitLine2D(std::vector<cv::Point2f> &pointClouds, cv::Vec4f &line)
{
    int pointsNum = pointClouds.size();
    cv::Mat pointMat(1,pointsNum,CV_32FC2);

    for(int i=0;i<pointsNum;i++)
    {
        pointMat.at<cv::Vec2f>(0,i)[0] = pointClouds[i].x;
        pointMat.at<cv::Vec2f>(0,i)[1] = pointClouds[i].y;
    }

    cv::fitLine(pointMat,line,CV_DIST_L2,0,0.01,0.01);

    return 0;
}
