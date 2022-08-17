#include <iostream>
#include <vector>
#include <opencv2/opencv.hpp>
#include "../inc/CvVectorImgsShow.h"

int main()
{

    std::vector<std::string> strs;
    std::string str1 = "Hello str1!";
    std::string str2 = "Hello str2!";

    strs.push_back(str1);
    strs.push_back(str2);


    std::vector<cv::Mat> imgs;
    cv::Mat resImage;

    cv::Mat img1(200,200,CV_8UC3,cv::Scalar(255,0,0));
    cv::Mat img2(200,200,CV_8UC3,cv::Scalar(0,255,0));
    cv::Mat img3(200,200,CV_8UC3,cv::Scalar(0,0,255));
    cv::Mat img4(200,200,CV_8UC3,cv::Scalar(0,255,255));
    cv::Mat img5(200,200,CV_8UC3,cv::Scalar(255,255,0));

    imgs.push_back(img1);
    imgs.push_back(img2);
    imgs.push_back(img3);
    imgs.push_back(img4);
    imgs.push_back(img5);

    wicv::CvVectorImgsShow::buildPanoImage(imgs,strs,resImage);

    cv::imshow("resImg",resImage);

    cv::waitKey(0);
    std::cout<<"hello world!"<<std::endl;

    return 0;

}