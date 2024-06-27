from pyscreeze import screenshot
from datetime import date
import toml

import smtplib, ssl, logging
from email.message import EmailMessage

from os.path import abspath, exists
from os import mkdir

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(asctime)s](%(levelname)s) %(message)s", 
                    filename='latest.log', encoding='utf-8', level=logging.DEBUG)

# Read config file
try:
    f = open(abspath("config.toml"), "a+", encoding="utf-8")
    f.seek(0)  # Move index to the beginning of the config
    config = toml.loads(f.read())  # Parse config
finally:
    f.close()
SERVER = config["server"]  # These two constants was defined in the code.
PORT = config["port"]  # Now they are moved to the config.
logger.info("SMTP SERVER:%s:%s" % (SERVER, PORT))

# Screenshot
screenshot_name = date.today().strftime("%Y年%m月%d日备忘录.png")
screenshot_path = ".\\screenshots\\" + screenshot_name
if not exists(abspath(".\\screenshots\\")):
    mkdir(abspath(".\\screenshots\\"))
    logger.warning("Screenshot folder not found. Creating screenshot folder.")
screenshot(abspath(screenshot_path))
logger.info("Saved screenshot:%s." % screenshot_path)

# Send E-mail

# Connect to Outlook SMTP server
connect = smtplib.SMTP(SERVER, PORT)
connect.starttls(context=ssl.create_default_context())
connect.login(config["from-addr"], config["passwd"])
logger.info("Successfully connected and logged in to the server.")

# Create email
msg = EmailMessage()
msg.set_content(screenshot_name)
msg["subject"] = config["title"]
msg['from'] = '%s <%s>' % (config["from-name"], config["from-addr"])
msg['to'] = '%s <%s>' % (config["to-name"], config["to-addr"])
with open(abspath(screenshot_path), "rb") as i:  # Add screenshot as attachment
    msg.add_attachment(i.read(), maintype='image', subtype='png', filename=screenshot_name)
connect.sendmail(config["from-addr"], config["to-addr"], msg.as_string())  # Send E-mail
logger.info("Successfully send email.")
connect.quit()  # Disconnect
