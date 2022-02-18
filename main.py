#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from decouple import config as env
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler
import config
import models
from models import Base

# environments
CONFIG_ADMIN = env('CONFIG_ADMIN', cast=int)
DEBUG = env('DEBUG', default=False)

# logging
logging_config = {
    'level': logging.DEBUG,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}
if not DEBUG:
    logging_config.update({
        'level': logging.ERROR,
        'filename': 'log/error.log',
    })

logging.basicConfig(**logging_config)
logger = logging.getLogger(__name__)

# create a db engine and session maker and create all tables
engine = create_engine('sqlite:///star_bot.db', echo=DEBUG)  # echo queries in debug mode
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

session = Session()


def start(update, context):
    if not DEBUG:
        chat_id = update.effective_message.chat_id

        if chat_id == CONFIG_ADMIN:
            keyboard = [
                ['بروزرسانی لیست یوسی ها'],
                ['ریست لیست تسویه حساب'],
                ['قفل سفارش'],
                ['بازکردن سفارش'],
            ]
        else:
            admin = session.query(models.Admin.user_chat_id).filter(
                models.Admin.user_chat_id == chat_id,
            ).all()
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
            ['بروزرسانی لیست یوسی ها'],
            ['ریست لیست تسویه حساب'],
            ['قفل سفارش'],
            ['بازکردن سفارش'],
            ['اطلاعیه'],
        ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.effective_message.reply_text(
        'لطفا یکی از گزینه های زیر را انتخاب کنید.',
        reply_markup=reply_markup,
    )


def is_online(update, context):
    update.effective_message.reply_text('ربات انلاین است.')


def error_handler(update, context):
    logger.error('Update "%s" caused error "%s"', update, context.error)


def main():
    token = env('TOKEN')
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('online', is_online))
    # dp.add_handler(ordering_handler)
    # dp.add_handler(show_checkout_list_handler)
    # dp.add_handler(paid_handler)
    # dp.add_handler(config_uc_handler)
    # dp.add_handler(reset_checkout_list_handler)
    # dp.add_handler(reset_checkout_list_query_handler)
    # dp.add_handler(stop_ordering_handler)
    # dp.add_handler(start_ordering_handler)
    # dp.add_handler(send_notification_handler)
    # dp.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
