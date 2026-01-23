from setuptools import setup
import os

package_name = 'farm_base_station'

# Prepare data files - only include files that exist
data_files = [
    ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
]

# Only include storage/samples.db if it exists (database is typically created at runtime)
storage_db_path = 'storage/samples.db'
if os.path.exists(storage_db_path):
    data_files.append(('share/' + package_name + '/storage', [storage_db_path]))

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name, package_name + '.backend', package_name + '.frontend'],
    data_files=data_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ujwalwag',
    maintainer_email='ujwalwag@todo.todo',
    description='Base station backend, frontend, storage',
    license='MIT',
    entry_points={
        'console_scripts': [
            'server = farm_base_station.backend.server:main',
            'ros_bridge = farm_base_station.backend.ros_bridge:main',
            'data_logger = farm_base_station.backend.data_logger:main',
            'dashboard = farm_base_station.frontend.dashboard:main',
            'plots = farm_base_station.frontend.plots:main',
        ],
    },
)
