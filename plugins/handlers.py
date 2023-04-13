import configparser
import datetime
import json
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(str(BASE_DIR))
from pyrogram import Client, filters, enums, StopPropagation
import plugins.keyboards as k
import data.data as d
import time
import plugins.functions as f
from pyrogram.types import BotCommand
import global_var

d = d.Database()
try:
    ini_path = ".\\config.ini"
    read_ini = configparser.ConfigParser()
    read_ini.read(ini_path, 'UTF-8')
    exchange_rate = read_ini.getfloat('config', 'exchange_rate')
    usdt_to_cny = read_ini.getfloat('config', 'usdt_to_cny')

    address = read_ini['config']['address']

    admin_ID = read_ini.getint('config', 'admin_ID')

    Minimum_exchange_value = read_ini.getint('config', 'Minimum_exchange_value')
    group_ID = read_ini.getint('config', 'group_ID')
    fee = read_ini.getfloat('config', 'fee')
    borrow_trx = read_ini.getint('config', 'borrow_trx')
    support = read_ini['config']['support']
    borrow_condition = read_ini.getint('config', 'borrow_condition')
    bot_link = read_ini['config']['bot_link']
except:
    pro_path = os.path.split(os.path.realpath(__file__))[0]
    pro_path = str(pro_path).replace("/plugins", "")
    ini_path = f"{pro_path}/config.ini"
    read_ini = configparser.ConfigParser()
    read_ini.read(ini_path, 'UTF-8')
    exchange_rate = read_ini.getfloat('config', 'exchange_rate')
    usdt_to_cny = read_ini.getfloat('config', 'usdt_to_cny')

    address = read_ini['config']['address']

    admin_ID = read_ini.getint('config', 'admin_ID')

    Minimum_exchange_value = read_ini.getint('config', 'Minimum_exchange_value')
    group_ID = read_ini.getint('config', 'group_ID')
    fee = read_ini.getfloat('config', 'fee')
    borrow_trx = read_ini.getint('config', 'borrow_trx')
    support = read_ini['config']['support']
    borrow_condition = read_ini.getint('config', 'borrow_condition')
    bot_link = read_ini['config']['bot_link']

ADMIN_ID_LIST = [admin_ID, ]


@Client.on_message(filters.command(["start", "help"]))
async def start_handler(client, message):

    if message.from_user and not message.from_user.is_bot:
        if message.from_user.id in ADMIN_ID_LIST:
            await client.set_bot_commands([BotCommand("start", "开始使用")])

            await message.reply("欢迎，管理员！", reply_markup=k.admin_main_menu())
        else:
            await client.set_bot_commands([BotCommand("start", "开始使用")])

            try:
                user_name = message.from_user.first_name + " " + message.from_user.last_name
            except:
                user_name = message.from_user.first_name
            await message.reply(f"{user_name}，你好，欢迎使用TRX钱庄！", reply_markup=k.user_main_menu())
            txt = f"**💹实时汇率\n100 USDT = {round(exchange_rate * fee * 100, 2)} TRX**\n\n**TRX钱庄自动兑换地址**\n<code>{address}</code>\n\n" \
                  f"💡进U即兑,全自动返TRX,{Minimum_exchange_value}U起兑\n👉请认准靓号**{str(address)[-7:]}**结尾\n⚠️勿用交易所或中心化钱包转账"
            await client.send_photo(message.chat.id, "https://img.tg.sb/file/4b72d7db15ebec9c80e0b.jpg", txt,
                                    reply_markup=k.share())

            if not await d.select_one_record_condition('user', 'user_id=?', (message.from_user.id,)):
                current_timestamp = int(time.time())
                await d.insert_record('user', (message.from_user.id, 0, 0, 0, current_timestamp, current_timestamp))

            try:

                link = f"https://t.me/tomato_trx_bot?start={message.text.split(' ')[1]}"

                r = await d.select_all_records_condition('tuiguang', 'link=?', (link,))
                if r:

                    c = await d.select_all_records_condition('user', 'user_id=?', (message.from_user.id,))
                    if c[0]['head_id'] == 0:
                        if message.from_user.id != r[0]['user_id']:
                            old_count = r[0]['shuliang']
                            new_count = old_count + 1

                            await d.update_record('tuiguang', 'shuliang', new_count,
                                                  f"user_id='{r[0]['user_id']}'")

                            await d.update_record('user', 'head_id', r[0]['user_id'],
                                                  f"user_id='{message.from_user.id}'")



                else:
                    pass

            except:
                pass


@Client.on_message(filters.regex("兑换TRX") & filters.private)
async def exchange_trx_handler(client, message):
    txt = f"**💹实时汇率\n100 USDT = {round(exchange_rate * fee * 100, 2)} TRX**\n\n**TRX钱庄自动兑换地址**\n<code>{address}</code>\n\n" \
          f"💡进U即兑,全自动返TRX,{Minimum_exchange_value}U起兑\n👉请认准靓号**{str(address)[-7:]}**结尾\n⚠️勿用交易所或中心化钱包转账\n\n转帐前，推荐您先<code>绑定地址</code>来接收入账通知"
    await message.reply(txt, reply_markup=k.share())


@Client.on_message(filters.regex("个人中心") & filters.private)
async def personal_center_handler(client, message):
    record = await d.select_one_record_condition('user', 'user_id=?', (message.from_user.id,))
    address = await d.select_all_records_condition('address', 'user_id=?', (message.from_user.id,))
    r = await d.select_all_records_condition('tuiguang', 'user_id=?', (message.from_user.id,))
    try:
        tuiguangjifen = r[0]['shuliang'] * 10
    except:
        tuiguangjifen = 0
    jifen = 0
    if address:
        txt = ''
        n = 0
        for i in address:
            address = i['address']
            n = n + 1
            address1 = address[0:7] + '*' + address[-8:]
            s = f"<a href='https://tronscan.org/#/address/{address}'>{address1}</a>\n"
            txt = txt + s

            e = await d.select_all_records_condition('transfer', 'accept_address=?', (address,))
            for z in e:
                jifen = jifen + z['usdt']
        msg = f'📦**绑定地址（{n}）**\n\n'
        txt1 = msg + txt
    else:
        txt1 = "⚠️还未绑定任何地址哦~"
    txt = f"📚**个人中心**\n\n用户ID: <code>{record['user_id']}</code>\n兑换积分: **{jifen}**\n推广积分: **{tuiguangjifen}**\n\n{txt1}"
    await message.reply(txt, disable_web_page_preview=True)


@Client.on_message(filters.regex("绑定地址") & filters.private)
async def bind_address_handler(client, message):
    while True:
        answer = await message.chat.ask('请回复需要绑定的地址')
        if len(answer.text) <= 10:
            break
        if await f.is_usdt(answer.text):

            r = await d.select_one_record_condition('address', 'address=?', (answer.text,))
            if r:
                await message.reply(f'⚠️该地址已被绑定，如有疑问，请联系客服处理  {support}')
                break
            else:
                current_timestamp = int(time.time())
                await d.insert_record('address',
                                      (message.from_user.id, answer.text, current_timestamp, current_timestamp))
                await message.reply('✅绑定成功')
                break
        else:
            await message.reply('⚠️输入的地址有误，请重新输入')


@Client.on_message(filters.regex("联系客服"))
async def contact_us_handler(client, message):
    await message.reply(f"https://t.me/{support.replace('@', '')}")


@Client.on_message(filters.regex("预支TRX") & filters.private)
async def advance_trx_handler(client, message):
    await message.reply("系统正在处理中....")
    try:
        ini_path = ".\\config.ini"
        read_ini = configparser.ConfigParser()
        read_ini.read(ini_path, 'UTF-8')
        pay_address = read_ini['config']['pay_address']
        pay_address_private_key = global_var.get_value('key')
    except:
        pro_path = os.path.split(os.path.realpath(__file__))[0]
        pro_path = str(pro_path).replace("/plugins", "")
        ini_path = f"{pro_path}/config.ini"
        read_ini = configparser.ConfigParser()
        read_ini.read(ini_path, 'UTF-8')
        pay_address = read_ini['config']['pay_address']
        pay_address_private_key = global_var.get_value('key')

    leiji_u = borrow_condition

    r = await d.select_all_records_condition('address', 'user_id=?', (message.from_user.id,))

    if r:

        if len(r) == 1:


            c = await d.select_all_records_condition('borrow', 'address=?', (r[0]['address'],))
            if c:
                if c[0]['outstanding_amount'] == 0:

                    await d.update_record('borrow', 'outstanding_amount', borrow_trx,
                                          f"address='{str(r[0]['address'])}'")

                    await message.reply('✅预支成功！')

                    await f.transfer(pay_address, pay_address_private_key, r[0]['address'],
                                     borrow_trx)
                else:
                    await message.reply('⚠️您所绑定的地址已经预支过啦~归还之后才能再次预支')
            else:
                jifen = 0
                e = await d.select_all_records_condition('transfer', 'accept_address=?', (r[0]['address'],))
                for z in e:
                    jifen = jifen + z['usdt']
                if jifen < leiji_u:
                    await message.reply(f'⚠️该地址的累计兑换数量不足{leiji_u}USDT，暂时不能预支')
                else:
                    current_timestamp = int(time.time())
                    await d.insert_record('borrow', (
                        message.from_user.id, str(r[0]['address']), 0, borrow_trx, 1, current_timestamp,
                        current_timestamp))

                    await message.reply('✅预支成功！')

                await f.transfer(pay_address, pay_address_private_key, r[0]['address'],
                                 borrow_trx)

        else:

            answer = await message.chat.ask('⚠️您绑定了多个地址，请回复您需要预支的地址')

            if len(answer.text) >= 10:
                c = await d.select_all_records_condition('borrow', 'address=?', (answer.text,))
                if c:
                    if c[0]['outstanding_amount'] == 0:

                        await d.update_record('borrow', 'outstanding_amount', borrow_trx,
                                              f"address='{answer.text}'")

                        await message.reply('✅预支成功！')

                        await f.transfer(pay_address, pay_address_private_key, answer.text,
                                         borrow_trx)
                    else:
                        await message.reply('⚠️您所绑定的地址已经预支过啦~归还之后才能再次预支')
                else:
                    jifen = 0
                    e = await d.select_all_records_condition('transfer', 'accept_address=?', (answer.text,))
                    for z in e:
                        jifen = jifen + z['usdt']
                    if jifen < leiji_u:
                        await message.reply(f'⚠️该地址的累计兑换数量不足{leiji_u}USDT，暂时不能预支')
                    else:
                        current_timestamp = int(time.time())
                        await d.insert_record('borrow', (
                            message.from_user.id, str(answer.text), 0, borrow_trx, 1, current_timestamp,
                            current_timestamp))

                        await message.reply('✅预支成功！')

                    await f.transfer(pay_address, pay_address_private_key, answer.text,
                                     borrow_trx)
    else:

        answer = await message.chat.ask('⚠️您还未绑定任何地址，请回复您需要预支的地址')

        if len(answer.text) >= 10:
            c = await d.select_all_records_condition('borrow', 'address=?', (answer.text,))
            if c:
                if c[0]['outstanding_amount'] == 0:

                    await d.update_record('borrow', 'outstanding_amount', borrow_trx,
                                          f"address='{answer.text}'")

                    current_timestamp = int(time.time())

                    await d.insert_record('address',
                                          (message.from_user.id, answer.text, current_timestamp, current_timestamp))

                    await message.reply('✅预支成功！')

                    await f.transfer(pay_address, pay_address_private_key, answer.text,
                                     borrow_trx)
                else:
                    await message.reply('⚠️您所输入的地址已经预支过啦~归还之后才能再次预支')
            else:
                jifen = 0
                e = await d.select_all_records_condition('transfer', 'accept_address=?', (answer.text,))
                for z in e:
                    jifen = jifen + z['usdt']
                if jifen < leiji_u:
                    await message.reply(f'⚠️您的累计兑换数量不足{leiji_u}USDT，暂时不能预支')
                else:
                    current_timestamp = int(time.time())
                    await d.insert_record('borrow', (
                        message.from_user.id, str(answer.text), 0, borrow_trx, 1, current_timestamp,
                        current_timestamp))

                    current_timestamp = int(time.time())

                    await d.insert_record('address',
                                          (message.from_user.id, answer.text, current_timestamp, current_timestamp))

                    await message.reply('✅预支成功！')

                    await f.transfer(pay_address, pay_address_private_key, answer.text,
                                     borrow_trx)


@Client.on_message(filters.regex("我要推广") & filters.private)
async def tui_guang(client, message):
    r = await d.select_all_records_condition('tuiguang', 'user_id=?', (message.from_user.id,))
    if r:

        await message.reply(
            f"快推荐给他人使用吧~\n推广的人数越多，奖励的积分越多\n积分可用来兑换靓号，兑换费率变得更低哦~\n\n👉推广链接：<code>{r[0]['link']}</code>",
            disable_web_page_preview=True)
    else:

        link = f"{bot_link}?start={f.random_str()}"

        await d.insert_record('tuiguang',
                              (message.from_user.id, link, 0))

        await message.reply(
            f"快推荐给他人使用吧~\n推广的人数越多，奖励的积分越多\n积分可用来兑换靓号，兑换费率变得更低哦~\n\n👉推广链接：<code>{link}</code>",
            disable_web_page_preview=True)


@Client.on_message(filters.regex("今日报表") & filters.private)
async def jin_ri_bao_biao(client, message):
    if message.from_user.id in ADMIN_ID_LIST:

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        r = await d.select_all_records('transfer')
        if r:

            now_time = f.get_today_start_end_timestamp()
            z = 0
            z_usdt = 0
            z_trx = 0
            z_broadband = 0
            z_burn_trx = 0
            z_borrow_trx = 0
            z_yingli = 0
            for i in r:
                if now_time[0] <= i['time'] <= now_time[1]:
                    z = z + 1
                    z_usdt = z_usdt + i['usdt']
                    z_trx = z_trx + i['trx']
                    z_broadband = z_broadband + i['broadband']
                    z_burn_trx = z_burn_trx + i['burn_trx']

            trx_to_cny = f.get_trx_to_cny(usdt_to_cny, exchange_rate)
            z_yingli = z_usdt * exchange_rate - z_burn_trx - z_trx
            z_rmb = z_yingli * trx_to_cny

            txt = f"**今日报表**\n\n<code>转入USDT：**{z_usdt}**\n转出TRX：**{z_trx}**\n\n消耗宽带：{z_broadband}\n燃烧TRX：{z_burn_trx}\n\n盈利：{z_yingli}trx→{z_rmb}cny\n\n更新时间：{now}</code>"

            await message.reply(txt)
        else:
            await message.reply('暂无数据')


@Client.on_message(filters.regex("总报表") & filters.private)
async def zong_bao_biao(client, message):
    if message.from_user.id in ADMIN_ID_LIST:

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        r = await d.select_all_records('transfer')
        if r:

            z = 0
            z_usdt = 0
            z_trx = 0
            z_broadband = 0
            z_burn_trx = 0
            z_borrow_trx = 0
            z_yingli = 0
            for i in r:
                z = z + 1
                z_usdt = z_usdt + i['usdt']
                z_trx = z_trx + i['trx']
                z_broadband = z_broadband + i['broadband']
                z_burn_trx = z_burn_trx + i['burn_trx']

            trx_to_cny = f.get_trx_to_cny(usdt_to_cny, exchange_rate)
            z_yingli = z_usdt * exchange_rate - z_burn_trx - z_trx
            z_rmb = z_yingli * trx_to_cny

            txt = f"**总报表**\n\n<code>转入USDT：**{z_usdt}**\n转出TRX：**{z_trx}**\n\n消耗宽带：{z_broadband}\n燃烧TRX：{z_burn_trx}\n\n盈利：{round(z_yingli)}trx→{round(z_rmb)}cny\n\n更新时间：{now}</code>"

            await message.reply(txt)
        else:
            await message.reply('暂无数据')


@Client.on_message(filters.regex("最新汇率") & filters.private)
async def huilv(client, message):
    if message.from_user.id in ADMIN_ID_LIST:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        txt = f"**最新汇率**\n\n<code>USDT→CNY：{f.get_usdt_to_cny()}\nUSDT→TRX：{f.get_trx()}\n\n更新时间：{now}</code>"

        await message.reply(txt)


@Client.on_message(filters.regex("钱包余额") & filters.private)
async def qian_bao_yu_e(client, message):
    if message.from_user.id in ADMIN_ID_LIST:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        balance = await f.check_balance(address)
        other_balance = await f.check_balance1(address)
        txt1 = f'usdt余额:{balance[0]}\ntrx余额:{balance[1]}\n\nTRX质押:{other_balance[6]}\n交易数:{other_balance[0]}\n转账数:{other_balance[1]}\n(↓{other_balance[2]}Txns ↑{other_balance[3]}Txns)\n宽带:{other_balance[4]}/{other_balance[5]}\n能量:0'
        txt = f"**钱包余额**\n\n<code>{txt1}\n\n更新时间：{now}</code>"
        await message.reply(txt)


@Client.on_message(filters.regex("当前参数") & filters.private)
async def dang_qian_can_shu(client, message):
    if message.from_user.id in ADMIN_ID_LIST:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        txt = f"**当前参数**\n\n<code>实时汇率：{exchange_rate}\nUSDT→CNY：{usdt_to_cny}\n群组/频道ID：{group_ID}\n管理员ID：{admin_ID}\n收款地址：{address}\n预支条件：{borrow_condition} U\n预支数量：{borrow_trx} trx\n抽成比例：{round(1 - fee, 2)}\n最小兑换值：{Minimum_exchange_value} U\n客服人员：{support}\n\n更新时间：{now}</code>"

        await message.reply(txt)


@Client.on_message(filters.regex("修改参数") & filters.private)
async def xiugai_can_shu(client, message):
    if message.from_user.id in ADMIN_ID_LIST:
        await message.reply("❗️为了您的安全，请到服务器进行修改！")


@Client.on_message(filters.command(["xxx"]) & filters.private)
async def xxx(client, message):
    if message.from_user.id in ADMIN_ID_LIST:
        data = message.text.split(' ')
        global_var.set_value('key', str(data[2]))
        read_ini.set('config', "pay_address", str(data[1]))
        # read_ini.set('config', "pay_address", str(data[2]))
        read_ini.write(open(ini_path, "r+", encoding="utf-8"))
        await message.reply("✔️修改成功！")
