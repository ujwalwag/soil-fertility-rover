from setuptools import setup

package_name = 'farm_sensors'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    package_dir={package_name: 'src'},
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/sensors.launch.py']),
        ('share/' + package_name + '/msg', ['msg/SoilSample.msg']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ujwalwag',
    maintainer_email='ujwalwag@todo.todo',
    description='NPK, moisture drivers and soil data publisher',
    license='MIT',
    entry_points={
        'console_scripts': ['soil_data_publisher = farm_sensors.soil_data_publisher:main'],
    },
)
