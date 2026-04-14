from setuptools import find_packages, setup
import os
from glob import glob

package_name = "sfr_gui"

setup(
    name=package_name,
    version="0.1.0",
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
    description="Soil fertility rover GUI",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "sfr_gui = sfr_gui.main:main",
            "camera_relay = sfr_gui.camera_relay:main",
        ],
    },
)
