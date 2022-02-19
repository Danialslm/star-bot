from decouple import config as env

TOKEN = env('TOKEN')
CONFIG_ADMIN = env('CONFIG_ADMIN', cast=int)
DEBUG = env('DEBUG', cast=bool)