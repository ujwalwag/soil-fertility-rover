from setuptools import setup

package_name = 'farm_perception'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    package_dir={package_name: 'src'},
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', ['config/perception_params.yaml']),
        ('share/' + package_name + '/launch', ['launch/perception.launch.py']),
    ],
    install_requires=['setuptools', 'opencv-python', 'numpy'],
    zip_safe=True,
    maintainer='ujwalwag',
    maintainer_email='ujwalwag@todo.todo',
    description='Soil contact and depth perception',
    license='MIT',
    entry_points={
        'console_scripts': ['perception_node = farm_perception.perception_node:main'],
    },
)
