//
// Created by liuxun on 18-2-12.
//

#include <ros/ros.h>
#include <image_transport/image_transport.h>
#include <cv_bridge/cv_bridge.h>
#include <sensor_msgs/image_encodings.h>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

cv::Mat desMat;
image_transport::Subscriber image_sub;

void cvBridgeCB(const sensor_msgs::ImageConstPtr &msg)
{
    cv_bridge::CvImagePtr cv_ptr;
    try {
        cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
    }
    catch (cv_bridge::Exception &e) {
        ROS_ERROR("cv_bridge exception: %s", e.what());
        return;
    }

    cv_ptr->image.copyTo(desMat);

    cv::imshow("des",desMat);
    cv::waitKey(20);

}

int main(int argc, char** argv)
{
    ros::init(argc, argv, "cv_sub");
    ros::NodeHandle nh;
    image_transport::ImageTransport it(nh);

    image_sub = it.subscribe("output_video", 1,&cvBridgeCB);
    ros::spin();


    return 0;
}