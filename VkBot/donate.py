import requests as rq
import pymysql as pms
import vk_api as api
import json

class donate():

    def __init__(self):
        pass

    def get_donates(self):
        request = 'https://api.vkdonate.ru?action=donates&count={0}&key=e21f784712a344c78dcb'.format(10)
        response = rq.get(request).text
        donaters = json.loads(response)['donates']
        print(donaters)
        return donaters

