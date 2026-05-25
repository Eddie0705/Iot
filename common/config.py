# Shared configuration file for all Pi components.
# Agent Pi, Admin Pi, and Room Pi use this to connect to the Master Pi.
# This file is gitignored — do not commit credentials.

#master pi ip
#MASTER_HOST = "10.132.66.24"

#MASTER_PORT = 5050
MASTER_HOST="10.132.60.32"
MASTER_PORT= "5050"


AGENT_PORT = 5001
ROOM_PORT = 5002
ADMIN_PORT = 5003

# Email config — use a Gmail App Password (not your regular password)
EMAIL_SENDER = "e0210144@gmail.com"
EMAIL_PASSWORD = "zxmw lphr oobo qspg"