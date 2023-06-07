import pkg_resources
import requests

from tutor import hooks

from .__about__ import __version__

response = requests.get('https://data.gym.soy/feeds/complete.json')
if response.status_code == 200:
    data = response.json()
else:
    # Print an error message
    print('Error fetching data')

################# Configuration
config = {
    # Add here your new settings
    "defaults": {
        "VERSION": __version__,
        "WELCOME_MESSAGE": data['items']['config']['meta']['subtitle'],
        "PRIMARY_COLOR": "#0077c8",  # Aquent Gymnasium Blue
        "SECONDARY_COLOR": "#ff5f14",  # Aquent Gymnasium Orange
        # Footer links are dictionaries with a "title" and "url"
        # To remove all links, run:
        # tutor config save --set GYM_FOOTER_NAV_LINKS=[] --set GYM_FOOTER_LEGAL_LINKS=[]
        "FOOTER_NAV_LINKS": data['items']['config']['navigation']['footer'],
        "FOOTER_LEGAL_LINKS": [],
    },
    "unique": {},
    "overrides": {},
}

# Theme templates
hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    pkg_resources.resource_filename("gymtheme", "templates")
)
# This is where the theme is rendered in the openedx build directory
hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("gym", "build/openedx/themes"),
    ],
)

# Force the rendering of scss files, even though they are included in a "partials" directory
hooks.Filters.ENV_PATTERNS_INCLUDE.add_item(
    r"gym/lms/static/sass/partials/lms/theme/"
)

# Load all configuration entries
hooks.Filters.CONFIG_DEFAULTS.add_items(
    [(f"GYM_{key}", value) for key, value in config["defaults"].items()]
)
hooks.Filters.CONFIG_UNIQUE.add_items(
    [(f"GYM_{key}", value) for key, value in config["unique"].items()]
)
hooks.Filters.CONFIG_OVERRIDES.add_items(list(config["overrides"].items()))
