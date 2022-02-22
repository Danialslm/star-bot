#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler

import env
import models
from db import Session, create_tables

# logging
logging_config = {
    'level': logging.DEBUG,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}
if not env.DEBUG:
    logging_config.update({
        'level': logging.ERROR,
        'filename': 'log/error.log',
    })

logging.basicConfig(**logging_config)
logger = logging.getLogger(__name__)

session = Session()


def start(update, context):
    if not env.DEBUG:
        chat_id = update.message.chat_id

        if chat_id == env.CONFIG_ADMIN:
            keyboard = [
                ['افزودن ادمین'],
                ['حذف ادمین'],
                ['بروزرسانی لیست یوسی ها'],
                ['ریست لیست تسویه حساب'],
                ['قفل سفارش'],
                ['بازکردن سفارش'],
            ]
        else:
            admin = session.query(models.Admin.chat_id).filter(
                models.Admin.chat_id == chat_id,
            ).first()
            session.close()
            # if the user does not admin, do nothing
            if not admin:
                return

            keyboard = [
                ['ثبت سفارش جدید'],
                ['نمایش لیست تسویه حساب'],
            ]
    else:
        keyboard = [
            ['ثبت سفارش جدید'],
            ['نمایش لیست تسویه حساب'],
            ['افزودن ادمین'],
            ['حذف ادمین'],
            ['بروزرسانی لیست یوسی ها'],
            ['ریست لیست تسویه حساب'],
            ['قفل سفارش'],
            ['بازکردن سفارش'],
            ['اطلاعیه'],
        ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        'لطفا یکی از گزینه های زیر را انتخاب کنید.',
        reply_markup=reply_markup,
    )


def is_online(update, context):
    update.message.reply_text('ربات انلاین است.')


def error_handler(update, context):
    logger.error('Update "%s" caused error "%s"', update, context.error)


def main():
    create_tables()

    token = env.TOKEN
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('online', is_online))
    dp.add_error_handler(error_handler)

    import config
    import ordering
    dp.add_handler(ordering.ordering_handler)
    dp.add_handler(ordering.show_admin_checkout_handler)
    dp.add_handler(ordering.paid_handler)
    dp.add_handler(config.config_uc_handler)
    dp.add_handler(config.add_admin_handler)
    dp.add_handler(config.remove_admin_handler)
    dp.add_handler(config.stop_ordering_handler)
    dp.add_handler(config.start_ordering_handler)
    # dp.add_handler(config.reset_checkout_list_handler)
    # dp.add_handler(reset_checkout_list_query_handler)
    dp.add_handler(config.send_notification_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
