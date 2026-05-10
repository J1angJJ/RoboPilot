from setuptools import find_packages, setup


package_name = "demo_detector"

setup(
    name=package_name,
    version="0.11.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        (f"share/{package_name}", ["package.xml", "robopilot.yaml"]),
        (f"share/{package_name}/launch", ["launch/demo_detector.launch.py"]),
        (f"share/{package_name}/config", ["config/params.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="RoboPilot User",
    maintainer_email="developer@example.com",
    description="ROS-style object detection node skeleton.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "detector_node = demo_detector.detector_node:main",
        ],
    },
)
