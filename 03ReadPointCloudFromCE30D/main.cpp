#include <iostream>
#include <opencv2/opencv.hpp>
#include "CE30Driver.h"
using namespace std;


void changeColor(cv::Mat& src, cv::Mat& dst)
{
    if(dst.rows != src.rows || dst.cols != src.cols)
    {
        dst.create(src.rows,src.cols,CV_8UC3);
    }
    for(int i=0;i<src.rows;i++)
    {
        for(int j=0;j<src.cols;j++)
        {
            uchar temp = src.at<uchar>(i,j);
            if(temp>160)
            {
                dst.at<cv::Vec3b>(i,j)[0] = temp;
                dst.at<cv::Vec3b>(i,j)[1] = 0;
                dst.at<cv::Vec3b>(i,j)[2] = 0;
            }else if(temp< 98)
            {
                dst.at<cv::Vec3b>(i,j)[0] = 0;
                dst.at<cv::Vec3b>(i,j)[1] = 0;
                dst.at<cv::Vec3b>(i,j)[2] = 255 - temp;
            }else
            {
                dst.at<cv::Vec3b>(i,j)[0] = 255;
                dst.at<cv::Vec3b>(i,j)[1] = 255;
                dst.at<cv::Vec3b>(i,j)[2] = 255;
            }

        }
    }
}

int main()
{
    wicv::CE30Driver* ce30Driver = wicv::CE30Driver::getInstance();

    cv::Mat curDepthMat;
    cv::Mat resizeDepthMat;
    cv::Mat curGreyMat;
    cv::Mat resizeGreyMat;

    cv::Mat depthMat(20,320,CV_32FC4);

    ce30Driver->open();
    if(!ce30Driver->isOpened())
    {
        std::cout<<"CE30D open failed!"<<std::endl;
        return -1;
    }

    int curIndex = 0;
//    while(true)
//    {
//        curIndex++;
//        ce30Driver->readDepthMap(curDepthMat);
////        curDepthMat.copyTo(resizeDepthMat);
////        cv::cvtColor(resizeDepthMat,resizeDepthMat,CV_GRAY2BGR);
//        changeColor(curDepthMat,resizeDepthMat);
//        cv::resize(resizeDepthMat,resizeDepthMat,cv::Size(curDepthMat.cols*4,curDepthMat.rows*4));
//
//        ce30Driver->readGreyMap(curGreyMat);
//        curGreyMat.copyTo(resizeGreyMat);
//        cv::resize(resizeGreyMat,resizeGreyMat,cv::Size(curGreyMat.cols*4, curGreyMat.rows*4));
//
//        cv::imshow("greyMat", resizeGreyMat);
//        cv::imshow("depthMat",resizeDepthMat);
//        cv::waitKey(2);
//    }

    ce30Driver->release();

}

//
//int main() {
//
//    UDPSocket socket;
//    if (!Connect(socket)) {
//        return -1;
//    }
//    VersionRequestPacket version_request;
//    if (!SendPacket(version_request, socket)) {
//        return -1;
//    }
//    VersionResponsePacket version_response;
//    if (!GetPacket(version_response, socket)) {
//        return -1;
//    }
//    cout << "CE30-D Version: " << version_response.GetVersionString() << endl;
//    StartRequestPacket start_request;
//    if (!SendPacket(start_request, socket)) {
//        return -1;
//    }
//
//    // Now it's ready to receive measurement data
//    Packet packet;
//    Scan scan;
//    while (true) {
//        if (!GetPacket(packet, socket)) {
//            continue;
//        }
//        unique_ptr<ParsedPacket> parsed = packet.Parse();
//        if (parsed) {
//            scan.AddColumnsFromPacket(*parsed);
//            if (!scan.Ready()) {
//                continue;
//            }
//            std::cout<<"scan:"<<scan.Width()<<" "<<scan.Height()<<std::endl;
//            for (int x = 0; x < scan.Width(); ++x) {
//                for (int y = 0; y < scan.Height(); ++y) {
//                    Channel channel = scan.at(x, y);
//                    cout <<
//                         "(" << channel.distance << ", " << channel.amplitude << ") "
//                                 "[" <<endl;
////                         channel.point().x << ", " <<
////                         channel.point().y << ", " <<
////                         channel.point().z << "]" << endl;
//                }
//            }
//            scan.Reset();
//        }
//    }
//}


//
//int main() {
//    UDPSocket socket;
//    if (!Connect(socket)) {
//        return -1;
//    }
//    VersionRequestPacket version_request;
//    if (!SendPacket(version_request, socket)) {
//        return -1;
//    }
//    VersionResponsePacket version_response;
//    if (!GetPacket(version_response, socket)) {
//        return -1;
//    }
//    cout << "CE30-D Version: " << version_response.GetVersionString() << endl;
//    StartRequestPacket start_request;
//    if (!SendPacket(start_request, socket)) {
//        return -1;
//    }
//    // Now it's ready to receive measurement data
//    Packet packet;
//    while (true) {
//        if (!GetPacket(packet, socket)) {
//            continue;
//        }
//        unique_ptr<ParsedPacket> parsed = packet.Parse();
//        std::cout<<"column: "<<parsed->columns.size()<<std::endl;
//        if (parsed) {
//            for (Column& column : parsed->columns) {
//                std::cout<<"channles: "<<column.channels.size()<<std::endl;
//                for (Channel& channel : column.channels) {
//                    // Print "[distance, amplitude] (x, y, z)"
////                    cout <<
////                         "(" << channel.distance << ", " << channel.amplitude << ") "
////                                 "[" <<
////                         channel.point().x << ", " <<
////                         channel.point().y << ", " <<
////                         channel.point().z << "]" << endl;
//                }
//            }
//        }
//    }
//    StopRequestPacket stop_request;
//    SendPacket(stop_request, socket);
//}
//



//
//void DataReceiveCB(std::shared_ptr<ce30_driver::PointCloud> cloud)
//{
//    for(ce30_driver::Point& point: cloud->points)
//    {
//        index++;
//        maxIndex = MAX(maxIndex,index);
//        //std::cout<<"index: "<<index<<" "<<point.x<<" "<<point.y<<" "<<point.z<<std::endl;
//    }
//}
//
//int main()
//{
//    ce30_driver::UDPServer server;
//    server.RegisterCallback(DataReceiveCB);
//    if(!server.Start())
//    {
//        return -1;
//    }
//    while(true) {
//        index = 0;
//        maxIndex = 0;
//        server.SpinOnce();
//        std::cout<<"maxIndex: "<<maxIndex<<std::endl;
//    }
//
//
//    std::cout<<"Hello world!"<<std::endl;
//
//    return 0;
//}