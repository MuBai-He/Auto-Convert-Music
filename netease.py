#coding=UTF-8
import os
import re
import requests
import json

class Netease_music():
    def __init__(self,address="http://localhost:3000"):
        self.netease = requests.session()
        self.address=address
        try:
            with open('netease.txt', 'r') as f:
                pass
            self.load_cookie()
        except:
            print("                         请先登陆")
            self.log_in()
        print("当前账号",json.loads(self.netease.get(address+"/login/status").text)["data"]["profile"]["nickname"])
    def load_cookie(self):
        with open('netease.txt') as f:
            self.netease.cookies.update(json.loads(f.read()))

    def save_cookie(self):
        with open('netease.txt','w') as f:
            cookie=json.dumps(self.netease.cookies.get_dict())
            f.write(cookie)
    def search_music(self,song_name):
        info=self.netease.get(self.address+f"/search?keywords={song_name}&limit=1").text
        info=json.loads(info)['result']['songs'][0]
        id=info['id']
        name=info['name']
        return id,name

    def search_download_music(self,song_name,level="exhigh"):

        id,name=self.search_music(song_name=song_name)
        if not os.path.exists('input'):
            os.mkdir('input')
        song_url = self.netease.get(self.address+f"/song/url/v1?id={id}&level={level}").text
        song_url=json.loads(song_url)['data'][0]['url']
        song=self.netease.get(song_url)
        suffix = song_url.split(".")[-1]
        file_path='input\\' + name + '.' + suffix
        with open( file_path, 'wb') as f:
            f.write(song.content)
        return name,file_path

    def download_music(self,id,level="exhigh"):
        if not os.path.exists('input'):
            os.mkdir('input')
        song_url = self.netease.get(self.address+f"/song/url/v1?id={id}&level={level}").text
        song_url=json.loads(song_url)['data'][0]['url']
        song=self.netease.get(song_url)
        name=self.netease.get(self.address+f"/song/detail?ids={id}").text
        name=json.loads(name)['songs'][0]['name']
        name = re.sub(r'[\[\]<>:"/\\|?*.]', '', name).rstrip('. ')  #特殊字符处理
        suffix = song_url.split(".")[-1]
        file_name='input\\' + name + '.' + suffix
        with open( file_name, 'wb') as f:
            f.write(song.content)
        return name,file_name

    def log_in(self):
        print("######################################################\n"
              "                       请选择登陆方式\n"
              "1.邮箱登录 2.手机号登陆 3.手机验证码登陆 4.扫码登陆 5.游客登陆")
        while True:
            select=0
            try:
                select=int(input("\n请输入数字序号："))
            except:
                pass

            if select==1:
                email=input("请输入邮箱：")
                password=input("请输入密码：")
                self.netease.post(f"/login?email={email}&password={password}")
                self.save_cookie()
            elif select==2:
                phone=input("请输入手机号：")
                password=input("请输入密码：")
                self.netease.post(self.address+f"/login/cellphone?phone={phone}&password={password}")
                self.save_cookie()
                break
            elif select==3:
                phone=input("请输入手机号：")
                self.netease.post(self.address+f"/captcha/sent?phone={phone}")
                password=input("请输入验证码：")
                self.netease.post(self.address+f"/captcha/verify?phone={phone}&captcha={password}")
                self.save_cookie()
                break
            elif select==4:
                print("懒得写了")
            elif select==5:
                self.netease.post(self.address+f"/register/anonimous")
                self.save_cookie()
                break
            else:
                print("输入错误，重新输入！")
