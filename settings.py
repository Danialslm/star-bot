import logging

from decouple import config, Csv

TOKEN = config('TOKEN')
DEBUG = config('DEBUG', cast=bool)

CONFIG_ADMIN = config('CONFIG_ADMIN', cast=int)

ORDER_ADMINS_GAP_1 = config('ORDER_ADMINS_GAP_1', cast=Csv(int))
ORDER_GROUP_CHAT_ID_1 = config('ORDER_GROUP_CHAT_ID_1', cast=int)
ORDER_PAYER_CHAT_ID_1 = config('ORDER_PAYER_CHAT_ID_1', cast=int)

ORDER_ADMINS_GAP_2 = config('ORDER_ADMINS_GAP_2', cast=Csv(int))
ORDER_GROUP_CHAT_ID_2 = config('ORDER_GROUP_CHAT_ID_2', cast=int)
ORDER_PAYER_CHAT_ID_2 = config('ORDER_PAYER_CHAT_ID_2', cast=int)
