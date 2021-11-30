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

ADMINS_NAME = {
    '110630213': 'Colleague 13H',
    '112028196': 'Colleague 12H',
    '1861705792': 'Colleague 8P',
    '866956859': 'Colleague 22Z',
    '1081836188': 'Colleague 16V',
    '2034678025': 'Colleague 18P',
    '1024426677': 'Colleague 5E',
    '574966516': 'Colleague 14Q',
    '1366972758': 'Colleague 9T',
    '289776530': 'Colleague 1Pz',
    '148617896': 'Colleague 6F',
    '1535310564': 'Colleague 3D',
    '1228391795': 'Colleague 17Dy',
    '260700445': 'Colleague 7G',
    '1061545843': 'Colleague 21V',
    '109255563': 'Colleague 4C',
    '2076327799': 'Colleague 15G',
    '99144121': 'Colleague 11A',
    '446722152': 'Colleague 24N',
    '131444268': 'Colleague 2B',
    '313806611': 'Colleague S8',


    '980450342': 'Zenxy 1',
    '1645166237': 'Zenxy 2',
    '985440407': 'Zenxy 3',
    '1141960568': 'Zenxy 4',
}
