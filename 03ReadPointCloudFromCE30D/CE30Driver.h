//
// Created by liuxun on 18-1-23.
//

#ifndef INC_03READPOINTCLOUDFROMCE30D_CE30DRIVER_H
#define INC_03READPOINTCLOUDFROMCE30D_CE30DRIVER_H
#include <iostream>
#include <ce30_driver/ce30_driver.h>
#include <opencv2/opencv.hpp>
using namespace ce30_driver;

namespace wicv
{
    class CE30Driver
    {
    public:
        //** construct and deconstruct
        CE30Driver();
        ~CE30Driver();

        //** singleton
        static CE30Driver* getInstance();

        //** open CE30
        int open();
        bool isOpened();
        int release();

        //** read depthMap and greyMap to cv::Mat
        int readDepthMap(cv::Mat& src);
        int readGreyMap(cv::Mat& src);

    private:
        //** open by socket
        UDPSocket m_socket;
        Packet m_packet;
        Scan m_scan;

        //** isOpened
        bool m_isOpened;

        //cv::Mat m_depthMap;
//        cv::Mat m_greyMap;
    };
}


#endif //INC_03READPOINTCLOUDFROMCE30D_CE30DRIVER_H
