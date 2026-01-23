from setuptools import setup

package_name = 'farm_bringup'

setup(
    name=package_name,
    version='0.0.0',
    packages=[],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', [
            'launch/sim_bringup.launch.py',
            'launch/sim.launch.py',
            'launch/complete_mission.launch.py'
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ujwalwag',
    maintainer_email='ujwalwag@todo.todo',
    description='Sim bringup launch for soil fertility rover',
    license='MIT',
)
