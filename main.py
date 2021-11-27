#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, Filters

import settings
from config import config_uc_handler, reset_checkout_list_handler, stop_ordering_handler, start_ordering_handler, \
    reset_checkout_list_query_handler
from ordering import ordering_handler, show_checkout_list_handler, paid_handler

# logging
if settings.DEBUG:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
else:
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='error.log'
    )
logger = logging.getLogger(__name__)

ORDER_ADMINS = [
    *settings.ORDER_ADMINS_GAP_1,
    *settings.ORDER_ADMINS_GAP_2,
]


def start(update, context):
    if not settings.DEBUG:
        keyboard = []
        if update.message.chat_id in ORDER_ADMINS:
            keyboard = [
                ['ثبت سفارش جدید'],
                ['نمایش لیست تسویه حساب'],
            ]
        elif update.message.chat_id == settings.CONFIG_ADMIN:
            keyboard = [
                ['بروزرسانی لیست یوسی ها'],
                ['ریست لیست تسویه حساب'],
                ['قفل سفارش'],
                ['بازکردن سفارش'],
            ]
    else:
        keyboard = [
            ['ثبت سفارش جدید'],
            ['نمایش لیست تسویه حساب'],
            ['بروزرسانی لیست یوسی ها'],
            ['ریست لیست تسویه حساب'],
            ['قفل سفارش'],
            ['بازکردن سفارش'],
        ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(
        'لطفا یکی از گزینه های زیر را انتخاب کنید.',
        reply_markup=reply_markup,
    )


def error_handler(update, context):
    logger.error('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(settings.TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler(
        'start',
        start,
        filters=Filters.chat([
            *ORDER_ADMINS,
            settings.CONFIG_ADMIN,
        ]))
    )
    dp.add_handler(ordering_handler)
    dp.add_handler(show_checkout_list_handler)
    dp.add_handler(paid_handler)
    dp.add_handler(config_uc_handler)
    dp.add_handler(reset_checkout_list_handler)
    dp.add_handler(reset_checkout_list_query_handler)
    dp.add_handler(stop_ordering_handler)
    dp.add_handler(start_ordering_handler)
    dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
