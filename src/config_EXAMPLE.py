from datetime import datetime, timezone

LOGS_PATH = 'logs'
LOG_FILENAME = 'weather_log.csv'
FIELDNAMES = ['validdate', 't_2m:C', 'uv:idx']
STARTTIME = '00:02:50'
GOOGLE_DRIVE_FOLDER_ID = ''
INTERVAL_MEASUREMENTS = 20
INTERVAL_BACKUP = 25
# Parameters for API call
VALIDDATE = f'{datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}'
PARAMETERS = 't_2m:C,uv:idx'
LOCATION = ''
FORMAT = 'json'
TOKEN_URL = 'https://login.meteomatics.com/api/v1/token'
API_URL = 'https://api.meteomatics.com'
USER = ''
PASS = ''
