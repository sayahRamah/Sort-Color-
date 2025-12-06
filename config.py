import os

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID', '5730502448')

# إعدادات اللغز
MIN_BOTTLES = 5
MAX_BOTTLES = 20
BOTTLE_CAPACITY = 4
