#!/usr/bin/python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree
import datetime
import requests
import random
import json
import time
import sys
import re
import os


class xatBotStat:
    def __init__(self):
        try:
            self.run()
        except KeyboardInterrupt:
            self.restart()
            self.run()

    def run(self):
        self.commands = (
            'clock',
            'date',
            'steam',
            'randomavatar',
            'setname',
            'setavatar',
            'setstatus',
            'setgame',
        )
        self.showHelp()
        self.id = self.getId()
        self.key = self.getKey()
        self.room = self.getRoom()
        self.handle()

    def showHelp(self):
        self.write('Commands available: ')
        for c in self.commands:
            self.write('* ' + c, 2)
        self.write('', 2)

    def getId(self):
        uid = self.raw('What is your xat username: ')
        getUser = self.getSite('https://xat.me/web_gear/chat/profile.php?name=' + uid)
        if not uid.isalnum() or not getUser[1].isdigit():
            self.write('Invalid xat ID', 1)
            return self.getId()
        else:
            return getUser[1]

    def getRoom(self):
        room = self.raw('What is chat name: ')
        getRoom = self.getSite('https://xat.com/api/roomid.php?d=' + room)
        if (getRoom[1])[:6] == '-10-11':
            self.write('Chat not found', 1)
            return self.getRoom()
        else:
            load = json.loads(getRoom[1])
            return load['id']

    def getKey(self):
        key = self.raw('What is your api key: ')
        if key is None or len(key) < 14: # nice number for now
            self.write('Invalid API key', 1)
            return self.getKey()
        else:
            return key
            
    def getSteamUser(self):
        user = self.raw('What is your Steam profile: ')
        if not user:
            self.write('Invalid username', 1)
            return self.getSteamUser()
        else:
            return user

    def handle(self):
        cmd = self.raw('Command: ')
        
        if cmd not in self.commands:
            self.write('Command not found', 1)
            self.handle()

        elif cmd == 'date':
            self.write('You can stop using CTRL + C')
            while True:
                datenow = datetime.datetime.now().strftime('%Y-%m-%d')
                self.send({'s': datenow})
                time.sleep(43200) # update each 12hours
                
        elif cmd == 'steam':
            user = self.getSteamUser()
            self.write('You can stop using CTRL + C')
            while True:
                inGame = self.getCurrentGame(user)
                if not inGame:
                    self.send({'s': ' '})
                else:
                    self.send({'s': 'Steam: ' + inGame})
                time.sleep(10) # update each 10sec...
            
        elif cmd == 'clock':
            self.write('You can stop using CTRL + C')
            while True:
                timenow = datetime.datetime.now().strftime('%H:%M:%S')
                self.send({'s': timenow})
                time.sleep(10) # update each 10sec....
                
        elif cmd == 'randomavatar':
            avchoose = random.randint(1, 1759)
            self.send({'a': avchoose})
            self.write('Avatar choose: ' + avchoose, 1)
            self.handle()
            
        elif cmd == 'setname':
            name = self.raw('New name: ')
            self.send({'n': name})
            self.write('Your name is now: ' + name, 1)
            self.handle()
            
        elif cmd == 'setavatar':
            avatar = self.raw('New avatar: ')
            self.send({'a': avatar})
            self.write('Your avatar is now: ' + avatar, 1)
            self.handle()
            
        elif cmd == 'setstatus':
            status = self.raw('New status: ')
            self.send({'s': status})
            self.write('Your status is now: ' + status, 1)
            self.handle()
            
        elif cmd == 'setgame':
            game = self.raw('What game are you playing: ')
            self.send({'s': 'Playing: ' + game})
            self.write('Ok, you are playing: ' + game, 1)
            self.handle()

    def raw(self, text):
        if sys.version_info > (3, 0):
            return input(text)
        else:
            return raw_input(text)

    def restart(self):
        if os.name == 'nt':
            os.system('cls')
            os.system('title xat Botstat')
        else:
            os.system('clear')
            sys.stdout.write('\x1b]2;xat Botstat\x07')

    def send(self, values={}):
        result = ''
        values.update({'r': str(self.room), 'u': int(self.id), 'k': str(self.key)})
        for (k, v) in values.items():
            result += '&' + k + '=' + str(v)
        final = self.getSite('https://xat.com/api/botstat.php?' + result)
        load = json.loads(final[1])
        if load['error'] == True:
            return self.onError(load)
        else:
            return True

    def onError(self, load):
        getError = load['message']
        self.restart()
        if getError[:2] == '10':
            self.write('Invalid params, try change your status', 1)
        elif not getError[0].isdigit():
            self.write(getError, 1)
        elif getError[:1] == '1':
            self.write('Chat not found', 1)
        elif getError[:1] == '5':
            self.write('Failed, you are not online at this chat', 1)
        elif getError[:1] == '6':
            self.write('You need power STATUS enabled', 1)
        elif getError[:1] == '7':
            self.write('You need power BOTSTAT', 1)
        elif getError[:1] == '9':
            self.write('Max 3 requests each 20 seconds reached', 1)
        self.write('', 2)
        self.run()

    def write(self, text, type=0):
        if type == 1:
            print('< ' + text)
        elif type == 2:
            print(text)
        else:
            print('> ' + text)
            
    def getCurrentGame(self, user):
        if not user:
            return False
        getGame = self.getSite('https://steamcommunity.com/id/%s?xml=1&t=%s' % (user, random.random()))
        input = getGame[1].decode()
        root = xml.etree.ElementTree.fromstring(input)
        for child in root:
            if 'In-Game' in str(child.text):
                return str(child.text).replace('In-Game<br/>', '')
        return False
       
    def getSite(self, url):
        if not url:
            return False
        response = requests.get(url)
        return [response.status_code, response.content]

xatBotStat()
