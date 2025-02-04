from __future__ import annotations

import os
import typing as t
import html

import importlib_resources
import requests
from tutor import hooks
from tutor.__about__ import __version_suffix__, __package_version__
from tutor.types import Config, get_typed

from .__about__ import __version__

# Handle version suffix in nightly mode, just like tutor core
if __version_suffix__:
    __version__ += "-" + __version_suffix__
from glob import glob

# dotenv
from dotenv import load_dotenv

load_dotenv(".env", override=True)

endpoint = os.getenv("API_URL") + "/api/config.json"

response = requests.get(endpoint)
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
        "API_URL": os.getenv("API_URL"),
        "STATIC_ASSETS_URL": os.getenv("STATIC_ASSETS_URL"),
        "ROOT_BASE": os.getenv("ROOT_BASE"),
        "ROOT_DOMAIN": os.getenv("ROOT_DOMAIN"),
        "ROOT_URL": os.getenv("ROOT_URL"),
        "MFE_URL": data['urls']['mfe'],
        "LMS_URL": data['urls']['lms'],
        "CMS_URL": data['urls']['cms'],
        "MAIN_NAV": data['header']['nav']['main'],
        "AUTH_NAV": data['header']['nav']['auth'],
        "COURSE_NAV": data['header']['nav']['courses'],
        "MSG": data['msg'],
        "LOGIN_LABEL": data['header']['nav']['auth']['public'][0]['label'],
        "REGISTER_LABEL": data['header']['nav']['auth']['public'][1]['label'],
        "DASHBOARD_LABEL": data['header']['nav']['auth']['private'][0]['label'],
        "LOGOUT_LABEL": data['header']['nav']['auth']['private'][1]['label'],
        "AUTHN_WELCOME_MSG": html.escape(data['msg']['mfe']['authn']['welcome']),
        "FOOTER_HTML": html.escape(data['html']['footer']),
        "FOOTER_LEGAL_LINKS": [],
        "LOGO_WHITE_SRC": data['logos']['main']['white']['src'],
        "LOGO_WHITE_SRCSET": data['logos']['main']['white']['srcset'],
        "HOMEPAGE_BG_IMAGE": "",
        # EXTRAS: additional CSS for html theme
        "EXTRAS": "",
        # OVERRIDES: additional CSS for mfe branding
        "OVERRIDES": "",
        "FONTS": "",
    },
    "unique": {},
    "overrides": {
        "API_URL": os.getenv("API_URL"),
        "STATIC_ASSETS_URL": os.getenv("STATIC_ASSETS_URL"),
        "CONTACT_EMAIL": "help@thegymnasium.com",
        "DOCKER_IMAGE_OPENEDX": "gymnasium/gym-theme-openedx:{{ TUTOR_VERSION }}",
        "DOCKER_IMAGE_OPENEDX_DEV": "gymnasium/gym-theme-openedx-dev:{{ TUTOR_VERSION }}",
        "INFO_EMAIL": "help@thegymnasium.com",
        "INTERCOM_APP_ID": os.getenv("INTERCOM_APP_ID"),
        "MARKETING_SITE_BASE_URL": os.getenv("ROOT_URL"),
        "MFE_DOCKER_IMAGE": "gymnasium/gym-theme-mfe:" + __version__,
        "MFE_DOCKER_IMAGE_DEV_PREFIX": "gymnasium/gym-theme",
        "ONETRUST_COOKIE_SCRIPT_ID": os.getenv("ONETRUST_COOKIE_SCRIPT_ID"),
        "PLATFORM_DESCRIPTION": data['meta']['description'],
        "PLATFORM_NAME": data['meta']['title'],
        "ROOT_BASE": os.getenv("ROOT_BASE"),
        "ROOT_DOMAIN": os.getenv("ROOT_DOMAIN"),
        "ROOT_URL": os.getenv("ROOT_URL"),
        "SITE_NAME": data['meta']['title'],
    },
}

# Theme templates
hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    str(importlib_resources.files("gymtheme") / "templates")
)
# This is where the theme is rendered in the openedx build directory
hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("gym-theme", "build/openedx/themes"),
    ],
)

# Force the rendering of scss files, even though they are included in a "partials" directory
hooks.Filters.ENV_PATTERNS_INCLUDE.add_items(
    [
        r"gym-theme/lms/static/sass/partials/lms/theme/",
        r"gym-theme/cms/static/sass/partials/cms/theme/",
    ]
)

# init script: set theme automatically
with open(
    os.path.join(
        str(importlib_resources.files("gymtheme") / "templates"),
        "gym-theme",
        "tasks",
        "init.sh",
    ),
    encoding="utf-8",
) as task_file:
    hooks.Filters.CLI_DO_INIT_TASKS.add_item(("lms", task_file.read()))

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
        str(importlib_resources.files("gymtheme") / "patches"),
        "*",
    )
):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))

