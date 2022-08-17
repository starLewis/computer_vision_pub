#include <ros/ros.h>
#include <rosbag/bag.h>
#include <rosbag/view.h>
#include <std_msgs/String.h>
#include <iostream>
#include <vector>

#include <boost/foreach.hpp>
int main(int argc, char **argv)
{
    ros::init(argc, argv, "readRosBag");
    ros::NodeHandle n;

    rosbag::Bag bag;
    bag.open("/home/liuxun/Clobotics/Data/CvDataOwnCloud/AutoFlight/Turbine/Ros_bag/ros_radar_15m_01.bag", rosbag::bagmode::Read);

    rosbag::View view(bag);
    std::vector<const rosbag::ConnectionInfo*> connection_infos = view.getConnections();
    std::set<std::string> topics;

    //** find the topics of bag
    BOOST_FOREACH(const rosbag::ConnectionInfo *info, connection_infos){
                    if(topics.find(info->topic)==topics.end()) {
                        topics.insert(info->topic);
//                        std::cout << info->topic << std::endl;
//                        std::cout<<"***datatype***"<<std::endl<<info->datatype<<std::endl;
//                        std::cout<<"***header***"<<std::endl<<info->header<<std::endl;
//                        std::cout<<"***id***"<<std::endl<<info->id<<std::endl;
//                        std::cout<<"***msg***"<<info->msg_def<<std::endl;

                    }
                    std::cout<<"******"<<std::endl;
                    std::cout<<info->msg_def.data()<<std::endl;
                    std::cout<<"******"<<std::endl;
                }


    //**

//    BOOST_FOREACH(const rosbag::MessageInstance m, view)
//    {
//        std_msgs::String::ConstPtr s = m.instantiate<std_msgs::String>();
//        if(s!=NULL)
//        {
//            std::cout<<s->data<<std::endl;
//        }
//    }

    return 0;
}