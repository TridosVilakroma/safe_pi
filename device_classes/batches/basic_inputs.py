devices=[
    {
    "device_name": "Heat Sensor",
    "type": "Heat",
    "gpio_pin": 35,
    "run_time": 0.0,
    "color": [
    0.0,
    0.0,
    0.0,
    0.85
    ],
    "trigger": "high"
    },
    {
    "device_name": "Fire System Micro Switch",
    "type": "Micro",
    "gpio_pin": 37,
    "run_time": 0,
    "color": [
    0.6666666666666666,
    0.0,
    0.0,
    0.85
    ],
    "trigger": "high"
    }
]

info=[
'[size=18][u]Basic Input Devices',
'''Two devices will be added, both high trigger inputs.
The pins being used are 35 and 40.''',
'[size=18][u]'+' '*80,
'''Device: Heat Sensor
Pin: 35
Trigger: high''',
'''Device: Fire System Micro Switch
Pin: 37
Trigger: high
(Adding this device without being tied into
a set micro switch will cause the
system to go into fired mode.)'''
]