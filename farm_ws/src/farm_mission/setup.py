from setuptools import setup

package_name = 'farm_mission'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    package_dir={package_name: 'src'},
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/mission.launch.py']),
        ('share/' + package_name + '/srv', ['srv/SetGeofence.srv']),
        ('share/' + package_name + '/action', ['action/DoSample.action']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ujwalwag',
    maintainer_email='ujwalwag@todo.todo',
    description='Mission state machine, geofence, waypoints',
    license='MIT',
    entry_points={
        'console_scripts': [
            'mission_state_machine = farm_mission.mission_state_machine:main',
            'waypoint_sampler = farm_mission.waypoint_sampler:main',
            'soil_sampling_mission = farm_mission.soil_sampling_mission:main',
        ],
    },
)
