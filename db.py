import json
import os.path


class Database:
    def __init__(self, filename: str = 'database.json'):
        if not os.path.exists(filename):
            mode = 'w+'
        else:
            mode = 'r'

        self.filename = filename
        with open(self.filename, mode) as database:
            database_data = database.read()
            # if database file doesn't have any data s  et 'self.database' to empty dictionary
            self.database = json.loads(database_data if database_data else '{}')

    def _save(self, data):
        # save data to database file
        with open(self.filename, 'w') as database:
            database.write(json.dumps(data))

    def get_users(self, just_ids=False):
        users = self.database.get('users', {})
        if just_ids:
            return users.keys()
        return users

    def get_user(self, chat_id):
        users = self.get_users()

        return users.get(str(chat_id), {})

    def get_uc_list(self):
        return self.database.get('uc_list', [])

    def get_ordering_state(self):
        return self.database.get('ordering_state', False)

    def set_uc_list(self, uc_list: list):
        if not isinstance(uc_list, list):
            raise ValueError('uc_list should be list')

        self.database['uc_list'] = uc_list

        self._save(self.database)
        return uc_list

    def set_user(self, chat_id: int, first_name: str, user_checkout_list: list):
        if not isinstance(chat_id, int):
            raise ValueError('chat_id should be int')
        if not isinstance(user_checkout_list, list):
            raise ValueError('user_checkout_list should be list')
        if not isinstance(first_name, str):
            raise ValueError('first_name should be string')

        chat_id = str(chat_id)

        users = self.get_users()
        users[chat_id] = {'first_name': first_name, 'checkout_list': user_checkout_list}

        self.database['users'] = users

        self._save(self.database)
        return users[chat_id]

    def clean_users(self):
        users = self.get_users()
        if users:
            self.database['users'] = {}
            self._save(self.database)
        return {}

    def set_ordering_state(self, ordering_state: bool):
        if not isinstance(ordering_state, bool):
            raise ValueError('checkout_list should be boolean')

        self.database['ordering_state'] = ordering_state

        self._save(self.database)
        return ordering_state


db = Database()
