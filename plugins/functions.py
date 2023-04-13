

import asyncio
import configparser
import datetime
import random
import string
import time
import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(str(BASE_DIR))

import aiohttp
import requests
from tronpy import AsyncTron
from tronpy.keys import PrivateKey
import data.data as d
from pyrogram import Client
from tronpy.providers import AsyncHTTPProvider

d = d.Database()

try:
    ini_path = ".\\config.ini"
    read_ini = configparser.ConfigParser()
    read_ini.read(ini_path, 'UTF-8')

    api = read_ini['config']['api_key']

except:
    pro_path = os.path.split(os.path.realpath(__file__))[0]
    pro_path = str(pro_path).replace("/plugins","")
    ini_path = f"{pro_path}/config.ini"
    read_ini = configparser.ConfigParser()
    read_ini.read(ini_path, 'UTF-8')
    api = read_ini['config']['api_key']

# async def transfer(pay_address, pay_address_private_key, accept_address, quantity):
#     async with AsyncTron(network='nile') as client:
#         txb = (
#             client.trx.transfer(pay_address, accept_address, int(quantity * 1000000))
#             # .memo("test memo")
#             .fee_limit(50000000)
#         )
#         txn = await txb.build()
#         txn_ret = await txn.sign(PrivateKey(bytes.fromhex(pay_address_private_key))).broadcast()
#         result = await txn_ret.wait()
#         try:
#             broadband = int(result['receipt']['net_usage'])
#             burn_trx = 0
#         except KeyError:
#             broadband = int(result['fee'] / 1000)
#             burn_trx = result['fee'] / 1000000
#         print(
#             f"交易哈希：{result['id']}\n区块高度：{result['blockNumber']}\n交易时间：{int(result['blockTimeStamp'] / 1000)}\n兑换地址：{accept_address}\n转账地址：{pay_address}\n转账数量：{quantity}\n消耗宽带：{broadband}\n燃烧TRX：{burn_trx}")
#         return result['id'], result['blockNumber'], int(
#             result['blockTimeStamp'] / 1000), accept_address, pay_address, quantity, broadband, burn_trx


async def transfer(pay_address, pay_address_private_key, accept_address, quantity):
    # api_key == "7cc73caa-c176-409e-8e44-ba16bf06c400"
    async with AsyncTron(
            AsyncHTTPProvider(api_key=api, timeout=5)) as client:
        txb = (
            client.trx.transfer(pay_address, accept_address, int(quantity * 1000000))
            # .memo("test memo")
            .fee_limit(50000000)
        )
        txn = await txb.build()
        txn_ret = await txn.sign(PrivateKey(bytes.fromhex(pay_address_private_key))).broadcast()
        result = await txn_ret.wait()
        try:
            broadband = int(result['receipt']['net_usage'])
            burn_trx = 0
        except KeyError:
            broadband = int(result['fee'] / 1000)
            burn_trx = result['fee'] / 1000000
        print(
            f"交易哈希：{result['id']}\n区块高度：{result['blockNumber']}\n交易时间：{int(result['blockTimeStamp'] / 1000)}\n兑换地址：{accept_address}\n转账地址：{pay_address}\n转账数量：{quantity}\n消耗宽带：{broadband}\n燃烧TRX：{burn_trx}")
        return result['id'], result['blockNumber'], int(
            result['blockTimeStamp'] / 1000), accept_address, pay_address, quantity, broadband, burn_trx


# 判断一个账户是否存在
async def is_usdt(address):
    try:
        url = f"https://apilist.tronscanapi.com/api/accountv2?address={address}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if data:
                    try:
                        if data['message'] == 'some parameters are invalid or out of range':
                            return False
                        else:
                            return True
                    except:
                        return True
                else:
                    return False
    except:
        return False

    # print(data)


async def get_token_balance(balance, token_name):
    for token in balance:
        if token['tokenName'] == token_name:
            return str(float(token['balance']) / 1000000)
    return None


async def check_balance(address):
    url = f"https://apilist.tronscanapi.com/api/account/tokens?address={address}"
    print(url)
    # print(f'这里接受到的数据为{address}')
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            balance = data["data"]
            usdt_balance = await get_token_balance(balance, "Tether USD")
            trx_balance = await get_token_balance(balance, "trx")
            if usdt_balance is None:
                usdt_balance = 0
            await session.close()
            return ['{:.2f}'.format(float(usdt_balance)), '{:.2f}'.format(float(trx_balance))]


async def check_balance1(address):
    url = f"https://apilist.tronscanapi.com/api/accountv2?address={address}"
    # print(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            jiaoyishu = data["totalTransactionCount"]
            zhuanzhangshu = data["transactions"]
            zhuanru = data["transactions_in"]
            zhuanchu = data["transactions_out"]
            kuandai = data['bandwidth']['freeNetRemaining']
            zuidakuandai = data['bandwidth']['freeNetLimit']

            trxzhiya = data["allowExchange"]
            if not trxzhiya:
                trxzhiya = 0

            # print(balance[5]['nrOfTokenHolders'])
            # usdt_balance = await get_token_balance(balance, "Tether USD")
            # trx_balance = await get_token_balance(balance, "trx")
            # if usdt_balance is None:
            #     usdt_balance = 0
            # print(交易数)
            await session.close()
            # print(jiaoyishu, zhuanzhangshu, zhuanru, zhuanchu, kuandai, zuidakuandai, trxzhiya)
            return jiaoyishu, zhuanzhangshu, zhuanru, zhuanchu, kuandai, zuidakuandai, trxzhiya
            
            
def get_current_timestamp():
    # 返回当前时间戳
    return int(time.time())*1000

def one_hour_ago():
    current_time = datetime.datetime.now()
    one_hour_ago = current_time - datetime.timedelta(hours=1)
    one_hour_ago_timestamp = int(str(int(time.mktime(one_hour_ago.timetuple()))) + '000')

    today_end = datetime.datetime(current_time.year, current_time.month, current_time.day, 23, 59, 59)
    today_end_timestamp = int(str(int(time.mktime(today_end.timetuple()))) + '999')

    return one_hour_ago_timestamp


async def monitor_usdt_balance(address):
    pay_address = "https://t.me/jiqingya"
    pay_address_private_key = "https://t.me/jiqingya"

    Program_start_time = one_hour_ago()  # 程序开始时间
    Minimum_exchange_value = 1
    Exchange_Rates = 12
    url = f'https://nileapi.tronscan.org/api/new/token_trc20/transfers?limit=20&toAddress={address}&start=0&sort=-timestamp&count=true&filterTokenValue=1&relatedAddress={address}&start_timestamp={str(Program_start_time)}'
    # url = f'https://apilist.tronscanapi.com/api/new/token_trc20/transfers?limit=20&toAddress={address}&start=0&sort=-timestamp&count=true&filterTokenValue=1&relatedAddress={address}'
    print(url)
    async with aiohttp.ClientSession() as session:
        timeout = aiohttp.ClientTimeout(total=30)
        async with session.get(url, timeout=timeout) as response:
            datas = await response.json()
            for data in datas['token_transfers']:
                # if data['contract_address'] == 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t':  # 合约地址是否正确
                if data['contract_address'] == 'TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf':  # 测试网
                    if data['finalResult'] == 'SUCCESS':  # 转账结果是否成功
                        transfer_amount = float(data['quant']) / 1000000  # 转账的金额
                        transfer_hash = data['transaction_id']  # 转账哈希
                        from_address = data['from_address']  # 谁转进来的usdt
                        # print(transfer_amount, transfer_hash, from_address)
                        transfer_trx = round(transfer_amount * Exchange_Rates, 2)  # 需要转账的trx
                        if transfer_amount >= Minimum_exchange_value:  # 收到的金额大于等于最小设置值
                            record = await d.select_one_record_condition('transfer', 'u_hash=?', (transfer_hash,))
                            if not record:  # 如果数据库中没有这条记录
                                s = await transfer(pay_address, pay_address_private_key, from_address, transfer_trx)
                                current_timestamp = int(time.time())

                                await d.insert_record('transfer', (
                                    s[2], transfer_hash, s[0], s[1], s[3], s[4], s[5], transfer_amount, s[6], s[7], 0,
                                    current_timestamp))
                                # 兑换成功消息发送到群里面
                                g_txt = f'兑换成功\n兑换金额：{transfer_amount}\n兑换trx：{transfer_trx}\n兑换地址：{from_address}\n兑换哈希：{transfer_hash}'
                                # 推送群组消息
                                # from main import app
                                # await Client.start()
                                await Client.send_message(chat_id=-1001686890836, text=g_txt)

                                # print(s)


# 获取trx的兑换价格
# async def get_trx():
#     url = f"https://api.justswap.io/v2/allpairs?&page_size=1&page_num=0"
#     # print(url)
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#             data = await response.json()
#             # print(data)
#             price = round(float(data['data']['0_TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t']['price']), 4)
#             return price
def get_trx():
    url = f"https://api.justswap.io/v2/allpairs?&page_size=1&page_num=0"
    # print(url)
    r = requests.get(url)
    data = r.json()
    # print(data)
    price = round(float(data['data']['0_TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t']['price']), 4)
    return price


def current_timestamp():
    # 获取当前时间戳（单位：秒）
    timestamp = time.time()

    # 将时间戳转换为以毫秒为单位的形式
    timestamp_ms = int(timestamp * 1000)

    return timestamp_ms


# 获取usdt的价格
# async def get_usdt_to_cny():
#     url = f"https://www.okx.com/v2/market/rate/getRateByRateName/usd_cny?t={current_timestamp()}"
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#             r = await response.json()
#             data = r['data']
#             t = 0
#             for i in data:
#                 t = t + float(i['rateParities'])
#             return round(t / len(data), 4)

def get_usdt_to_cny():
    url = f"https://www.okx.com/v2/market/rate/getRateByRateName/usd_cny?t={current_timestamp()}"
    r = requests.get(url)
    data = r.json()
    t = 0
    for i in data['data']:
        t = t + float(i['rateParities'])
    return round(t / len(data['data']), 4)


# 获取trx的价格
def get_trx_to_cny(u, t):
    return round(u / t, 2)


async def main():
    # s = await get_trx()
    u = 6.9328  # 1usdt的价格
    t = 14.9172  # 1U等于的trx数量

    z = get_trx_to_cny(u, t)

    s = get_trx() * 0.85

    print(z)
    print(s)


# 生成随机字符串 8 位数 小写字母
def random_str():
    return ''.join(random.sample(string.ascii_lowercase + string.digits, 8))



def get_today_start_end_timestamp():
    # 获取当前日期和时间
    now = datetime.datetime.now()

    # 获取今天的0点和24点时间戳
    today_start = int(datetime.datetime(now.year, now.month, now.day, 0, 0, 0).timestamp())
    today_end = int(datetime.datetime(now.year, now.month, now.day, 23, 59, 59).timestamp())

    # 返回时间戳元组
    return today_start, today_end
if __name__ == '__main__':
    # pro_path = os.path.split(os.path.realpath(__file__))[0]
    # pro_path = str(pro_path).replace("/plugins","")
    print(api)
    
