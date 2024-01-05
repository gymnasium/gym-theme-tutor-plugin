import pkg_resources
import requests
import os
import os.path
from glob import glob

from tutor import hooks

from .__about__ import __version__

response = requests.get('http://gym.soy/feeds/config.json')
# response = requests.get('http://local.overhang.io:4040/feeds/config.json')
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
        "CONFIG": data,
        "META": data['meta'],
        "ROOT_URL": data['urls']['root'],
        "CMS_URL": data['urls']['cms'],
        "MFE_URL": data['urls']['mfe'],
        "PRIMARY_COLOR": data['colors']['primary'],  # Aquent Gymnasium Blue
        "SECONDARY_COLOR": data['colors']['secondary'],  # Aquent Gymnasium Orange
        "MAIN_NAV": data['navigation']['main'],
        "AUTH_NAV": data['navigation']['auth'],
        "FOOTER_NAV_LINKS": data['navigation']['footer'],
        "FOOTER_LEGAL_LINKS": [],
        "LOGO_WHITE_SRC": data['logos']['main']['white']['src'],
        "LOGO_WHITE_SRCSET": data['logos']['main']['white']['srcset'],
        "LOGO_BLACK_SRC": data['logos']['main']['black']['src'],
        "LOGO_BLACK_SRCSET": data['logos']['main']['black']['srcset'],
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
    r"gym-theme/lms/static/sass/partials/lms/theme/"
)

# Load all configuration entries
hooks.Filters.CONFIG_DEFAULTS.add_items(
    [(f"GYM_{key}", value) for key, value in config["defaults"].items()]
)
hooks.Filters.CONFIG_UNIQUE.add_items(
    [(f"GYM_{key}", value) for key, value in config["unique"].items()]
)
hooks.Filters.CONFIG_OVERRIDES.add_items(list(config["overrides"].items()))

########################################
# PATCH LOADING
########################################

# For each file in gymtheme/patches,
# apply a patch based on the file's name and contents.
for path in glob(
    os.path.join(
        pkg_resources.resource_filename("gymtheme", "patches"),
        "*",
    )
):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))

