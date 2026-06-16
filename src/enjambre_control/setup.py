from setuptools import setup
from glob import glob
import os

package_name = 'enjambre_control'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Vicente Carmona Zapata',
    maintainer_email='correo@unir.es',
    description='Control y visualización del enjambre de 6 drones en RViz',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'swarm_controller = enjambre_control.swarm_controller:main',
            'swarm_visualizer = enjambre_control.swarm_visualizer:main',
        ],
    },
)
