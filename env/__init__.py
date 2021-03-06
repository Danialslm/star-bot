from decouple import config as env

TOKEN = env('TOKEN')

CONFIG_ADMIN = env('CONFIG_ADMIN', cast=int)

STAR_GROUP_CHAT_ID = env('STAR_GROUP_CHAT_ID', cast=int)
STAR_GROUP_PAYER_CHAT_ID = env('STAR_GROUP_PAYER_CHAT_ID', cast=int)

ZNXY_GROUP_CHAT_ID = env('ZNXY_GROUP_CHAT_ID', cast=int)
ZNXY_GROUP_PAYER_CHAT_ID = env('ZNXY_GROUP_PAYER_CHAT_ID', cast=int)

PAYERS_CHAT_ID = [STAR_GROUP_PAYER_CHAT_ID, ZNXY_GROUP_PAYER_CHAT_ID]

NOTIFY_SENDER_CHAT_ID = env('NOTIFY_SENDER_CHAT_ID', cast=int)

DEBUG = env('DEBUG', cast=bool)