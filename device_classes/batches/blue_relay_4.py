devices=[
    {
    "device_name": "Exhaust Fan",
    "type": "Exfan",
    "gpio_pin": 35,
    "run_time": 0.0,
    "color": [
    0.0,
    0.0,
    0.0,
    0.85
    ],
    "trigger": "low"
    },
    {
    "device_name": "Makeup Air Fan",
    "type": "MAU",
    "gpio_pin": 37,
    "run_time": 0,
    "color": [
    0.0,
    0.0,
    0.0,
    0.85
    ],
    "trigger": "low"
    },
    {
    "device_name": "Lights",
    "type": "Light",
    "gpio_pin": 38,
    "run_time": 0,
    "color": [
    0.0,
    0.0,
    0.0,
    0.85
    ],
    "trigger": "low"
    },
    {
    "device_name": "Dry Contact",
    "type": "Dry",
    "gpio_pin": 40,
    "run_time": 0,
    "color": [
    0.0,
    0.0,
    0.0,
    0.85
    ],
    "trigger": "low"
    }
]

info=[
'[size=18][u]Four Channel Blue Relay Board',
'''Four devices will be added, all low trigger.
The pins being used are 35,37,38 and 40.''',
'[size=18][u]'+' '*80,
'''Device: Exhaust Fan
Pin: 35
Trigger: Low
Relay Ch: 1''',
'''Device: Makeup Air Fan
Pin: 37
Trigger: Low
Relay Ch: 2''',
'''Device: Lights
Pin: 38
Trigger: Low
Relay Ch: 3''',
'''Device: Dry Contact
Pin: 40
Trigger: Low
Relay Ch: 4'''
]