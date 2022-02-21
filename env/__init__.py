from decouple import config as env

TOKEN = env('TOKEN')

CONFIG_ADMIN = env('CONFIG_ADMIN', cast=int)

STAR_GROUP_CHAT_ID = env('STAR_GROUP_CHAT_ID', cast=int)
ZNXY_GROUP_CHAT_ID = env('ZNXY_GROUP_CHAT_ID', cast=int)

DEBUG = env('DEBUG', cast=bool)