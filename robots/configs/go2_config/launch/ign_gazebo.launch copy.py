import os
import launch_ros
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, SetEnvironmentVariable, 
                            IncludeLaunchDescription, SetLaunchConfiguration)
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration, TextSubstitution
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
import xacro


def generate_launch_description():
    name = 'go2'
    use_sim_time = LaunchConfiguration('use_sim_time', default=True)
    go2_description_share = launch_ros.substitutions.FindPackageShare(package="go2_description").find("go2_description")
    default_model_path = os.path.join(go2_description_share, "xacro/robot.xacro")
    # xacroをロード
    xacro_file = xacro.process_file(default_model_path, mappings={'use_sim' : 'true'})
    # xacroを展開してURDFを生成
    robot_desc = xacro.process_file(
            xacro_file,
            mappings={'robot_name': name}
        ).toxml()
    params = {'robot_description': robot_desc}
    return LaunchDescription([
        IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory('ros_gz_sim'), 'launch'), '/gz_sim.launch.py']),
                launch_arguments=[('gz_args', [' -r -v 4 empty.sdf'])]
        ),
        Node(
                package='ros_gz_sim',
                executable='create',
                output='screen',
                arguments=['-string', robot_desc,
                        '-name', 'go2',
                        '-allow_renaming', 'false'],
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(
                get_package_share_directory('go2_description'), 'launch'), '/description.launch.py']),
        )
    ])