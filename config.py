import os
import re

from sqlalchemy.orm import joinedload
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Filters, MessageHandler, ConversationHandler,
    CallbackQueryHandler, CommandHandler,
)

import models
from db import Session
from env import CONFIG_ADMIN

# conversation levels
GET_UC_LIST, DECISION = range(2)  # update uc list
GET_NOTIFY_MSG = range(2, 3)  # send notification
GET_ADMIN_INFO = range(3, 4)  # add admin
GET_ADMIN_CHAT_ID = range(4, 5)  # remove admin

UPDATE_UC_LIST_TEXT = (
    'لطفا لیست جدید یوسی ها را با فرمت زیر ارسال کنید.\n'
    '60 - 60000\n'
    '120 - 120000\n\n'
    'نکته : تعداد یوسی سمت چپ و قیمت به تومان سمت راست است.\n\n'
    'برای لغو فرایند /cancel را ارسال کنید.'
)

ADD_ADMIN_TEXT = (
    'لطفا چت ایدی و نام مستعار ادمین و نام گروه (znxy یا star) را به فرمت زیر ارسال کنید:\n\n'
    'chat id - admin name - group\n\n'
    'برای لغو فرایند /cancel را ارسال کنید.'
)

session = Session()


def update_uc_list(update, context):
    context.user_data['new_uc_list'] = []

    update.message.reply_text(UPDATE_UC_LIST_TEXT)
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
            amount = i[0].strip()
            price = i[1].strip()

            if not (validate(amount) and validate(price)):
                raise ValueError
            else:
                new_uc_list.append({'amount': int(amount), 'price': int(price)})
    except (IndexError, ValueError):
        update.message.reply_text(UPDATE_UC_LIST_TEXT)
        return GET_UC_LIST
    else:
        text = 'لیست یوسی ها به شکل زیر خواهد شد.\n\n'
        for i in context.user_data['new_uc_list']:
            text += f'یوسی : {i["amount"]}\n'
            text += f'قیمت : {i["price"]} تومان\n\n'

        keyboard = [
            [InlineKeyboardButton('ارسال دوباره', callback_data='send_again')],
            [InlineKeyboardButton('ذخیره', callback_data='save')],
            [InlineKeyboardButton('لغو بروزرسانی', callback_data='cancel_updating')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text, reply_markup=reply_markup)
        return DECISION


def update_uc_decision(update, context):
    query = update.callback_query
    if query.data == 'send_again':
        context.user_data['new_uc_list'] = []
        query.edit_message_text(UPDATE_UC_LIST_TEXT)
        return GET_UC_LIST
    elif query.data == 'save':
        session.query(models.UC).delete()

        notify_text = 'اعلانیه\n لیست جدید یوسی ها:\n\n'
        for uc in context.user_data['new_uc_list']:
            session.add(models.UC(**uc))
            notify_text += f'یوسی {uc["amount"]} قیمت {uc["price"]} تومان\n\n'

        session.commit()
        session.close()

        # send update notification for all admins
        admins = session.query(models.Admin).all()
        for admin in admins:
            try:
                context.bot.send_message(admin.chat_id, notify_text)
            except Exception as e:
                context.bot.send_message(
                    query.message.chat_id,
                    f'برای کاربر {admin.name} ارسال نشد.\nدلیل : {e}'
                )

        query.edit_message_text('لیست یوسی ها بروز و به کاربران اطلاع داده شد.')
        return ConversationHandler.END
    elif query.data == 'cancel_updating':
        query.edit_message_text('بروزرسانی لیست یوسی ها لغو شد.')
        return ConversationHandler.END


def cancel_update_uc_list(update, context):
    update.message.reply_text('فرایند بروزرسانی لیست یوسی لغو شد.')
    return ConversationHandler.END


def add_admin(update, context):
    update.message.reply_text(ADD_ADMIN_TEXT)
    return GET_ADMIN_INFO


def get_admin_info(update, context):
    admin_info = update.message.text

    try:
        # validation
        admin_info = admin_info.split('-')

        # if there is more that two `-` in message text
        if len(admin_info) > 3:
            raise ValueError

        admin_chat_id = int(admin_info[0].strip())
        admin_name = admin_info[1].strip()
        admin_group = admin_info[2].strip().lower()

    except (IndexError, ValueError):
        update.message.reply_text(ADD_ADMIN_TEXT)
        return GET_ADMIN_INFO
    else:
        # check that admin does not already exists
        admin = session.query(models.Admin).filter(
            models.Admin.chat_id == admin_chat_id,
        ).first()

        if admin:
            text = (
                f'این ادمین با چت ایدی {admin.chat_id} '
                f'و نام مستعار {admin.name} '
                f'در گروه {admin.group} '
                'از قبل وجود دارد.'
            )
            update.message.reply_text(text)
            return ConversationHandler.END

        # save new admin info to database
        admin = models.Admin(chat_id=admin_chat_id, name=admin_name, group=admin_group)
        session.add(admin)
        session.commit()
        session.close()

        text = (
            f'ادمین جدید برای گروه {admin_group} با مشخصات زیر :\n'
            f'نام ادمین : {admin_name}\n'
            f'چت ایدی ادمین : {admin_chat_id}\n'
            'ذخیره شد.'
        )
        update.message.reply_text(text)
        return ConversationHandler.END


def cancel_add_admin(update, context):
    update.message.reply_text('فرایند افزودن ادمین لغو شد.')
    return ConversationHandler.END


def remove_admin(update, context):
    update.message.reply_text('لطفا چت ایدی ادمین را برای حذف ارسال کنید.\nبرای لغو فرایند /cancel را وارد کنید.')
    return GET_ADMIN_CHAT_ID


def get_admin_chat_id(update, context):
    try:
        admin_chat_id = int(update.message.text)
    except ValueError:
        update.message.reply_text('چت ایدی معتبر نیست لطفا دوباره وارد کنید.')
        return GET_ADMIN_CHAT_ID
    else:
        # check that admin is exist
        admin = session.query(models.Admin).filter(
            models.Admin.chat_id == admin_chat_id,
        ).first()

        if not admin:
            update.message.reply_text('ادمینی با این چت ایدی وجود ندارد. لطفا چت ایدی را دوباره وارد کنید')
            return GET_ADMIN_CHAT_ID

        # remove the admin and he's/she's checkout from database
        session.query(models.SoldUc).filter(
            models.SoldUc.admin_id == admin.id,
        ).delete()
        session.delete(admin)
        session.commit()
        session.close()

        text = (
            f'ادمین گپ {admin.group} با مشخصات زیر :\n\n'
            f'چت ایدی : {admin.chat_id}\n'
            f'نام مستعار : {admin.name}\n\n'
            'حذف شد.'
        )
        update.message.reply_text(text)
        return ConversationHandler.END


def cancel_remove_admin(update, context):
    update.message.reply_text('فرایند حذف ادمین لغو شد.')
    return ConversationHandler.END


def reset_admins_checkout(update, context):
    """ show admins total debt """
    text = 'لیست تسویه حساب همه کاربران:\n\n'
    admins = session.query(models.Admin). \
        options(joinedload(models.Admin.sold_ucs).joinedload(models.SoldUc.uc)). \
        all()

    for admin in admins:
        admin_total_debt = 0

        for sold_uc in admin.sold_ucs:
            admin_total_debt += sold_uc.uc.price * sold_uc.quantity

        text += (
            f'ادمین : {admin.name}\n'
            f'چت ایدی : {admin.chat_id}\n'
            f'بدهی : {admin_total_debt}\n\n'
        )
    session.close()
    keyboard = [
        [InlineKeyboardButton('ریست', callback_data='reset')],
        [InlineKeyboardButton('لغو', callback_data='cancel')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup)


def handle_reset_checkout_list(update, context):
    query = update.callback_query
    if query.data == 'cancel':
        query.edit_message_text('عملیات ریست کردن لیست تسویه حساب لغو شد.')
    elif query.data == 'reset':
        session.query(models.SoldUc).delete()
        session.commit()
        session.close()
        query.edit_message_text('لیست تسویه حساب کاربران ریست شد.')


def stop_ordering(update, context):
    try:
        del os.environ['ORDERING_STATE']
    except KeyError:
        pass
    update.message.reply_text('فرایند سفارش یوسی متوقف شد.')


def start_ordering(update, context):
    os.environ['ORDERING_STATE'] = 'open'
    update.message.reply_text('فرایند سفارش یوسی شروع شد.')


def new_notification(update, context):
    update.message.reply_text('لطفا پیام خود را ارسال کنید.\nبرای لغو فرایند دستور /cancel را وارد کنید.')
    return GET_NOTIFY_MSG


def get_notify_msg(update, context):
    msg = update.message.text
    for admin in session.query(models.Admin).all():
        try:
            context.bot.send_message(admin.chat_id, msg)
        except Exception as e:
            context.bot.send_message(update.message.chat_id, f'برای کاربر {admin.name} ارسال نشد.\nدلیل : {e}')

    update.message.reply_text('پیام شما برای همه کاربران ارسال شد.')
    session.close()
    return ConversationHandler.END


def cancel_new_notify(update, context):
    update.message.reply_text('فرایند ارسال اطلاعیه لغو شد.')
    return ConversationHandler.END


# handlers
config_uc_handler = ConversationHandler(
    entry_points=[MessageHandler(
        Filters.regex('^بروزرسانی لیست یوسی ها$') & Filters.chat([CONFIG_ADMIN]),
        update_uc_list,
    )],
    states={
        GET_UC_LIST: [MessageHandler(
            Filters.text & ~Filters.command & Filters.chat([CONFIG_ADMIN]),
            get_new_uc_list,
        )],
        DECISION: [CallbackQueryHandler(update_uc_decision)],
    },
    fallbacks=[CommandHandler('cancel', cancel_update_uc_list)],
)

add_admin_handler = ConversationHandler(
    entry_points=[MessageHandler(
        Filters.regex('^افزودن ادمین$') & Filters.chat([CONFIG_ADMIN]),
        add_admin,
    )],
    states={
        GET_ADMIN_INFO: [MessageHandler(
            Filters.text & ~Filters.command & Filters.chat([CONFIG_ADMIN]),
            get_admin_info,
        )],
    },
    fallbacks=[CommandHandler('cancel', cancel_add_admin)]
)

remove_admin_handler = ConversationHandler(
    entry_points=[MessageHandler(
        Filters.regex('^حذف ادمین$') & Filters.chat([CONFIG_ADMIN]),
        remove_admin,
    )],
    states={
        GET_ADMIN_CHAT_ID: [MessageHandler(
            Filters.text & ~Filters.command & Filters.chat([CONFIG_ADMIN]),
            get_admin_chat_id,
        )],
    },
    fallbacks=[CommandHandler('cancel', cancel_remove_admin)],
)

reset_checkout_list_handler = MessageHandler(
    Filters.regex('^ریست لیست تسویه حساب$') & Filters.chat([CONFIG_ADMIN]),
    reset_admins_checkout,
)

reset_checkout_list_query_handler = CallbackQueryHandler(handle_reset_checkout_list)

stop_ordering_handler = MessageHandler(
    Filters.regex('^قفل سفارش$') & Filters.chat([CONFIG_ADMIN]),
    stop_ordering,
)

start_ordering_handler = MessageHandler(
    Filters.regex('^بازکردن سفارش$') & Filters.chat([CONFIG_ADMIN]),
    start_ordering,
)

send_notification_handler = ConversationHandler(
    entry_points=[MessageHandler(
        Filters.regex('^اطلاعیه$') & Filters.chat([CONFIG_ADMIN]),
        new_notification,
    )],
    states={
        GET_NOTIFY_MSG: [MessageHandler(
            Filters.text & ~Filters.regex('^اطلاعیه$') & ~Filters.command & Filters.chat([CONFIG_ADMIN]),
            get_notify_msg,
        )]
    },
    fallbacks=[CommandHandler('cancel', cancel_new_notify)]
)
