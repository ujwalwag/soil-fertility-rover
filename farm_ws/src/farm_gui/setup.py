from setuptools import find_packages, setup
import os
from glob import glob

package_name = "farm_gui"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="ujwalwag",
    maintainer_email="ujwalwag@todo.todo",
    description="GUI for farm rover simulation",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "farm_gui = farm_gui.main:main",
            "camera_relay = farm_gui.camera_relay:main",
        ],
    },
)
