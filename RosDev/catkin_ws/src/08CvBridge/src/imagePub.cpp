//
// Created by liuxun on 18-2-12.
//

#include <ros/ros.h>
#include <image_transport/image_transport.h>
#include <cv_bridge/cv_bridge.h>
#include <sensor_msgs/image_encodings.h>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

image_transport::Publisher image_pub;

void pubImage(cv::Mat& src)
{
    //** publish based on cv_bridge
    sensor_msgs::ImagePtr imagePtr = cv_bridge::CvImage(std_msgs::Header(),sensor_msgs::image_encodings::BGR8,src).toImageMsg();
    image_pub.publish(imagePtr);
}

int main(int argc, char** argv)
{
    ros::init(argc,argv,"test_bridge");
    ros::NodeHandle nh;
    image_transport::ImageTransport it(nh);
    image_pub = it.advertise("output_video", 1);

    std::string videoPath = "/home/liuxun/Clobotics/Data/CvDataOwnCloud/AutoFlight/Turbine/DJI_0127.MP4";
    cv::VideoCapture vCap;
    vCap.open(videoPath);

    if(!vCap.isOpened())
    {
        std::cout<<"open video failed!"<<std::endl;
        return -1;
    }

    cv::Mat curFrame;
    while(true)
    {
        vCap.read(curFrame);
        cv::resize(curFrame,curFrame,cv::Size(curFrame.rows/4,curFrame.cols/4));
        pubImage(curFrame);

        cv::imshow("src",curFrame);
        cv::waitKey(30);
    }

    return 0;
}