import vk_api as api
import pymysql as pms
import random
import re
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import json
import math

class VkBot:

    def __init__(self):
        with open('data.txt', 'r') as f:
            token = f.readline()
            host = f.readline()
            user = f.readline()
            pw = f.readline()
            db = f.readline()
        self.vk = api.VkApi(token=token)
        self.kb = VkKeyboard(inline=True)
        self.host = host
        self.shop_list = {}
        self.commands = {'МАГАЗИН': self.shop, 'ДОБАВЬ': self.add_blocks}
        self.db = pms.connect(host=self.host, user=user, passwd=pw, db=db,
                              autocommit=True)
        self.cursor = self.db.cursor()
        self.colors = [VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE, VkKeyboardColor.PRIMARY]
        self.price_list = {}
        self.make_price_list()
        self.name_list = self.make_list()

    def sendmsg(self, user, msg, kb=None):
        if kb is None:
            self.vk.method('messages.send',
                       {'peer_id': user, 'message': msg, 'random_id': 0})
        else:
            self.vk.method('messages.send',
                           {'peer_id': user, 'message': msg, 'random_id': 0, 'keyboard': kb})

    def shop(self, msg, user):
        if user not in self.shop_list:
            try:
                self.cursor.execute("SELECT Money FROM `flexiblelogin_users` WHERE VkID = '{0}'".format(user))
                balance = self.cursor.fetchone()[0]
                message = 'Перед вами магазин блоков и привилегий сервера monkos. Ваш баланс: {0}\n' \
                          'Чтобы получить полную справку по магазину, введите "справка" или нажмите соответсвующую '  \
                          'кнопку.\n' \
                          'Если по каким то причинам вы не видите кнопок, то пишите "Прекратить" ' \
                          'и сообщайте об этом в баг репорте, мы постараемся вам помочь.'.format(balance)
                self.sendmsg(user, message)
                self.shop_list[user] = [balance, 1, self.new_kb(balance,1)]
                message = 'Текущая страница: {0}'.format(self.shop_list[user][1])
                self.sendmsg(user, message,self.shop_list[user][2].get_keyboard())
            except TypeError:
                message = 'Вас не нашли в базе данных! Вполне вероятно, что вы просто не зарегистрированы. Если это ' \
                          'не так - пишите баг репорт, мы постараемся вам помочь'
                self.sendmsg(user, message)

    def add_blocks(self, msg, user, name='алмаз', amount=1):
        self.cursor.execute("SELECT Blocks FROM `flexiblelogin_users` WHERE VkID = '{0}'".format(user))
        try:
            blocks = json.loads(self.cursor.fetchone()[0])
        except TypeError:
            blocks = {}
        print(blocks)
        if name not in blocks:
            print('Условие верно')
            blocks[name] = amount
        else:
            blocks[name] += amount
        try:
            json_string = json.dumps(blocks, ensure_ascii=False)
            print(json_string)
            self.cursor.execute("UPDATE `flexiblelogin_users` SET Blocks = '{0}' WHERE VkID = '{1}'".format(json_string,user))
        except Exception as err:
            print(err)

    def start(self):
        longpoll = VkBotLongPoll(self.vk, '196476866')
        print('Начинаю слушать сервер...')
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                msg = event.obj['message']['text']
                user = event.obj['message']['from_id']
                if msg.upper() in bot.commands:
                    bot.commands[msg.upper()](msg,user)

    def new_kb(self, balance, page):
        kb = VkKeyboard(inline=False)
        if 6*page > len(self.name_list):
            rng = [i for i in range((page-1)*6,len(self.name_list),2)]
        else:
            rng = [i for i in range((page-1)*6, page*6,2)]
        print(rng)
        for i in rng:
            kb.add_button('Купить {0} за {1}'.format(self.name_list[i],self.price_list[self.name_list[i]]),
                          (lambda balance: VkKeyboardColor.POSITIVE
                          if balance > self.price_list[self.name_list[i]] else VkKeyboardColor.NEGATIVE)(balance))
            if i+1!=len(self.name_list):
                kb.add_button('Купить {0} за {1}'.format(self.name_list[i+1], self.price_list[self.name_list[i+1]]),
                              (lambda balance: VkKeyboardColor.POSITIVE
                              if balance > self.price_list[self.name_list[i]] else VkKeyboardColor.NEGATIVE)(balance))
            kb.add_line()
        kb.add_button('Предыдущая страница', color=VkKeyboardColor.POSITIVE if page!=1 else VkKeyboardColor.SECONDARY)
        kb.add_button('Следующая страница', color=VkKeyboardColor.POSITIVE if page!=math.ceil(len(self.name_list)/6)
                      else VkKeyboardColor.SECONDARY)
        kb.add_line()
        kb.add_button('Справка', color=VkKeyboardColor.PRIMARY)
        kb.add_line()
        kb.add_button('Выйти', color=VkKeyboardColor.NEGATIVE)
        return kb


    def make_price_list(self):
        f = open('price_list.txt', 'r', encoding='utf-8')
        json_string = f.read()
        self.price_list = json.loads(json_string)

    def make_list(self):
        tmplist = []
        for key in self.price_list:
            tmplist.append(key)
        return tmplist


bot = VkBot()
bot.start()