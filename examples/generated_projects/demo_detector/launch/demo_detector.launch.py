"""ROS2-style launch pseudocode for demo_detector."""

# This file mirrors a common ROS2 launch structure.
# It is generated for learning and planning; RoboPilot does not require
# launch_ros or a ROS2 runtime to be installed.


def generate_launch_description():
    try:
        from launch import LaunchDescription
        from launch_ros.actions import Node
    except ImportError:
        return {
            "package": "demo_detector",
            "node": "detector_node",
            "selected_template": "object_detection",
            "note": "ROS2 launch modules are not installed; this is pseudocode.",
        }

    return LaunchDescription(
        [
            Node(
                package="demo_detector",
                executable="detector_node",
                name="detector_node",
                output="screen",
                parameters=["config/params.yaml"],
            )
        ]
    )
