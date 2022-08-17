//
// Created by liuxun on 18-1-13.
//

#include "../inc/CvVectorImgsShow.h"
wicv::CvVectorImgsShow::CvVectorImgsShow()
{

}

wicv::CvVectorImgsShow::~CvVectorImgsShow()
{

}

//** build panorma image from several images and serverl strings
int wicv::CvVectorImgsShow::buildPanoImage(std::vector<cv::Mat> &imgs, std::vector<std::string> &strs,
                                           cv::Mat &panoImg) {
    int minHeight = 200;

    //** construct imgs show
    bool hasImgs = false;
    int unitImgWidth = 100;
    int unitImgHeight = 100;
    cv::Mat imgsMat(unitImgHeight, unitImgWidth, CV_8UC3, cv::Scalar(128, 128, 128));
    if (imgs.size() <= 0) {
        hasImgs = false;
    } else {
        hasImgs = true;

        unitImgWidth = imgs[0].cols;
        unitImgHeight = imgs[0].rows;

        int row = 1;
        int col = 1;
        if (imgs.size() <= 2) {
            row = 1;
            col = imgs.size();
        } else {
            row = 2;
            col = imgs.size() / 2.0 + 0.5;
        }

        cv::resize(imgsMat, imgsMat, cv::Size(col * unitImgWidth, row * unitImgHeight));
        int halfImgsNum = imgs.size() / 2.0 + 0.5;
        for (int i = 0; i < imgs.size(); i++) {
            if (imgs.size() <= 2) {
                row = 0;
                col = i;
            } else {
                if (i < halfImgsNum) {
                    row = 0;
                    col = i;
                } else {
                    row = 1;
                    col = i - halfImgsNum;
                }
            }

            if (imgs[i].rows != unitImgHeight || imgs[i].cols != unitImgWidth) {
                cv::resize(imgs[i], imgs[i], cv::Size(unitImgWidth, unitImgHeight));
            }

            cv::Mat curImg = imgs[i];
            if(curImg.channels() == 1)
            {
                cv::cvtColor(curImg,curImg,CV_GRAY2BGR);
            }

            if(curImg.channels() == 3)
            {
                curImg.copyTo(imgsMat(cv::Rect(col * unitImgWidth, row * unitImgHeight, unitImgWidth, unitImgHeight)));
            }

//            imgs[i].copyTo(imgsMat(cv::Rect(col * unitImgWidth, row * unitImgHeight, unitImgWidth, unitImgHeight)));
        }
    }


    //** construct strs show
    bool hasStrs = false;
    cv::Mat strsMat(360, minHeight, CV_8UC3, cv::Scalar(128, 128, 128));
    cv::Point currentCoordinate(20, 20);
    for (int i = 0; i < strs.size(); i++) {
        hasStrs = true;
        cv::putText(strsMat, strs[i], currentCoordinate, 4, 0.6, cv::Scalar(200, 0, 200), 1);
        currentCoordinate.y += 20;
    }

    //** build panorma image
    int panormaWidth = 100;
    int panormaHeight = 100;
    cv::Mat resImg(panormaHeight, panormaWidth, CV_8UC3, cv::Scalar(128, 128, 128));
    if (hasImgs && hasStrs) {
        panormaHeight = MAX(imgsMat.rows, strsMat.rows);
        panormaWidth = imgsMat.cols + strsMat.cols;

        cv::resize(resImg, resImg, cv::Size(panormaWidth, panormaHeight));
        imgsMat.copyTo(resImg(cv::Rect(0, 0, imgsMat.cols, imgsMat.rows)));
        strsMat.copyTo(resImg(cv::Rect(imgsMat.cols, 0, strsMat.cols, strsMat.rows)));
    } else if (hasImgs) {
        imgsMat.copyTo(resImg);
    } else if (hasStrs) {
        strsMat.copyTo(resImg);
    }

    resImg.copyTo(panoImg);
}

int wicv::CvVectorImgsShow::storeVideo(std::string &storeVideoPath, int videoFrameWidth, int videoFrameHeight,
                                       int videoFPS, cv::Mat &videoFrame)
{
    //** video Writer
    static cv::VideoWriter vWrt;

    if(!vWrt.isOpened())
    {
        vWrt.open(storeVideoPath,CV_FOURCC('M','P','4','2'), videoFPS, cv::Size(videoFrameWidth,videoFrameHeight));

        if(!vWrt.isOpened())
        {
            std::cout<<"video: "<< storeVideoPath<< " write failed!"<<std::endl;

            return -1;
        }
    }

    vWrt.write(videoFrame);

    return 0;
}

void wicv::CvVectorImgsShow::storeVideoRelease()
{
    static cv::VideoWriter vWrt;
    vWrt.release();
}