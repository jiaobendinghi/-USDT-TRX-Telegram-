import configparser
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(str(BASE_DIR))
from pyromod.helpers import ikb

from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup,
                            InlineKeyboardButton)

try:
    ini_path = ".\\config.ini"
    read_ini = configparser.ConfigParser()
    read_ini.read(ini_path, 'UTF-8')

    group_link = read_ini['config']['group_link']
    support = read_ini['config']['support']

except:
    pro_path = os.path.split(os.path.realpath(__file__))[0]
    pro_path = str(pro_path).replace("/plugins", "")
    ini_path = f"{pro_path}/config.ini"
    read_ini = configparser.ConfigParser()
    read_ini.read(ini_path, 'UTF-8')

    group_link = read_ini['config']['group_link']
    support = read_ini['config']['support']


# 创始人主菜单普通键盘
def admin_main_menu():
    return ReplyKeyboardMarkup(
        [
            ["今日报表", "总报表"],  # First row
            ["最新汇率", "钱包余额"],  # Second row
            ["当前参数", "修改参数"]
        ],
        resize_keyboard=True  # Make the keyboard smaller
    )


def admin_main_menu_inline():
    return ikb([
        [('今日盈利', 'call_1'), ('所有盈利', 'call_2')]
    ])


def user_main_menu():
    return ReplyKeyboardMarkup(
        [
            ["兑换TRX", "个人中心"],  # First row
            ["我要推广", "预支TRX"],  # Second row
            ["绑定地址", "联系客服"]
        ],
        resize_keyboard=True  # Make the keyboard smaller
    )


def share():
    return InlineKeyboardMarkup(
        [
            [  # Second row
                InlineKeyboardButton(  # Opens the inline interface
                    "🔎分享",
                    switch_inline_query=""
                ),
                InlineKeyboardButton(  # Opens the inline interface
                    "🧾交易群",
                    url=f"{group_link}"
                ),
                InlineKeyboardButton(  # Opens the inline interface
                    "👨客服",
                    url=f"https://t.me/{support.replace('@', '')}"
                )
            ]
        ]
    )


def kefu():
    return InlineKeyboardMarkup(
        [
            [  # Second row
                InlineKeyboardButton(  # Opens the inline interface
                    "🔎分享",
                    switch_inline_query=""
                ),
                InlineKeyboardButton(  # Opens the inline interface
                    "🧾交易群",
                    url=f"{group_link}"
                ),
                InlineKeyboardButton(  # Opens the inline interface
                    "👨客服",
                    url=f"https://t.me/{support.replace('@', '')}"
                )
            ]
        ]
    )
