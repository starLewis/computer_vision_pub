//
// Created by liuxun on 18-1-13.
//

#ifndef CPPFUN_CVVECTORIMGSSHOW_H
#define CPPFUN_CVVECTORIMGSSHOW_H
#include <vector>
#include <iostream>
#include <opencv2/opencv.hpp>

namespace wicv{
    class CvVectorImgsShow
    {
    public:
        CvVectorImgsShow();
        ~CvVectorImgsShow();

        static int buildPanoImage(std::vector<cv::Mat>& imgs, std::vector<std::string>& strs, cv::Mat& panoImg);

        static int storeVideo(std::string& storeVideoPath, int videoFrameWidth, int videoFrameHeight, int videoFPS, cv::Mat& videoFrame);

        static void storeVideoRelease();

    };

}

#endif //CPPFUN_CVVECTORIMGSSHOW_H
