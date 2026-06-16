SWARM_DRONES = {
    'drone1': {'id': 1, 'led_color': 'blue',  'position': (0.0, 0.5, 0.5)},
    'drone2': {'id': 2, 'led_color': 'blue',  'position': (-0.5, 0.0, 0.5)},
    'drone3': {'id': 3, 'led_color': 'blue',  'position': (0.5, 0.0, 0.5)},
    'drone4': {'id': 4, 'led_color': 'red',   'position': (-0.3, -0.5, 0.5)},
    'drone5': {'id': 5, 'led_color': 'red',   'position': (0.3, -0.5, 0.5)},
    'drone6': {'id': 6, 'led_color': 'green', 'position': (0.0, -1.0, 0.5)},
}

DEFAULT_ALTITUDE = 0.5
DEFAULT_FORMATION = 'flecha'
DEFAULT_CENTER = (0.0, 0.0)
DEFAULT_YAW_DEG = 0.0
PUBLISH_RATE_HZ = 10.0
LED_MARKER_SCALE = 0.08
TEXT_MARKER_SCALE = 0.10
DRONE_MODEL_SCALE = 1.0

COLOR_MAP = {
    'red':    (1.0, 0.0, 0.0, 1.0),
    'green':  (0.0, 1.0, 0.0, 1.0),
    'blue':   (0.0, 0.0, 1.0, 1.0),
    'yellow': (1.0, 1.0, 0.0, 1.0),
    'purple': (0.8, 0.0, 0.8, 1.0),
    'white':  (1.0, 1.0, 1.0, 1.0),
}
