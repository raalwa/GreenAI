LOGS_PATH = 'logs'
LOG_FILENAME = 'weather_log.csv'
FIELDNAMES = ['validdate', 'direct_rad:W', 'diffuse_rad:W', 'clear_sky_rad:W',
              'global_rad:W', 'uv:idx', 'is_day:idx', 'sun_azimuth:d', 'sun_elevation:d', 'current', 'voltage', 'power']
STARTTIME = '00:02:50'
GOOGLE_DRIVE_FOLDER_ID = ''
INTERVAL_MEASUREMENTS = 2
INTERVAL_BACKUP = 2
# Parameters for API call
PARAMETERS = 'direct_rad:W,diffuse_rad:W,clear_sky_rad:W,global_rad:W,uv:idx,is_day:idx,sun_azimuth:d,sun_elevation:d'
LOCATION = ''
FORMAT = 'json'
TOKEN_URL = 'https://login.meteomatics.com/api/v1/token'
API_URL = 'https://api.meteomatics.com'
USER = ''
PASS = ''
