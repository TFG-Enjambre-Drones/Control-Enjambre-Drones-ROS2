from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

from enjambre_control.formations import FORMATIONS
from enjambre_control.swarm_config import SWARM_DRONES


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    formation = LaunchConfiguration('formation')
    center_x = LaunchConfiguration('center_x')
    center_y = LaunchConfiguration('center_y')
    altitude = LaunchConfiguration('altitude')
    yaw_deg = LaunchConfiguration('yaw_deg')

    xacro_file = PathJoinSubstitution([
        FindPackageShare('enjambre_drones'),
        'urdf',
        'dron_base.xacro'
    ])

    nodes = [
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('formation', default_value='flecha', choices=sorted(FORMATIONS.keys())),
        DeclareLaunchArgument('center_x', default_value='0.0'),
        DeclareLaunchArgument('center_y', default_value='0.0'),
        DeclareLaunchArgument('altitude', default_value='0.5'),
        DeclareLaunchArgument('yaw_deg', default_value='0.0'),
    ]

    for drone_name in SWARM_DRONES:
        prefix_value = f'{drone_name}_'
        robot_description = ParameterValue(
            Command(['xacro ', xacro_file, ' prefix:=', prefix_value]),
            value_type=str,
        )

        nodes.append(
            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                namespace=drone_name,
                name='robot_state_publisher',
                output='screen',
                parameters=[{
                    'use_sim_time': use_sim_time,
                    'frame_prefix': f'{drone_name}/',
                    'robot_description': robot_description,
                }],
            )
        )

    nodes.extend([
        Node(
            package='enjambre_control',
            executable='swarm_controller',
            name='swarm_controller',
            output='screen',
            parameters=[{
                'formation': formation,
                'center_x': center_x,
                'center_y': center_y,
                'altitude': altitude,
                'yaw_deg': yaw_deg,
            }],
        ),
        Node(
            package='enjambre_control',
            executable='swarm_visualizer',
            name='swarm_visualizer',
            output='screen',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', PathJoinSubstitution([FindPackageShare('enjambre_control'), 'rviz', 'swarm.rviz'])],
            output='screen',
        ),
    ])

    return LaunchDescription(nodes)
