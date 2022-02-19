import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, MessageHandler, ConversationHandler, CallbackQueryHandler, CommandHandler

import models
from env import CONFIG_ADMIN
from main import Session

# conversation levels
GET_UC_LIST, DECISION = range(2)
GET_NOTIFY_MSG = range(2, 3)

CONFIG_UC_TEXT = (
    'لطفا لیست جدید یوسی ها را با فرمت زیر ارسال کنید.\n'
    'برای لغو فرایند /cancel را ارسال کنید.\n\n'
    '60 - 60000\n'
    '120 - 120000\n\n'
    'نکته : تعداد یوسی سمت چپ و قیمت به تومان سمت راست است.'
)

session = Session()


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
            amount = i[0].strip()
            price = i[1].strip()

            if not (validate(amount) and validate(price)):
                raise ValueError
            else:
                new_uc_list.append({'amount': int(amount), 'price': int(price)})
    except (IndexError, ValueError):
        update.message.reply_text(CONFIG_UC_TEXT)
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


def decision(update, context):
    query = update.callback_query
    if query.data == 'send_again':
        context.user_data['new_uc_list'] = []
        query.edit_message_text(CONFIG_UC_TEXT)
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
                context.bot.send_message(admin.user_chat_id, notify_text)
            except Exception as e:
                context.bot.send_message(
                    query.message.chat_id,
                    f'برای کاربر {admin.admin_name} ارسال نشد.\nدلیل : {e.message}'
                )

        query.edit_message_text('لیست یوسی ها بروز و به کاربران اطلاع داده شد.')
        return ConversationHandler.END
    elif query.data == 'cancel_updating':
        query.edit_message_text('بروزرسانی لیست یوسی ها لغو شد.')
        return ConversationHandler.END


def cancel_update_uc_list(update, context):
    update.message.reply_text('فرایند بروزرسانی لیست یوسی لغو شد.')
    return ConversationHandler.END


# def reset_checkout_list(update, context):
#     text = 'لیست تسویه حساب همه کاربران:\n\n'
#     checkout_list = session.query(models.CheckoutUc). \
#         join(models.Checkout). \
#         join(models.UC). \
#         all()
#
#     for checkout in checkout_list:
#         user_total_debt = 0
#         admin_name = checkout.admin.admin_name
#         print(admin_name)
#     for uc in checkout.ucs.all():
#         for item in values['checkout_list']:
#             if uc['uc'] == item['uc']:
#                 user_total_debt += uc['price'] * item['quantity']
#                 break
#
#     text += f'ادمین : {admin_name}\n'
#     text += f'نام : {user_first_name}\n'
#     text += f'چت ایدی : {user}\n'
#     text += f'بدهی : {user_total_debt}\n\n'
#
# keyboard = [
#     [InlineKeyboardButton('ریست', callback_data='reset')],
#     [InlineKeyboardButton('لغو', callback_data='cancel')],
# ]
# reply_markup = InlineKeyboardMarkup(keyboard)
# update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')


# def handle_reset_checkout_list(update, context):
#     query = update.callback_query
#     if query.data == 'cancel':
#         query.edit_message_text('عملیات ریست کردن لیست تسویه حساب لغو شد.')
#     elif query.data == 'reset':
#         db.clean_users()
#         query.edit_message_text('لیست تسویه حساب کاربران ریست شد.')
#
#
# def stop_ordering(update, context):
#     db.set_ordering_state(False)
#
#     update.message.reply_text('فرایند سفارش یوسی متوقف شد.')
#
#
# def start_ordering(update, context):
#     db.set_ordering_state(True)
#
#     update.message.reply_text('فرایند سفارش یوسی شروع شد.')
#
#
# def new_notification(update, context):
#     update.message.reply_text('لطفا پیام خود را ارسال کنید.\nبرای لغو فرایند دستور /cancel را وارد کنید.')
#     return GET_NOTIFY_MSG
#
#
# def get_notify_msg(update, context):
#     msg = update.message.text
#     for user in ORDER_ADMINS:
#         try:
#             context.bot.send_message(user, msg)
#         except Exception as e:
#             context.bot.send_message(update.message.chat_id, f'برای کاربر {user} ارسال نشد.\nدلیل : {e.message}')
#
#     update.message.reply_text('پیام شما برای همه کاربران ارسال شد.')
#     return ConversationHandler.END
#
#
# def cancel_new_notify(update, context):
#     update.message.reply_text('فرایند ارسال اطلاعیه لغو شد.')
#     return ConversationHandler.END


# handlers
config_uc_handler = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.regex('^بروزرسانی لیست یوسی ها$') &
                       Filters.chat([CONFIG_ADMIN]),
                       config_uc_list)
    ],
    states={
        GET_UC_LIST: [MessageHandler(Filters.text &
                                     ~Filters.command &
                                     Filters.chat([CONFIG_ADMIN]),
                                     get_new_uc_list)],
        DECISION: [CallbackQueryHandler(decision)],
    },
    fallbacks=[CommandHandler('cancel', cancel_update_uc_list)],
)

# reset_checkout_list_handler = MessageHandler(
#     Filters.regex('^ریست لیست تسویه حساب$') & Filters.chat([CONFIG_ADMIN]),
#     reset_checkout_list,
# )

# reset_checkout_list_query_handler = CallbackQueryHandler(handle_reset_checkout_list)
#
# stop_ordering_handler = MessageHandler(
#     Filters.regex('^قفل سفارش$') & Filters.chat([settings.CONFIG_ADMIN]),
#     stop_ordering,
# )
#
# start_ordering_handler = MessageHandler(
#     Filters.regex('^بازکردن سفارش$') & Filters.chat([settings.CONFIG_ADMIN]),
#     start_ordering,
# )
#
# send_notification_handler = ConversationHandler(
#     entry_points=[MessageHandler(
#         Filters.regex('^اطلاعیه$') & Filters.chat([settings.NOTIFY_SENDER]),
#         new_notification,
#     )],
#     states={
#         GET_NOTIFY_MSG: [MessageHandler(
#             Filters.text & ~Filters.regex('^اطلاعیه$') & ~Filters.command & Filters.chat([settings.NOTIFY_SENDER]),
#             get_notify_msg,
#         )]
#     },
#     fallbacks=[CommandHandler('cancel', cancel_new_notify)]
# )
