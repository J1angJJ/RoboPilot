#!/usr/bin/env python3
"""Tiny ROS1-style talker for RoboPilot static analysis demos.

This file is intentionally illustrative. The tutorial does not run it.
"""

import rospy
from std_msgs.msg import String


def main():
    rospy.init_node("demo_talker")
    rate_hz = rospy.get_param("~rate_hz", 1.0)
    publisher = rospy.Publisher("demo_chatter", String, queue_size=10)
    rate = rospy.Rate(rate_hz)
    count = 0
    while not rospy.is_shutdown():
        publisher.publish(String(data=f"hello from ROS1 demo {count}"))
        count += 1
        rate.sleep()


if __name__ == "__main__":
    main()
