from launch import LaunchDescription
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch.actions import OpaqueFunction
import rclpy
from rclpy.node import Node as RclpyNode
import time
import os

def wait_for_topics(context, *args, **kwargs):
    rclpy.init()
    node = RclpyNode('wait_for_topics_node')

    required_topics = ['/odom', '/scan']

    print("Esperando lidar y odometria")

    while True:
        topics = [t[0] for t in node.get_topic_names_and_types()]

        if all(topic in topics for topic in required_topics):
            print("Topics disponibles, lanzando SLAM")
            break

        time.sleep(1)

    node.destroy_node()
    rclpy.shutdown()

    return [
        Node(
            package='slam_gmapping', 
            executable='slam_gmapping_node',
            name='slam_gmapping',
            output='screen',
            parameters=[
                {'use_sim_time': False},
                os.path.join(
                    get_package_share_directory("slam_gmapping"),
                    'config',
                    'slam_gmapping.yaml'
                )
            ]
        )
    ]


def generate_launch_description():

    # lidar 
    lidar_node = Node(
        package='oradar_lidar',
        executable='oradar_scan',
        name='MS200',
        output='screen',
        parameters=[
            {'device_model': 'MS200'},
            {'frame_id': 'lidar'},
            {'scan_topic': '/scan'},  
            {'port_name': '/dev/oradar'},
            {'baudrate': 230400},
            {'angle_min': 0.0},
            {'angle_max': 360.0},
            {'range_min': 0.05},
            {'range_max': 20.0},
            {'clockwise': False},
            {'motor_speed': 15}
        ]
    )

    #  TF base_link -> lidar
    tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_link_to_lidar',
        arguments=['0.07', '0', '0.13', '0', '0', '0', 'base_link', 'lidar'],
        output='screen'
    )

    return LaunchDescription([

        #  Lidar 
        lidar_node,
        tf_node,
        # odom to TF node 
        Node(
                package="odom_to_TF",
                executable="odomTF_node",
                name="odom_toTF",
        ),

        # Espera y luego lanza SLAM
        OpaqueFunction(function=wait_for_topics)
    ])