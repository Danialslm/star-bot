import re

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    MessageHandler,
    ConversationHandler,
    Filters,
    CallbackQueryHandler,
    CommandHandler,
)

import settings
from utils import db, get_updated_user

GET_CREDENTIALS, HANDLE_ORDERING = range(2)

ORDER_ADMINS = settings.ORDER_ADMINS_GAP_1 + settings.ORDER_ADMINS_GAP_2
PAYER_ADMINS = [settings.ORDER_PAYER_CHAT_ID_1, settings.ORDER_PAYER_CHAT_ID_2]
PAYER_GROUPS = [settings.ORDER_GROUP_CHAT_ID_1, settings.ORDER_GROUP_CHAT_ID_2]


def create_tmp_checkout_list(checkout_list):
    return [
        {'uc': i['uc'], 'quantity': 0}
        for i in checkout_list
    ]


def new_order(update, context):
    if not db.get_ordering_state():
        update.message.reply_text('درحال حاظر فرایند ثبت سفارش متوقف شده است.')
        return ConversationHandler.END

    # initiate data
    context.user_data['uc_order'] = {'UCs': []}
    context.user_data['uc_list'] = db.get_uc_list()
    context.user_data['checkout_list'] = get_updated_user(
        context.user_data['uc_list'], update.message.chat_id, update.message.chat.first_name
    )['checkout_list']
    context.user_data['tmp_checkout_list'] = create_tmp_checkout_list(context.user_data['checkout_list'])

    update.message.reply_text('لطفا ایدی عددی و ایدی اسمی را ارسال کنید.\nبرای لغو فرایند /cancel را ارسال کنید.')
    return GET_CREDENTIALS


def get_credentials(update, context):
    def create_keyboard():
        # create uc ordering inline buttons
        keyboard = []

        counter = 0
        for uc in context.user_data['uc_list']:
            counter += 1
            if counter % 2 == 0:
                keyboard[-1].append(InlineKeyboardButton(str(uc['uc']) + ' 💶', callback_data=str(uc['uc'])))
            else:
                keyboard.append([InlineKeyboardButton(str(uc['uc']) + ' 💶', callback_data=str(uc['uc']))])

        keyboard.append([InlineKeyboardButton('ارسال سفارش', callback_data='send_order')])
        keyboard.append([InlineKeyboardButton('لغو سفارش', callback_data='cancel_ordering')])

        return keyboard

    credentials = update.message.text
    # validate given credentials
    try:
        uc_order = context.user_data['uc_order']
        id_, nick_name = credentials.split()

        if not bool(re.match(r'^\d+$', id_)):
            raise ValueError

        uc_order['id'] = id_
        uc_order['nick_name'] = nick_name
    except ValueError:
        text = (
            'فرمت ارسال مشخصات اشتباه است.\n'
            'مثال فرمت : \n'
            '0123456789\n'
            'starVihan\n\n'
            'نکته : اعداد باید به حروف انگلیسی باشد'
        )
        update.message.reply_text(text)
        return GET_CREDENTIALS

    reply_markup = InlineKeyboardMarkup(create_keyboard())
    update.message.reply_text('لطفا مقدار یوسی را وارد کنید.\n مقدار تا به الان : خالی', reply_markup=reply_markup)

    return HANDLE_ORDERING


def handle_ordering(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    uc_order = context.user_data['uc_order']
    checkout_list = context.user_data['checkout_list']
    tmp_checkout_list = context.user_data['tmp_checkout_list']

    if query.data == 'cancel_ordering':
        # cancel ordering
        query.edit_message_text('سفارش لغو شد.')
        return ConversationHandler.END

    elif query.data == 'send_order':
        # show some error if order was blank
        if not context.user_data['uc_order']['UCs']:
            context.bot.answer_callback_query(query.id, text='لیست خالی است!', show_alert=True)
            return HANDLE_ORDERING

        formatted_uc_list = '+'.join(uc_order['UCs'])
        # send uc order to specific chat id
        text = (
            f'ایدی عددی : {uc_order["id"]}\n'
            f'ایدی اسمی : {uc_order["nick_name"]}\n\n'
            f'تعداد یوسی : {formatted_uc_list}\n\n\n\n'
            f'فرستنده : {chat_id}'
        )

        if chat_id in settings.ORDER_ADMINS_GAP_1:
            context.bot.send_message(settings.ORDER_GROUP_CHAT_ID_1, text)

        elif chat_id in settings.ORDER_ADMINS_GAP_2:
            context.bot.send_message(settings.ORDER_GROUP_CHAT_ID_2, text)

        # update user checkout list
        for item in checkout_list:
            for tmp_item in tmp_checkout_list:
                if item['uc'] == tmp_item['uc']:
                    item['quantity'] += tmp_item['quantity']
                    break

        db.set_user(chat_id, query.message.chat.first_name, checkout_list)

        text = (
            f'سفارش به مقدار:\n\n {formatted_uc_list}\n ارسال شد'
        )
        query.edit_message_text(text)
        return ConversationHandler.END
    else:
        # update uc order
        selected_uc = query.data
        uc_order['UCs'].append(selected_uc)
        uc_order['total'] = sum(map(int, uc_order['UCs']))
        uc_order_until_now = '+'.join(uc_order['UCs'])

        text = (
            'لطفا مقدار یوسی را وارد کنید.\n'
            f'جمع مقدار یوسی تا به الان : {uc_order["total"]}\n'
            f'مقدار یوسی تا به الان : {uc_order_until_now}'
        )
        query.edit_message_text(text=text, reply_markup=query.message.reply_markup)

        # increase tmp_checkout_list quantity after selecting uc
        for item in tmp_checkout_list:
            if item['uc'] == int(selected_uc):
                item['quantity'] += 1
                break

        query.answer()
        return HANDLE_ORDERING


def cancel_ordering(update, context):
    update.message.reply_text('فرایند ثبت سفارش متوقف شد.')
    return ConversationHandler.END


def show_checkout_list(update, context):
    uc_list = db.get_uc_list()
    checkout_list = get_updated_user(uc_list, update.message.chat_id, update.message.chat.first_name)['checkout_list']
    total_uc_quantity_sold = 0
    total_sold = 0

    # calculate how much uc sold
    text = ''
    for uc_list_item in uc_list:
        for checkout_list_item in checkout_list:
            if uc_list_item['uc'] == checkout_list_item['uc']:
                quantity = checkout_list_item['quantity']

                total_uc_quantity_sold += quantity
                total_sold += uc_list_item['price'] * quantity
                text += f'تعداد سفارش {uc_list_item["uc"]} یوسی : {quantity}\n'
                break

    text += f'\nمجموع مبلغ : {total_sold} هزار تومان.\n'
    text += f'تعداد کل سفارشات امروز : {total_uc_quantity_sold}'
    update.message.reply_text(text)


def paid(update, context):
    payer_chat_id = update.message.from_user.id

    if payer_chat_id in PAYER_ADMINS:
        text = update.message.reply_to_message.text
        # send paid confirm message to order sender
        sender_chat_id = int(re.findall(r'فرستنده : (\d+)', text)[0])
        text += '\n\nاین لیست پرداخت شد✅.'

        context.bot.send_message(sender_chat_id, text)


# handlers
ordering_handler = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.regex('^ثبت سفارش جدید$') & Filters.chat(ORDER_ADMINS), new_order)
    ],
    states={
        GET_CREDENTIALS: [
            MessageHandler(Filters.text & ~Filters.command & Filters.chat(ORDER_ADMINS), get_credentials)
        ],
        HANDLE_ORDERING: [CallbackQueryHandler(handle_ordering)],
    },
    fallbacks=[CommandHandler('cancel', cancel_ordering)],
)

show_checkout_list_handler = MessageHandler(
    Filters.regex('^نمایش لیست تسویه حساب$') & Filters.chat(ORDER_ADMINS),
    show_checkout_list,
)

paid_handler = MessageHandler(
    Filters.regex('^✅$') & Filters.chat(PAYER_GROUPS) & Filters.reply,
    paid,
)
