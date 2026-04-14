from setuptools import find_packages, setup
import os
from glob import glob

package_name = "sfr_arm"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="ujwalwag",
    maintainer_email="ujwalwag@todo.todo",
    description="Arm control and MoveIt-related config for soil fertility rover",
    license="MIT",
    entry_points={
        "console_scripts": [
            "arm_controller = sfr_arm.arm_controller:main",
        ],
    },
)
