import os 
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.environ.get('API_TELEGRAM')
BOT_PASSWORD = os.environ.get('BOT_PASSWORD')
EXCEL_DIR = "excel_data"
