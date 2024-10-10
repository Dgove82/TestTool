import os.path

from src.utils.model import SQLserver
import settings

CONF = None

if os.path.exists(settings.DB_PATH):
    CONF = SQLserver.load_conf()
