# Copyright 2024 iamliuzy

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



from pyscreeze import screenshot
from datetime import datetime
import toml
from sys import exit

import smtplib, ssl, logging
from email.message import EmailMessage
import argparse
from pathlib import Path

# Constant definitions.
VERSION = "0.0.1"
LICENSE = """
Copyright 2024 iamliuzy

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

class ConfigError():
    @staticmethod
    def not_filled_properly(info=""):
        logger.critical("config.toml not filled properly.")
        logger.critical("In the config.toml file, replace the '<>' and the content between them with the correct values.")
        if info != "":
            logger.critical(info)
        exit()
    @staticmethod
    def not_found():
        logger.critical("config.toml not found. Download from ")  # TODO: download link
        exit()

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(asctime)s](%(levelname)s) %(message)s", 
                    filename='latest.log', encoding='utf-8', level=logging.DEBUG,
                    filemode='w')

# Read config file
config: dict[str, str | int]

parser = argparse.ArgumentParser()
parser.add_argument("--config", "-C", default="config.toml", required=False)
parser.add_argument("--version", "-V", action="store_true", required=False)
parser.add_argument("--license", "-L", action="store_true", required=False)
args = vars(parser.parse_args())

# If you enter the -V, -version command line arguments, you output the version number and copyright information and exit.
# If you enter -L, -license command line parameter, then output the copyright information and exit.
if args["version"]:
    print("screenshot-and-send-email v%s." % VERSION, end="" if args["license"] else "\n")
if args["version"] or args["license"]:
    print("%s\n" % LICENSE)
    exit()

config_file = Path(args["config"])
if not config_file.exists():
    ConfigError.not_found()
try:
    config = toml.loads(config_file.read_text("utf-8"))  # Parse config
except toml.decoder.TomlDecodeError:
    ConfigError.not_filled_properly("Unexpected '<>'.")
for value in config.values():
    if not isinstance(value, int):
        if value.startswith("<") and value.endswith(">"):
            ConfigError.not_filled_properly("Unexpected '<>'.")

try:
    SERVER = config["server"]  # These two constants was defined in the code.
    PORT = config["port"]  # Now they are moved to the config.
except KeyError:
    ConfigError.not_filled_properly("Missing key: server or port.")
logger.info("SMTP SERVER:%s:%s" % (SERVER, PORT))

# Screenshot
try:
    screenshot_name = datetime.now().strftime(config["screenshot-name"])
except KeyError:
    ConfigError.not_filled_properly("Missing key: screenshot-name.")
screenshot_folder = Path(".\\screenshots\\")
screenshot_path = screenshot_folder.joinpath(screenshot_name)
if not screenshot_folder.exists():
    screenshot_folder.mkdir()
    logger.warning("Screenshot folder not found. Creating screenshot folder.")
screenshot(screenshot_path.resolve())
logger.info("Saved screenshot:%s." % screenshot_path)

# Send E-mail

# Connect to Outlook SMTP server
try:
    match config["encryption"]:
        case 0:
            connect = smtplib.SMTP(SERVER, PORT)
        case 1:
            connect = smtplib.SMTP_SSL(SERVER, PORT)
        case 2:
            connect = smtplib.SMTP(SERVER, PORT)
            connect.starttls(context=ssl.create_default_context())
        case _:
            ConfigError.not_filled_properly("Wrong encryption mode.")
    connect.login(config["from-addr"], config["passwd"])
except KeyError:
    ConfigError.not_filled_properly("Missing key: encryption.")
logger.info("Successfully connected and logged in to the server.")

# Create email
msg = EmailMessage()
msg.set_content(screenshot_name)
try:
    msg["subject"] = config["title"]
    msg['from'] = '%s <%s>' % (config["from-name"], config["from-addr"])
    msg['to'] = '%s <%s>' % (config["to-name"], config["to-addr"])
    image = screenshot_path.read_bytes()
    msg.add_attachment(image, maintype='image', subtype='png', filename=screenshot_name)  # Add screenshot as attachment
    connect.sendmail(config["from-addr"], config["to-addr"], msg.as_string())  # Send E-mail
except KeyError:
    ConfigError.not_filled_properly("Missing key: from-addr, from-name, to-addr, to-name or title.")
logger.info("Successfully send email.")
connect.quit()  # Disconnect
