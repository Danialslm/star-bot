import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import Filters, MessageHandler, ConversationHandler, CallbackQueryHandler

import settings
from db import db

GET_UC_LIST, DECISION = range(2)

CONFIG_UC_TEXT = (
    'لطفا لیست جدید یوسی ها را با فرمت زیر ارسال کنید.\n\n'
    '60 - 60000\n'
    '120 - 120000\n\n'
    'نکته : تعداد یوسی سمت چپ و قیمت به تومان سمت راست است.'
)


def config_uc_list(update, context):
    context.user_data['new_uc_list'] = []

    update.message.reply_text(CONFIG_UC_TEXT)
    return GET_UC_LIST


def get_new_uc_list(update, context):
    new_uc_list = context.user_data['new_uc_list']
    text = update.message.text

    # remove additional new line
    text = re.sub(r'\n+', '\n', text)

    # validate given data
    try:
        validate = lambda x: bool(re.match(r'^\d+$', x))

        text = text.split('\n')

        for i in text:
            i = i.split('-')
            uc = i[0].strip()
            price = i[1].strip()

            if not (validate(uc) and validate(price)):
                raise ValueError
            else:
                new_uc_list.append({'uc': int(uc), 'price': int(price)})
    except (IndexError, ValueError):
        update.message.reply_text(CONFIG_UC_TEXT)
        return GET_UC_LIST
    else:
        text = 'لیست یوسی ها به شکل زیر خواهد شد.\n\n'
        for i in context.user_data['new_uc_list']:
            text += f'یوسی : {i["uc"]}\n'
            text += f'قیمت : {i["price"]} تومان\n\n'

        keyboard = [
            [InlineKeyboardButton('ارسال دوباره', callback_data='send_again')],
            [InlineKeyboardButton('ذخیره', callback_data='save')],
            [InlineKeyboardButton('لغو بروزرسانی', callback_data='cancel_updating')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text, reply_markup=reply_markup)
        return DECISION


def decision(update, context):
    query = update.callback_query
    if query.data == 'send_again':
        query.edit_message_text(CONFIG_UC_TEXT)
        return GET_UC_LIST
    elif query.data == 'save':
        # update uc list
        new_uc_list = db.set_uc_list(context.user_data['new_uc_list'])

        # send update notification for all users
        ORDER_ADMINS = settings.ORDER_ADMINS_GAP_1 + settings.ORDER_ADMINS_GAP_2

        notify_text = 'اعلانیه\n لیست جدید یوسی ها:\n\n'
        for uc in new_uc_list:
            notify_text += f'یوسی {uc["uc"]} قیمت {uc["price"]} تومان\n\n'

        for user in ORDER_ADMINS:
            try:
                context.bot.send_message(user, notify_text)
            except BadRequest:
                continue

        query.edit_message_text('لیست یوسی ها بروز و به کاربران اطلاع داده شد.')
        return ConversationHandler.END
    elif query.data == 'cancel_updating':
        query.edit_message_text('بروزرسانی لیست یوسی ها لغو شد.')
        return ConversationHandler.END


def reset_checkout_list(update, context):
    uc_list = db.get_uc_list()
    users = db.get_users()

    text = 'لیست تسویه حساب همه کاربران:\n\n'
    for user, values in users.items():
        user_total_debt = 0
        user_first_name = values['first_name']

        for uc in uc_list:
            for item in values['checkout_list']:
                if uc['uc'] == item['uc']:
                    user_total_debt += uc['price'] * item['quantity']
                    break

        text += f'ادمین : {user_first_name}\n'
        text += f'بدهی : {user_total_debt}\n\n'

    keyboard = [
        [InlineKeyboardButton('ریست', callback_data='reset')],
        [InlineKeyboardButton('لغو', callback_data='cancel')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')


def handle_reset_checkout_list(update, context):
    query = update.callback_query
    if query.data == 'cancel':
        query.edit_message_text('عملیات ریست کردن لیست تسویه حساب لغو شد.')
    elif query.data == 'reset':
        db.clean_users()
        query.edit_message_text('لیست تسویه حساب کاربران ریست شد.')


def stop_ordering(update, context):
    db.set_ordering_state(False)

    update.message.reply_text('فرایند سفارش یوسی متوقف شد.')


def start_ordering(update, context):
    db.set_ordering_state(True)

    update.message.reply_text('فرایند سفارش یوسی شروع شد.')


# handlers
config_uc_handler = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.regex('^بروزرسانی لیست یوسی ها$') & Filters.chat([settings.CONFIG_ADMIN]),
                       config_uc_list)
    ],
    states={
        GET_UC_LIST: [MessageHandler(Filters.text & Filters.chat([settings.CONFIG_ADMIN]), get_new_uc_list)],
        DECISION: [CallbackQueryHandler(decision)],
    },
    fallbacks=[],
)

reset_checkout_list_handler = MessageHandler(
    Filters.regex('^ریست لیست تسویه حساب$') & Filters.chat([settings.CONFIG_ADMIN]),
    reset_checkout_list,
)

reset_checkout_list_query_handler = CallbackQueryHandler(handle_reset_checkout_list)

stop_ordering_handler = MessageHandler(
    Filters.regex('^قفل سفارش$') & Filters.chat([settings.CONFIG_ADMIN]),
    stop_ordering,
)

start_ordering_handler = MessageHandler(
    Filters.regex('^بازکردن سفارش$') & Filters.chat([settings.CONFIG_ADMIN]),
    start_ordering,
)
