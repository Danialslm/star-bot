## Private telegram bot for [STAR team](https://t.me/pubg_star_ir) writen in python and [python-telegram-bot](https://python-telegram-bot.org/) library

### This bot made for make easier interaction for between star team staffs for selling uc (Pubg currency) .

---
## Installation
1. create a virtualenv by running `python3 -m virtualenv .venv`
2. install the dependencies by running `pip install -r requirements.txt`
3. create a telegram bot in @BotFather
4. rename the `env/.env.sample` to `env/.env` and replace your chat ids (also bot token which you got from bot father in previous step)
5. make executable the main script by running `sudo chmod 755 ./main.py`
6. run the main script by running `./main.py` and start the bot.

---
## Roles
the bot can have a config admin which defined in `env/.env` and also have many ordinary admins

#### config admin can define uc list, add or remove admin, lock and unlock order registration process, see and clear the admins' checkout list (how much did the admin sell uc)
#### the ordinary admins can only register orders and view their checkout list
#### at the end the notification sender admin which defined in `env/.env` can only send notification to all admins

___
this is my first README.md, so its may not very good :)
