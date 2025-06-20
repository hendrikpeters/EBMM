# settings.py

from os import environ

SESSION_CONFIGS = [
    dict(
        name='ebmm_experiment',
        display_name="EBMM Investment Study (Prototype)",
        num_demo_participants=1,
        app_sequence=['investment'],
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc="",
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(
        name='live_demo',
        display_name='Room for live demo (no participant labels)',
    ),
]

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here is the EBMM Investment Study prototype.
"""

SECRET_KEY = '8458257623028'

INSTALLED_APPS = ['otree']
