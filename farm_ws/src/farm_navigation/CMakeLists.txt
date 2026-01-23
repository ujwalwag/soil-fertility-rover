cmake_minimum_required(VERSION 3.8)
project(farm_navigation)

find_package(ament_cmake REQUIRED)

# Install resource file
install(FILES resource/${PROJECT_NAME} DESTINATION share/ament_index/resource_index/packages/)

install(DIRECTORY config maps launch DESTINATION share/${PROJECT_NAME})

ament_package()
