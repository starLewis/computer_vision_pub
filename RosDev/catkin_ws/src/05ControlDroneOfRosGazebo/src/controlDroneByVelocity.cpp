#include <ros/ros.h>
#include <std_msgs/Float64.h>
#include <geometry_msgs/TwistStamped.h>
#include <geometry_msgs/PoseStamped.h>
#include <pcl/point_cloud.h>
#include <pcl_ros/point_cloud.h>
#include <pcl_conversions/pcl_conversions.h>
#include <sensor_msgs/PointCloud2.h>
#include <mavros_msgs/CommandLong.h>
#include <wa_ros_msgs/DroneSpeedCtrl.h>
#include <wa_ros_msgs/DroneGimbalCtl.h>
#include <wa_ros_msgs/DronePosUpdate.h>
#include <cv_bridge/cv_bridge.h>
#include <image_transport/image_transport.h>
#include <opencv2/opencv.hpp>

image_transport::Publisher image_pub;
ros::Publisher speed_control_pub;
geometry_msgs::TwistStamped vel_cmd;
ros::ServiceClient command_long_client;
float target_heading = 0.0f;
//** get the info of drone

void gimbal_control(float roll, float pitch, float yaw) {
    //WARNING: Don't filter yaw control here!!!
    mavros_msgs::CommandLong srv;
    srv.request.broadcast = 0;
    srv.request.command = 205;
    srv.request.confirmation = 0;
    srv.request.param1 = pitch;//pitch
    srv.request.param2 = roll;//roll
    srv.request.param3 = yaw;//yaw
    srv.request.param4 = 0;
    srv.request.param5 = 0;
    srv.request.param6 = 0;
    srv.request.param7 = 2;

    if (command_long_client.call(srv)) {
        //ROS_INFO("gimbal control result: %d", (int) srv.response.result);
    } else {
        ROS_ERROR("gimbal control Failed");
    }
}
void gimbal_control_cb(const wa_ros_msgs::DroneGimbalCtl::ConstPtr &msg) {

    wa_ros_msgs::DroneGimbalCtl droneGimbalCtl = *msg;
    //todo modify gimbal control message
    //float heading = droneGimbalCtl.heading + drone_pos.m_heading;
    float heading = droneGimbalCtl.heading + target_heading;
//    ROS_INFO("pitch = %.2f",droneGimbalCtl.pitch);
    //ROS_INFO("gimbal yaw target = %.2f", (double)heading);
    gimbal_control(0, droneGimbalCtl.pitch, heading);

    // use PID
    //droneGimbalCtl.heading = heading;
    //gimbal_pid_ctrl_pub.publish(droneGimbalCtl);
}

void gimbal_follow_drone()
{
    float heading = target_heading;
    gimbal_control(0,0,heading);
}

void speed_control_cb(const wa_ros_msgs::DroneSpeedCtrl::ConstPtr &msg) {

    wa_ros_msgs::DroneSpeedCtrl droneSpeedCtrl;

    droneSpeedCtrl = *msg;
    vel_cmd.twist.linear.x = droneSpeedCtrl.e_speed;
    vel_cmd.twist.linear.y = droneSpeedCtrl.n_speed;
    vel_cmd.twist.linear.z = -droneSpeedCtrl.u_speed;
    vel_cmd.twist.angular.z = droneSpeedCtrl.yaw_speed * 3.14 / 180;//rad/s

    speed_control_pub.publish(vel_cmd);

    ROS_INFO("xxx");

    //gimbal yaw follow body
//    target_heading = droneSpeedCtrl.target_heading;
//    gimbal_follow_drone();
}

void local_pos_cb(const geometry_msgs::PoseStamped::ConstPtr &msg) {
    geometry_msgs::PoseStamped local_pos = *msg;
//    relative_alt = local_pos.pose.position.z;
//    ROS_INFO("localX,Y,Z: %.2f %.2f %.2f",local_pos.pose.position.x,
//        local_pos.pose.position.y, local_pos.pose.position.z);
    //ROS_INFO("get pos = %.2f", global_pos.altitude);
}
void yaw_cb(const std_msgs::Float64::ConstPtr &msg) {
    std_msgs::Float64 yaw = *msg;

    target_heading = yaw.data;

    //drone_pos.m_heading = (float) -yaw.data;// todo this adds negative
}

void point_cloud_cb(const sensor_msgs::PointCloud2::ConstPtr &msg)
{
    sensor_msgs::PointCloud2 input;
    input = *msg;

    pcl::PointCloud<pcl::PointXYZ> cloud;
    cv::Mat xyzMat(20,320,CV_32FC4);

    pcl::fromROSMsg(input,cloud);
    for(int i = 0; i < 20; i++)
    {
        for(int j = 0; j < 320; j++)
        {
            xyzMat.at<cv::Vec4f>(i,j)[0] = cloud[i*320+j].x;
            xyzMat.at<cv::Vec4f>(i,j)[1] = cloud[i*320+j].y;
            xyzMat.at<cv::Vec4f>(i,j)[2] = cloud[i*320+j].z;
            xyzMat.at<cv::Vec4f>(i,j)[3] =sqrt(cloud[i*320+j].x*cloud[i*320+j].x + cloud[i*320+j].y*cloud[i*320+j].y + cloud[i*320+j].z*cloud[i*320+j].z);
        }
    }

    //** publish based on cv_bridge
    sensor_msgs::ImagePtr imagePtr = cv_bridge::CvImage(std_msgs::Header(),sensor_msgs::image_encodings::TYPE_32FC4,xyzMat).toImageMsg();
    image_pub.publish(imagePtr);

//    cv::imshow("xyzd",xyzMat);
//    cv::waitKey(20);

}

int main(int argc, char **argv)
{
    ros::init(argc, argv, "drone_speed_contrl");
    ros::NodeHandle nh;

    speed_control_pub = nh.advertise<geometry_msgs::TwistStamped>("/mavros/setpoint_velocity/cmd_vel",100);

    ros::Subscriber local_pos_sub = nh.subscribe<geometry_msgs::PoseStamped>
            ("/mavros/local_position/pose", 10, local_pos_cb);
    ros::Subscriber speed_control_sub = nh.subscribe<wa_ros_msgs::DroneSpeedCtrl>
            ("/drone/speed_control", 10, speed_control_cb);
    ros::Subscriber yaw_sub = nh.subscribe<std_msgs::Float64>
            ("/mavros/global_position/compass_hdg", 10, yaw_cb);

    command_long_client = nh.serviceClient<mavros_msgs::CommandLong>
            ("/mavros/cmd/command");// /camera/take_photo

    image_transport::ImageTransport it(nh);
    image_pub = it.advertise("/depth_cam/xyzMat",1);

    ros::Subscriber solid_radar_sub = nh.subscribe("/depth_cam/points",10,point_cloud_cb);

//
    geometry_msgs::TwistStamped vel_cmd;

    double e_speed = 0;
    double n_speed = 0;
    double u_speed = 1;
    double yaw_speed = 0;
    ros::Rate loop_rate(10);
    while(ros::ok())

    {
        vel_cmd.twist.linear.x = e_speed;
        vel_cmd.twist.linear.y = n_speed;
        vel_cmd.twist.linear.z = u_speed;
        vel_cmd.twist.angular.z = yaw_speed*3.14/180;

        //gimbal yaw follow body
//        gimbal_follow_drone();

        speed_control_pub.publish(vel_cmd);

        ros::spinOnce();
        loop_rate.sleep();
    }

    return 0;
}