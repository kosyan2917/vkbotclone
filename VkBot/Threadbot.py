import vk_api as api
import pymysql as pms
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import uuid
import bcrypt
import string
import smtplib
import random
from email.mime.text import MIMEText
from email.header import Header
import json
import math
import logging as lg
import threading as thr
import time
import requests as rq

class Vote():

    def __init__(self):
        self.bot = VkBot()
        self.host = '***REMOVED***'
        self.db = pms.connect(host=self.host, user='***REMOVED***', passwd='***REMOVED***', db='***REMOVED***',
                              autocommit=True)
        self.cursor = self.db.cursor()
        self.cursor.execute("SELECT vkid FROM vote_db JOIN flexiblelogin_users ON "
                            "vote_db.username = flexiblelogin_users.Username")
        self.votes = self.cursor.fetchall()

    def get_votes(self):
        result = []
        self.cursor.execute("SELECT vkid FROM vote_db JOIN flexiblelogin_users ON "
                                        "vote_db.username = flexiblelogin_users.Username")
        votes = self.cursor.fetchall()
        print(votes, ' self ', self.votes)
        if len(votes) > len(self.votes):
            for i in range(len(self.votes), len(votes)):
                self.bot.write_msg(votes[i][0], 'Спасибо за ваш голос! Ваш баланс увеличен на 50.')
        self.votes = votes




class Donate():

    def __init__(self):
        pass

    def get_donates(self):
        request = 'https://api.vkdonate.ru?action=donates&count={0}&key=e21f784712a344c78dcb'.format(10)
        response = rq.get(request).text
        donaters = json.loads(response)['donates']
        print(donaters)
        return donaters


class NullNamespace:
    bytes = b''


class VkBot:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(VkBot, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.host = '***REMOVED***'
        self.token = '***REMOVED***'
        self.db = pms.connect(host=self.host, user='***REMOVED***', passwd='***REMOVED***', db='***REMOVED***',
                              autocommit=True)
        self.vk = api.VkApi(token=self.token)
        self.chat = 2000000001
        self.commands = {'ЗАРЕГИСТРИРОВАТЬСЯ': self.register0, 'НАЧАТЬ': self.help, 'ХЕЛП':self.help,'START':self.help,
                         'ПРЕКРАТИТЬ': self.unreg, 'ВОССТАНОВИТЬ ПАРОЛЬ':self.forgot_pw1, 'ОБЩАТЬСЯ С:': self.dialog,
                         'РЕПОРТ':self.report, 'КРИНЖ':self.turn_mode, 'ХАЙП':self.turn_mode, 'ВЫЙТИ':self.unreg,
                         'МАГАЗИН': self.shop}
        self.shop_commands = {'СЛЕДУЮЩАЯ СТРАНИЦА':self.n_page, 'ПРЕДЫДУЩАЯ СТРАНИЦА': self.p_page, 'СПРАВКА':self.shop_help}
        self.keyboard = VkKeyboard(one_time=False)
        self.regkb = VkKeyboard(one_time=False)
        self.adminkb = VkKeyboard(one_time=False)
        self.reports = VkKeyboard(inline=True)
        self.dialog_kb = VkKeyboard(inline=True)
        self.agree_kb = VkKeyboard(inline=True)
        self.agree_kb.add_button('Согласен', color=VkKeyboardColor.POSITIVE)
        self.agree_kb.add_button('Прекратить', color=VkKeyboardColor.NEGATIVE)
        self.dialog_kb.add_button('Пока не работает')
        self.report_list = ['Проблемы с установкой', 'Проблемы с регистрацией', 'Другое']
        self.reports.add_button(self.report_list[0])
        for typ in self.report_list[1:]:
            self.reports.add_line()
            self.reports.add_button(typ)
        self.keyboard.add_button('Зарегистрироваться', color=VkKeyboardColor.POSITIVE)
        self.keyboard.add_button('Хелп', color=VkKeyboardColor.POSITIVE)
        self.keyboard.add_line()
        self.keyboard.add_button('Восстановить пароль', color=VkKeyboardColor.POSITIVE)
        self.keyboard.add_line()
        self.keyboard.add_button('Магазин', color=VkKeyboardColor.POSITIVE)
        self.keyboard.add_line()
        self.keyboard.add_button('Репорт', color=VkKeyboardColor.NEGATIVE)
        self.adminkb.add_button('Зарегистрироваться', color=VkKeyboardColor.POSITIVE)
        self.adminkb.add_button('Хелп', color=VkKeyboardColor.POSITIVE)
        self.adminkb.add_line()
        self.adminkb.add_button('Восстановить пароль', color=VkKeyboardColor.POSITIVE)
        self.regkb.add_button('Прекратить')
        self.adminkb.add_button('Прекратить')
        self.adminkb.add_line()
        self.adminkb.add_button('Общаться с:', color=VkKeyboardColor.NEGATIVE)
        self.report_user = {}
        self.reg = {}
        self.restore = {}
        self.dialogs = []
        self.flag = False
        self.cursor = self.db.cursor()
        self.alphabet = string.ascii_letters + string.digits
        self.pw_alphabet = self.alphabet + '@-_%*()&#~'
        self.admins = [173938201]
        self.cringe_mode = False
        self.hype = []
        self.shop_list = {}
        self.price_list = {}
        self.make_price_list()
        self.name_list = self.make_list()
        lg.basicConfig(filename='shop.log', level=lg.INFO)

    def shop(self, msg, user, item=None):
        if user not in self.shop_list:
            try:
                self.cursor.execute("SELECT Money FROM `flexiblelogin_users` WHERE VkID = '{0}'".format(user))
                balance = self.cursor.fetchone()[0]
                message = 'Перед вами магазин блоков и привилегий сервера monkos. Ваш баланс: {0}\n' \
                          'Чтобы получить полную справку по магазину, введите "справка" или нажмите соответсвующую '  \
                          'кнопку.\n' \
                          'Если по каким то причинам вы не видите кнопок, то пишите "Прекратить" ' \
                          'и сообщайте об этом в баг репорте, мы постараемся вам помочь.'.format(balance)
                self.write_msg(user, message)
                self.shop_list[user] = [balance, 1, self.new_kb(balance, 1), 0, None]
                try:
                    message = 'Текущая страница: {0} из {1}. Ваш баланс: {2}'.format(self.shop_list[user][1],
                                                                                     math.ceil(len(self.name_list) / 6),
                                                                                     self.shop_list[user][0])
                    self.write_msg(user, message, self.shop_list[user][2])
                except KeyError as err:
                    print(err)
            except TypeError as err:
                print(err)
                message = 'Вас не нашли в базе данных! Вполне вероятно, что вы просто не зарегистрированы. Если это ' \
                          'не так - пишите баг репорт, мы постараемся вам помочь'
                self.write_msg(user, message)
        elif self.shop_list[user][3] == 1:
            self.buy(msg, user)
        elif self.shop_list[user][3] == 2:
            if msg.isdigit():
                if self.shop_list[user][0] >= int(msg)*self.price_list[item]:
                    self.shop_list[user][3] = 0
                    self.add_blocks(msg, user, item, int(msg))
                    message = "Вы успешно приобрели предмет"
                    lg.info("Игроком {0} было куплено {1} {2}".format(user, int(msg), item))
                    self.write_msg(user, message)
                    self.cursor.execute("UPDATE `flexiblelogin_users` SET Money='{0}' WHERE VkID = '{1}'"
                                        .format(self.shop_list[user][0]-int(msg)*self.price_list[item], user))
                    self.unreg(msg, user)
                else:
                    self.write_msg(user, 'Предмет не куплен, у вас недостаточно средств!')
                    self.unreg(msg, user)
            else:
                self.write_msg(user, 'Это не похоже на число. Попробуйте еще раз', self.regkb)
        else:
            try:
                message = 'Текущая страница: {0} из {1}'.format(self.shop_list[user][1], math.ceil(len(self.name_list)/6))
                self.write_msg(user, message, self.shop_list[user][2])
            except KeyError as err:
                print(err)

    def add_blocks(self, msg, user, name, amount):
        self.cursor.execute("SELECT Blocks FROM `flexiblelogin_users` WHERE VkID = '{0}'".format(user))
        try:
            blocks = json.loads(self.cursor.fetchone()[0])
        except TypeError:
            blocks = {}
        if name.lower() not in blocks:
            blocks[name.lower()] = amount
        else:
            blocks[name.lower()] += amount
        try:
            json_string = json.dumps(blocks, ensure_ascii=False)
            self.cursor.execute("UPDATE `flexiblelogin_users` SET Blocks = '{0}' WHERE VkID = '{1}'".format(json_string,user))
        except Exception as err:
            print(err)

    def new_kb(self, balance, page):
        kb = VkKeyboard(inline=False)
        print('Длина массива' + str(len(self.name_list)))
        print('Номер страницы' + str(page))
        if 6*page > len(self.name_list):
            rng = [i for i in range((page-1)*6, len(self.name_list), 2)]
        else:
            rng = [i for i in range((page-1)*6, page*6, 2)]
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
        kb.add_button('Предыдущая страница', color=VkKeyboardColor.POSITIVE if page!=1 else VkKeyboardColor.PRIMARY)
        kb.add_button('Следующая страница', color=VkKeyboardColor.POSITIVE if page!=math.ceil(len(self.name_list)/6)
                      else VkKeyboardColor.PRIMARY)
        kb.add_line()
        kb.add_button('Справка', color=VkKeyboardColor.PRIMARY)
        kb.add_line()
        kb.add_button('Выйти', color=VkKeyboardColor.NEGATIVE)
        return kb

    def make_price_list(self):
        f = open('price_list.txt', 'r', encoding='utf-8')
        json_string = f.read()
        json_string = json_string.lower()
        self.price_list = json.loads(json_string)

    def make_list(self):
        tmplist = []
        for key in self.price_list:
            tmplist.append(key)
        return tmplist

    def turn_mode(self, msg, user):
        if user in self.hype:
            self.hype.pop(self.hype.index(user))
            message = 'Вы вышли из кринж мода'
            self.write_msg(user, message)
        else:
            message = 'Хайп течет в ваших венах!'
            self.write_msg(user, message)
            self.hype.append(user)

    def dialog(self, msg, user):
        if user not in self.admins:
            message = 'У вас нет доступа к этой команде'
            self.write_msg(user,message)
        else:
            if not self.flag:
                self.flag = True
            else:
                message = 'Сейчас от лица сообщества будут писать администраторы, а не бот, поэтому весь функционал бота ' \
                          'будет отключен. Чтобы вернуть его, напишите "Прекратить" или нажмите соответвующую кнопку.'
                try:
                    self.write_msg(int(msg),message,self.regkb)
                except:
                    print('Неа')
                self.dialogs.append(int(msg))
                self.flag = False

    def dialog_chat(self, msg):
        message = 'Сейчас от лица сообщества будут писать администраторы, а не бот, поэтому весь функционал бота ' \
                  'будет отключен. Чтобы вернуть его, напишите "Прекратить" или нажмите соответвующую кнопку.'
        try:
            self.write_msg(int(msg[42:]), message, self.regkb)
        except:
            print('Неа')
        self.dialogs.append(int(msg[42:]))

    def confirmation(self,email,code, mode=0): #0 - Регистрация, 1 - Восстановление пароля
        self.server = smtplib.SMTP(self.host)
        self.server.login('noreply@monkos.ru', 'KEs71b!I')
        FROM = 'noreply@monkos.ru'
        if mode == 0:
            subject = 'Подтверждение email адреса'
            text = 'Здравствуйте, вы решили зарегистрироваться на проекте monkos. Чтобы подтвердить свой email, введите этот' \
                   ' код в сообщения боту:\n\n {0} \n\nЕсли вы нигде не регистрировались, просто проигнорирйте это сообщение\n' \
                   'Это автоматическое сообщение. На него не нужно отвечать'.format(code)
        elif mode == 1:
            subject = 'Восстановление пароля'
            text = 'Здравствуйте, пользователь, вы сделали запрос на восстановление пароля на проекте monkos. ' \
                   'Чтобы продолжить процедуру, введите этот код в сообщения боту:\n\n {0} \n\nЕсли вы ничего не делали,' \
                   ' просто проигнорирйте это сообщение\n' \
                   'Это автоматическое сообщение. На него не нужно отвечать'.format(code)
        message = MIMEText(text,'plain','utf-8')
        message['Subject'] = Header(subject,'utf-8')
        message['From'] = FROM
        message['To'] = email
        self.server.sendmail(FROM, [email], message.as_string())
        self.server.quit()

    def report(self, msg, user, mode=0):
        if mode == 0:
            self.report_user[user] = [1]
            message = 'Выберите тип проблемы'
            self.write_msg(user, message, self.reports)
        elif mode == 1:
            self.report_user[user].append(msg)
            message = 'Опишите проблему как можно подробнее'
            self.write_msg(user, message, self.regkb)
            self.report_user[user][0] = 2
        elif mode == 2:
            self.dialog_kb = VkKeyboard(inline=True)
            self.dialog_kb.add_button('Общаться с {0}'.format(user))
            message = 'Пользователь https://vk.com/id{0} отправил репорт\n' \
                      'Тип репорта: {1}\n' \
                      'Текст репорта: {2}'.format(user,self.report_user[user][1],msg)
            try:
                self.write_msg(self.chat, message, self.dialog_kb)
                message = 'Ваше сообщние успешно доставлено'
                self.write_msg(user, message)
            except Exception as err:
                print(err)
                message = 'Что то пошло не так. Ваше сообщение не было доставлено'
                self.write_msg(user, message)
            self.unreg(msg, user)

    def unreg(self, msg, user):
        if user in self.reg:
            self.reg.pop(user)
            message = 'Процесс регистрации окончен'
            self.write_msg(user,message)
        elif user in self.restore:
            self.restore.pop(user)
            message = 'Процесс восстановления пароля закончен'
            self.write_msg(user, message)
        elif user in self.dialogs:
            self.dialogs.pop(self.dialogs.index(user))
            message = 'Функционал бота восстановлен'
            self.write_msg(user, message)
        elif user in self.report_user:
            self.report_user.pop(user)
            message = 'Успешно'
            self.write_msg(user, message)
        elif user in self.shop_list:
            self.shop_list.pop(user)
            message = "Вы вышли из магазина"
            self.write_msg(user, message)
        else:
            message = 'Вы ничего не делаете в данный момент!'
            self.write_msg(user,message)

    def help(self, msg, user):
        text = 'Бот умеет следующее: \n Зарегистрироваться - регистрация нового пользователя' \
               ' \n Хелп - выводит список команд \n Восстановить пароль - восстановление пароля' \
               '\n Репорт - отпавить сообщение об ошибке администраторам. Они свяжутся с вами в ближайшее время, чтобы решить ваш вопрос' \
               '\n Магазин - мазазин внутриигровых предметов и привилегий'
        self.write_msg(user, text)

    def write_msg(self, user_id, message, kb=None):
        cringe = '!!!!!!!!!!!!!!!!!!!!! хайп 😂😂🤣😂😂😂😂😂😂😂😂😂😂😂😂😂😂😂😂😂😂😂😂😂😂😂 ХАЙП ХАЙП КРИНЖ !!!!!!!!!!!!!!!!!! ❤❤❤❤❤❤❤🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣🤣 \n Спасибо бро йоу 🤙🏻🤙🏻🤙🏻🤙🏻🤙🏻🤙🏻'
        if kb is None:
            if user_id in self.admins:
                kb = self.adminkb
            else:
                kb = self.keyboard
        self.vk.method('messages.send', {'peer_id': user_id, 'message': message, 'random_id': 0, 'keyboard': kb.get_keyboard()})
        if user_id in self.hype:
            message = message + cringe

    def forgot_pw1(self, msg, user):
        message = 'Введите почту, которую вы указали при регистрации'
        self.write_msg(user, message, self.regkb)
        self.restore[user] = [self.forgot_pw2]

    def forgot_pw2(self, msg, user):
        if self.check_mail(msg):
            message = 'На вашу почту отправлен шестизначный код. Введите его, чтобы продолжить'
            self.write_msg(user, message, self.regkb)
            code = self.gen_code()
            self.confirmation(msg,code,1)
            self.restore[user] = [self.forgot_pw3, code]
        else:
            message = 'Пользователь с таким адресом не зарегистрирован'
            self.write_msg(user, message, self.regkb)

    def forgot_pw3(self, msg, user):
        if msg.upper() == self.restore[user][1]:
            message = 'Введите новый пароль. Максимальная длина пароля' \
                              ' - 64 символа, минимальная - 6.\n Резрешенные символы - a-zA-Z1-9, а также ' \
                               'спецсимволы @, -, _, %, *, ), (, &, #, ~'
            self.write_msg(user, message, self.regkb)
            self.restore[user] = [self.forgot_pw4]

    def forgot_pw4(self, msg, user):
        if (len(msg)>5) and (len(msg)<64):
            for sym in msg:
                if sym not in self.pw_alphabet:
                    message = 'Вы использовали запрещенный символ --> {0} <--. Попробуйте другой пароль'.format(sym)
                    self.write_msg(user, message, self.regkb)
                    return 0
            else:
                pw = self.hash_pw(msg)
                try:
                    self.cursor.execute("UPDATE `flexiblelogin_users` SET `Password` = '{0}' WHERE `flexiblelogin_users`.`VkID` = {1}".format(pw, user))
                except Exception as err:
                    message = 'Вероятно, что то пошло не так. Попробуйте еще раз или напишите репорт'
                    self.write_msg(user, message)
                    print(err)
                self.unreg(msg,user)
        else:
            message = 'Кажется ваш пароль слишком короткий или слишком длинный. Попробуйте еще раз'
            self.write_msg(user, message, self.regkb)

    def register0(self, msg, user):
        self.cursor.execute("SELECT * FROM `flexiblelogin_users`")
        table = self.cursor.fetchall()
        self.reg[user] = [self.register1]
        for player in table:
            if player[8] == user:
                if user != 0:
                    message = 'К этому аккануту вк уже привязана учетная запись на нашем проекте!'
                    self.write_msg(user, message)
                    self.unreg(msg, user)
                    return 0
        else:
            message = 'Прежде чем приступить к регистрации, необходимо ознакомиться с правилами проекта и подтвердить свое согласие с ними.\n Для этого напишите "согласен" или нажмите на соответсвующую кнопку \n {0}'.format('https://vk.com/topic-196476866_47077902')
            self.write_msg(user, message, self.agree_kb)

    def register1(self, msg, user):
        if msg.upper() == 'СОГЛАСЕН':
            message = 'Введите адрес электронной почты'
            self.write_msg(user,message,self.regkb)
            self.reg[user] = [self.register2]
        else:
            message = 'К сожалению, регистрацию невозможно продолжить, не согласившись с правилами проекта'
            self.write_msg(user, message, self.regkb)

    def register2(self, msg, user): # Кто не добавит проверку на аттачменты, тот безрукий дурачок! Здесь почта
        if (msg.find('@') == -1) or (msg.find(' ') != -1) or (len(msg) >= 64):
            message = 'Почта введена неверно'
            self.write_msg(user, message,self.regkb)
        else:
            if self.check_mail(msg):
                message = 'Пользователь с таким адресом уже зарегистрирован'
                self.write_msg(user, message, self.regkb)
            else:
                self.reg[user].append(msg)
                self.reg[user].append(self.gen_code())
                message = 'На почту {0} отправлен шестизначный код. Введите его'.format(msg)
                self.confirmation(msg, self.reg[user][2])
                self.reg[user][0] = self.register3
                self.write_msg(user,message, self.regkb)

    def register3(self, msg, user):
        if msg.upper() == self.reg[user][2]:
            message = 'Отлично! Почта {0} может быть использована. Теперь введите ник. \n Минимальная длина никнейма' \
                      ' 2,максимальная - 16. Допустимые символы - все буквы латинского алфавита, все арабские цифры'.format(self.reg[user][1])
            self.write_msg(user, message, self.regkb)
            self.reg[user][0] = self.register4
        else:
            message = 'Код не совпадает. Повоторите попытку'
            self.write_msg(user, message, self.regkb)

    def register4(self, msg, user): #Здесь ник
        if (len(msg)==0):
            message = 'Задан пустой ник!'
            self.write_msg(user, message, self.regkb)
        else:
            for sym in msg:
                if sym not in self.alphabet:
                    message = 'Вы ввели запрещенный символ --> {0} <--.Попробуйте другой никнейм'.format(sym)
                    self.write_msg(user, message, self.regkb)
                    break
            else:
                self.cursor.execute("SELECT * FROM `flexiblelogin_users`")
                table = self.cursor.fetchall()
                print(table)
                for us in table:
                    print(us)
                    if msg == us[2]:
                        message = 'Пользователь с таким ником уже существует. Попробуйте другой'
                        self.write_msg(user, message, self.regkb)
                        return 0
                else:
                    ud = str(uuid.uuid3(NullNamespace, 'OfflinePlayer:' + msg))
                    print('Ник:' + msg)
                    ud = ud.replace('-', '')
                    print('UUID:'+ ud)
                    self.reg[user][2] = ud
                    self.reg[user].append(msg)
                    self.reg[user][0] = self.register4
                    message = 'Отлично, ник {0} может быть использован. \n Введите пароль. Максимальная длина пароля' \
                              ' - 64 символа, минимальная - 6.\n Резрешенные символы - a-zA-Z1-9, а также ' \
                               'спецсимволы @, -, _, %, *, ), (, &, #, ~'.format(msg)
                    self.write_msg(user, message, self.regkb)
                    self.reg[user][0] = self.register5

    def register5(self, msg, user): #Здесь пароль
        if (len(msg)>5) and (len(msg)<64):
            for sym in msg:
                if sym not in self.pw_alphabet:
                    message = 'Вы использовали запрещенный символ --> {0} <--. Попробуйте другой пароль'.format(sym)
                    self.write_msg(user, message, self.regkb)
                    return 0
            else:
                self.write_msg(user, 'Вы успешно зарегистрировались!\n Чтобы скачать лаунчер, перейдите по ссылке \n http://monkos.ru/files/launcher/Installer.exe')
                self.reg[user].append(self.hash_pw(msg))
                self.add_to_db(user)
                self.unreg(msg,user)
        else:
            message = 'Кажется ваш пароль слишком короткий или слишком длинный. Попробуйте еще раз'
            self.write_msg(user, message, self.regkb)

    def add_to_db(self, user):
        request = "INSERT INTO `flexiblelogin_users` (UUID,Username,Password,Email, VkID) VALUES (0x{0},'{1}','{2}','{3}',{4})".format(self.reg[user][2],self.reg[user][3],self.reg[user][4],self.reg[user][1],user)
        try:
            self.cursor.execute(request)
        except pms.err.IntegrityError:
            message = 'Упс. Кажется кто-то во время регистрации занял ваш никнейм или адрес. Пройдите регистрацию заново.'
            self.write_msg(user,message)

    def check_mail(self, msg):
        self.cursor.execute("SELECT * FROM `flexiblelogin_users`")
        table = self.cursor.fetchall()
        for us in table:
            if msg == us[6]:
                return True
        else:
            return False

    def n_page(self, msg, user):
        page = self.shop_list[user][1]
        if page == math.ceil(len(self.name_list) / 6):
            message = "Дальше страниц нет."
            self.write_msg(user, message)
        else:
            self.shop_list[user][1] += 1
        self.shop_list[user][2] = self.new_kb(self.shop_list[user][0], self.shop_list[user][1])
        self.shop(msg, user)

    def p_page(self, msg, user):
        page = self.shop_list[user][1]
        if page == 1:
            message = "Дальше страниц нет."
            self.write_msg(user, message)
        else:
            self.shop_list[user][1] -= 1
        self.shop_list[user][2] = self.new_kb(self.shop_list[user][0], self.shop_list[user][1])
        self.shop(msg, user)

    def buy(self, msg, user):
        separator = msg.find(' за')
        item = msg[7:separator].lower()
        balance = self.shop_list[user][0]
        if item in self.name_list:
            if balance >= self.price_list[item]:
                message = "Вы собираетесь купить {0} по цене {1} за штуку.\n" \
                          "Введите желаемое количество. Доступно: {2}".format(item, self.price_list[item], math.floor(balance/self.price_list[item]))
                self.shop_list[user][3] = 2
                self.shop_list[user][4] = item
                self.write_msg(user, message, self.regkb)
            else:
                self.shop_list[user][3] = 0
                message = "У вас не хватает средств на покупку хотя бы одного этого предмета"
                self.write_msg(user, message, self.shop_list[user][2])
        else:
            self.shop_list[user][3] = 0
            message = "Вы собрались купить что-то странное. Мы такого не продаем"
            self.write_msg(user, message, self.shop_list[user][2])

    def shop_help(self, msg, user):
        message = 'Используйте кнопки переключения страниц для навигации между страницами' \
                  'Нажмите на выйти, чтобы выйти из магазина.' \
                  'Вы можете купить предмет без кнопок написав сообщение в виде: \n Купить <имя_предмета> за'
        self.write_msg(user, message)

    def give_money(self, user, money):
        self.cursor.execute("SELECT Money FROM `flexiblelogin_users` WHERE VkID = '{0}'".format(user))
        balance = self.cursor.fetchone()[0]
        money_req = "UPDATE `flexiblelogin_users` SET `Money` = '{0}'" \
                    " WHERE `flexiblelogin_users`.`VkID` = {1}".format(balance+money, user)
        self.cursor.execute(money_req)
        self.write_msg(user, 'Спасибо за вашу поддержку!\n На ваш баланс начислено {0} фишек \n Ваш текуший баланс: {1}'.format(money,balance+money))


    @staticmethod
    def gen_code():
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

    @staticmethod
    def hash_pw(msg):
        pw = msg.encode('utf-8')
        hashed = bcrypt.hashpw(pw, bcrypt.gensalt(10))
        hashed = hashed.decode()
        hashed = hashed.replace('b', 'y', 1)
        return hashed

def longpoll_thread():
    while True:
        try:
            bot = VkBot()
            longpoll = VkBotLongPoll(bot.vk, '196476866')
            print("Бот приступил к работе")
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    if event.from_user:
                        msg = event.obj['message']['text']
                        user = event.obj['message']['from_id']
                        if user not in bot.dialogs:
                            if msg.upper() in bot.commands:
                                if (user not in bot.reg) and (user not in bot.restore) and (user not in bot.report_user) and (user not in bot.shop_list):
                                    bot.commands[msg.upper()](msg,user)
                                else:
                                    if msg.upper() == 'ПРЕКРАТИТЬ' or msg.upper() == 'ВЫЙТИ':
                                        bot.unreg(msg, user)
                                    else:
                                        message = 'В данный момент команды отключены'
                                        bot.write_msg(user, message, bot.regkb)
                            else:
                                if user in bot.reg:
                                    bot.reg[user][0](msg, user)
                                elif user in bot.restore:
                                    bot.restore[user][0](msg, user)
                                elif user in bot.report_user:
                                    bot.report(msg,user, bot.report_user[user][0])
                                    if msg.upper()=="ВЫЙТИ" or msg.upper() == "ПРЕКРАТИТЬ":
                                        bot.unreg(msg, user)
                                elif user in bot.shop_list:
                                    if msg.upper() in bot.shop_commands:
                                        bot.shop_commands[msg.upper()](msg, user)
                                    elif msg.upper()[:6] == "КУПИТЬ":
                                        bot.shop_list[user][3] = 1
                                        bot.shop(msg, user)
                                    elif bot.shop_list[user][3]==2:
                                        bot.shop(msg, user, bot.shop_list[user][4])
                                    else:
                                        bot.write_msg(user, 'Это что то странное. Состояние: {0}'.format(bot.shop_list[user]), bot.shop_list[user][2])
                                else:
                                    if bot.flag and user in bot.admins:
                                        bot.dialog(msg, user)
                                    else:
                                        message = 'Я такое не умею. Чтобы узнать список команд, напишите "хелп"'
                                        bot.write_msg(user, message)
                        else:
                            if msg.upper() == 'ПРЕКРАТИТЬ':
                                bot.unreg(msg,user)
                    elif event.from_chat:
                        msg = event.obj['message']['text']
                        if msg.upper()[31:42] == 'ОБЩАТЬСЯ С ':
                            bot.dialog_chat(msg)
                        else:
                            print(msg.upper()[:30])
                            print(msg.upper()[31:41])
        except Exception as err:
            lg.error('Ошибка {0} в потоке бота'.format(err))

def donate_thread():
    don = Donate()
    bot = VkBot()
    while True:
        try:
            check_time = time.time()
            donaters = don.get_donates()
            for donater in donaters:
                if check_time-donater['ts']<=5:
                    bot.give_money(donater['uid'],donater['sum']*100)
                    lg.info('Пользовтелю {0} выдано {1} валюты'.format(donater['ts'], donater['sum']*100))
            time.sleep(5)
        except Exception as err:
            lg.error("Ошибка {0} в потоке донатов".format(err))

def votnig():
    vote = Vote()
    while True:
        try:
            vote.get_votes()
        except Exception as err:
            lg.error('Ошибка {0} в потоке голосов'.format(err))
        time.sleep(5)

thread1 = thr.Thread(target=longpoll_thread)
thread2 = thr.Thread(target=donate_thread)
thread3 = thr.Thread(target=votnig)
thread1.start()
thread2.start()
thread3.start()