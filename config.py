import os
# Bot information
class Config(object):
  API_ID = int(os.environ.get("API_ID", ""))
  API_HASH = os.environ.get("API_HASH", "")
  BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
  OWNER_ID = 1162032262
  PORT = int(os.environ.get("PORT", "8080"))
  AUTHJS = {str(x) for x in os.environ.get("AUTHJS", "1162032262").split()}
  HOST = os.environ.get("HOST", "0.0.0.0")
  LOGS = int(os.environ.get("LOGS", "-1002396416731"))
