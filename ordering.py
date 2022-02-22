import os
import re

from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    MessageHandler, ConversationHandler, Filters,
    CallbackQueryHandler, CommandHandler,
)

import models
from db import Session
from env import (
    STAR_GROUP_CHAT_ID, ZNXY_GROUP_CHAT_ID,
    PAYERS_CHAT_ID
)

# conversation levels
GET_CREDENTIALS, HANDLE_ORDERING = range(2)

NEW_ORDER_TEXT = (
    'لطفا ایدی عددی و ایدی اسمی را با فرمت زیر :\n'
    'id - nickname\n'
    'ارسال کنید.\n'
    'برای لغو فرایند /cancel را ارسال کنید.'
)

session = Session()


def new_order(update, context):
    # check user is admin
    admin = session.query(models.Admin.chat_id).filter(
        models.Admin.chat_id == update.message.chat_id,
    ).first()
    if not admin:
        session.close()
        return ConversationHandler.END

    # check ordering state
    if not os.environ.get('ORDERING_STATE', False):
        update.message.reply_text('درحال حاضر فرایند ثبت سفارش متوقف شده است.')
        return ConversationHandler.END

    update.message.reply_text(NEW_ORDER_TEXT)
    return GET_CREDENTIALS


def get_credentials(update, context):
    ucs = session.query(models.UC).all()
    context.user_data['order'] = {'ucs_amount': []}
    context.user_data['tmp_checkout'] = [
        {'amount': uc.amount, 'quantity': 0} for uc in ucs
    ]

    def create_keyboard():
        """ create inline keyboard based on ucs """
        keyboard = []

        counter = 0
        for uc in ucs:
            counter += 1
            btn = InlineKeyboardButton(str(uc.amount) + ' 💶', callback_data=str(uc.amount))
            if counter % 2 == 0:
                keyboard[-1].append(btn)
            else:
                keyboard.append([btn])

        keyboard.append([InlineKeyboardButton('ارسال سفارش', callback_data='send_order')])
        keyboard.append([InlineKeyboardButton('لغو سفارش', callback_data='cancel_ordering')])

        return keyboard

    credentials = update.message.text
    try:
        # validate given credentials
        id_, nickname = credentials.split('-')

        if not bool(re.match(r'^\d+$', id_)):
            raise ValueError

        context.user_data['order']['id'] = id_
        context.user_data['order']['nickname'] = nickname
    except ValueError:
        update.message.reply_text(NEW_ORDER_TEXT)
        return GET_CREDENTIALS

    reply_markup = InlineKeyboardMarkup(create_keyboard())
    update.message.reply_text('لطفا مقدار یوسی را وارد کنید.\n مقدار تا به الان : خالی', reply_markup=reply_markup)

    return HANDLE_ORDERING


def update_admin_sold_ucs(admin_id, checkout):
    """ update admin sold ucs based on given checkout """
    for c in checkout:
        if c['quantity'] == 0:
            continue

        uc_obj = session.query(models.UC).filter(
            models.UC.amount == c['amount'],
        ).first()

        sold_uc_obj = session.query(models.SoldUc).filter(and_(
            models.SoldUc.admin_id == admin_id,
            models.SoldUc.uc_id == uc_obj.id,
        )).first()
        # if admin already sold this uc, increase its quantity.
        # if admin doesn't sold any same uc, create SoldUc object and add it to session
        if sold_uc_obj:
            sold_uc_obj.quantity += c['quantity']
        else:
            session.add(models.SoldUc(
                admin_id=admin_id,
                uc_id=uc_obj.id,
                quantity=c['quantity'],
            ))

    session.commit()


def handle_ordering(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    order = context.user_data['order']

    if query.data == 'cancel_ordering':
        # cancel ordering
        query.edit_message_text('سفارش لغو شد.')
        session.close()
        return ConversationHandler.END

    elif query.data == 'send_order':
        # show alert if admin trying to send empty order
        if not context.user_data['order']['ucs_amount']:
            context.bot.answer_callback_query(query.id, text='لیست خالی است!', show_alert=True)
            return HANDLE_ORDERING

        formatted_ucs_amount = '+'.join(order['ucs_amount'])

        # send uc order to admin group chat id
        text = (
            f'ایدی عددی : {order["id"]}\n'
            f'ایدی اسمی : {order["nickname"]}\n\n'
            f'مقدار یوسی : {formatted_ucs_amount}\n\n\n\n'
            f'فرستنده : {chat_id}'
        )

        admin = session.query(models.Admin).filter(
            models.Admin.chat_id == chat_id,
        ).first()

        if admin.group == 'star':
            context.bot.send_message(STAR_GROUP_CHAT_ID, text)
        elif admin.group == 'znxy':
            context.bot.send_message(ZNXY_GROUP_CHAT_ID, text)

        update_admin_sold_ucs(admin.id, context.user_data['tmp_checkout'])
        text = (
            f'سفارش به مقدار:\n\n {formatted_ucs_amount}\n ارسال شد'
        )
        query.edit_message_text(text)
        session.close()
        return ConversationHandler.END
    else:
        # update the order
        selected_uc = query.data
        order['ucs_amount'].append(selected_uc)
        order['total_amount'] = sum(map(int, order['ucs_amount']))
        order_until_now = '+'.join(order['ucs_amount'])

        text = (
            'لطفا مقدار یوسی را وارد کنید.\n'
            f'جمع مقدار یوسی تا به الان : {order["total_amount"]}\n'
            f'مقدار یوسی تا به الان : {order_until_now}'
        )
        query.edit_message_text(text=text, reply_markup=query.message.reply_markup)

        # update the temporary checkout
        for item in context.user_data['tmp_checkout']:
            if item['amount'] == int(selected_uc):
                item['quantity'] += 1
                break

        query.answer()
        return HANDLE_ORDERING


def cancel_ordering(update, context):
    update.message.reply_text('فرایند ثبت سفارش متوقف شد.')
    session.close()
    return ConversationHandler.END


def show_admin_checkout(update, context):
    chat_id = update.message.chat_id

    # check user is admin
    admin = session.query(models.Admin).filter(
        models.Admin.chat_id == chat_id,
    ).options(joinedload(models.Admin.sold_ucs).joinedload(models.SoldUc.uc)).first()
    if not admin:
        return

    text = ''
    total_sold = 0

    for sold_uc in admin.sold_ucs:
        total_sold += sold_uc.uc.price * sold_uc.quantity

        text += f'تعداد سفارش {sold_uc.uc.amount} یوسی : {sold_uc.quantity}\n'

    text += f'\nمجموع مبلغ : {total_sold} هزار تومان.\n'
    update.message.reply_text(text)
    session.close()


def paid(update, context):
    payer_chat_id = update.message.from_user.id

    if payer_chat_id in PAYERS_CHAT_ID:
        text = update.message.reply_to_message.text
        # send paid confirm message to order sender
        sender_chat_id = int(re.findall(r'فرستنده : (\d+)', text)[0])
        text += '\n\nاین لیست پرداخت شد✅.'

        context.bot.send_message(sender_chat_id, text)


# handlers
ordering_handler = ConversationHandler(
    entry_points=[MessageHandler(
        Filters.regex('^ثبت سفارش جدید$'),
        new_order,
    )],
    states={
        GET_CREDENTIALS: [MessageHandler(
            Filters.text & ~Filters.command,
            get_credentials,
        )],
        HANDLE_ORDERING: [CallbackQueryHandler(handle_ordering)],
    },
    fallbacks=[CommandHandler('cancel', cancel_ordering)],
)

show_admin_checkout_handler = MessageHandler(
    Filters.regex('^نمایش لیست تسویه حساب$'),
    show_admin_checkout,
)

paid_handler = MessageHandler(
    Filters.regex('^✅$') & Filters.chat([STAR_GROUP_CHAT_ID, ZNXY_GROUP_CHAT_ID]) & Filters.reply,
    paid,
)
