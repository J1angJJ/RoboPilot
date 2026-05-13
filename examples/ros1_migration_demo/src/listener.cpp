#include <ros/ros.h>
#include <std_msgs/String.h>

void chatterCallback(const std_msgs::String::ConstPtr& msg)
{
  ROS_INFO("RoboPilot demo heard: %s", msg->data.c_str());
}

int main(int argc, char** argv)
{
  ros::init(argc, argv, "demo_listener");
  ros::NodeHandle node;
  ros::Subscriber subscriber = node.subscribe("demo_chatter", 10, chatterCallback);
  ros::spin();
  return 0;
}
