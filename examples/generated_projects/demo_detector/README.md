# demo_detector

ROS-style object detection node skeleton.

## Task

Create an object detection node subscribing to camera images and publishing bounding boxes.

## Selected Template

`object_detection`

## Generated Files

- `package.xml`
- `setup.py`
- `setup.cfg`
- `robopilot.yaml`
- `launch/demo_detector.launch.py`
- `config/params.yaml`
- `demo_detector/detector_node.py`

## Notes

- Uses placeholder bounding box data for offline inspection.
- Designed for detect, object, YOLO, bbox, and bounding box tasks.

This package is intentionally offline-friendly pseudocode. It mirrors common
ROS2 Python package structure, but RoboPilot does not require a real ROS2
installation to generate or inspect these files.
