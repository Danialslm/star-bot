from db import db


def get_updated_user(uc_list, chat_id, first_name):
    """ get or set user if not exist in db and return it. user checkout list will synced with uc list! """
    user = db.get_user(chat_id)

    if user:
        # check uc list
        # if uc list has been updated, we should update user checkout list too
        checkout_list = user['checkout_list']
        updated = False

        checkout_list_uc_values = [item['uc'] for item in checkout_list]
        uc_list_uc_values = [item['uc'] for item in uc_list]

        for item in uc_list:
            if item['uc'] not in checkout_list_uc_values:
                # some uc added to uc list so we should add it to checkout list too
                checkout_list.append({'uc': item['uc'], 'quantity': 0})
                updated = True

        for index, item in enumerate(checkout_list):
            if item['uc'] not in uc_list_uc_values:
                # some uc removed from uc list so we should remove it from checkout list too
                checkout_list.pop(index)
                updated = True

        if updated:
            # update checkout list
            db.set_user(chat_id, first_name, checkout_list)

    else:
        # if the user doesn't exist in db, create it
        checkout_list = []
        for i in uc_list:
            checkout_list_item = {'uc': i['uc'], 'quantity': 0}

            checkout_list.append(checkout_list_item)

        user = db.set_user(chat_id, first_name, checkout_list)
    return user
