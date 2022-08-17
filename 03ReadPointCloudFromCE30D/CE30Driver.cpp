//
// Created by liuxun on 18-1-23.
//

#include "CE30Driver.h"

//** construct
wicv::CE30Driver::CE30Driver()
{
    m_isOpened = false;
}

//** deconstruct
wicv::CE30Driver::~CE30Driver()
{
    if(m_isOpened)
    {
        this->release();
    }

}

//** singleton
static wicv::CE30Driver* instanceClass = NULL;
wicv::CE30Driver* wicv::CE30Driver::getInstance()
{
    if(instanceClass == NULL)
    {
        instanceClass = new CE30Driver();
    }
    return instanceClass;
}

//** open CE30Driver
int wicv::CE30Driver::open()
{
    m_isOpened = false;
    if (!Connect(m_socket)) {
        return -1;
    }
    VersionRequestPacket version_request;
    if (!SendPacket(version_request, m_socket)) {
        return -1;
    }
    VersionResponsePacket version_response;
    if (!GetPacket(version_response, m_socket)) {
        return -1;
    }
    std::cout << "CE30-D Version: " << version_response.GetVersionString() << std::endl;
    StartRequestPacket start_request;
    if (!SendPacket(start_request, m_socket)) {
        return -1;
    }
    m_isOpened = true;

    return m_isOpened;
}

//** isOpened
bool wicv::CE30Driver::isOpened()
{
    return m_isOpened;
}

//** close CE30
int wicv::CE30Driver::release()
{
    StopRequestPacket stop_request;
    SendPacket(stop_request, m_socket);

    return 0;
}


//** read depth mat
int wicv::CE30Driver::readDepthMap(cv::Mat& src)
{

    if(src.rows != 20 || src.cols != 320)
    {
        src.create(20,320,CV_8UC1);
    }
    //while (true) {
        if (!GetPacket(m_packet, m_socket)) {
            return -1;
        }
        std::unique_ptr<ParsedPacket> parsed = m_packet.Parse();
        if (parsed) {
            m_scan.AddColumnsFromPacket(*parsed);
            if (!m_scan.Ready()) {
                return -1;
            }
            for (int x = 0; x < m_scan.Width(); ++x) {
                for (int y = 0; y < m_scan.Height(); ++y) {
                    Channel channel = m_scan.at(x, y);

                    int temp = (int)(channel.distance)*12.75;
                    if(temp > 255) temp = 255;
                    src.at<uchar>(y,x) = (uchar)temp;

//                    std::cout <<
//                         "(" << channel.distance << ", " << channel.amplitude << ") "
//                                 "[" <<
//                         channel.point().x << ", " <<
//                         channel.point().y << ", " <<
//                         channel.point().z << "]" << std::endl;
                }
            }
            m_scan.Reset();
        }
    //}

    return -1;
}

//** read grey map
int wicv::CE30Driver::readGreyMap(cv::Mat &src)
{

    if(src.rows != 20 || src.cols != 320)
    {
        src.create(20,320,CV_8UC1);
    }
    //while (true) {
    if (!GetPacket(m_packet, m_socket)) {
        return -1;
    }
    std::unique_ptr<ParsedPacket> parsed = m_packet.Parse();
    if (parsed) {
        m_scan.AddColumnsFromPacket(*parsed);
        if (!m_scan.Ready()) {
            return -1;
        }
        for (int x = 0; x < m_scan.Width(); ++x) {
            for (int y = 0; y < m_scan.Height(); ++y) {
                Channel channel = m_scan.at(x, y);

                int temp = (int)(channel.amplitude)*12.75;
                if(temp > 255) temp = 255;
                src.at<uchar>(y,x) = (uchar)temp;

//                    std::cout <<
//                         "(" << channel.distance << ", " << channel.amplitude << ") "
//                                 "[" <<
//                         channel.point().x << ", " <<
//                         channel.point().y << ", " <<
//                         channel.point().z << "]" << std::endl;
            }
        }
        m_scan.Reset();
    }
    //}

    return -1;
}