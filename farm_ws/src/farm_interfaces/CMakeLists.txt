cmake_minimum_required(VERSION 3.8)
project(farm_interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)

# Generate messages
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/SoilSample.msg"
  "msg/MissionStatus.msg"
  "msg/RobotHealth.msg"
  "msg/Telemetry.msg"
  "srv/SampleRequest.srv"
  "srv/SetGeofence.srv"
  "action/Sample.action"
  "action/DoSample.action"
  DEPENDENCIES geometry_msgs sensor_msgs std_msgs nav_msgs builtin_interfaces
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
