# coding: utf-8

import sys
import base64
import hashlib
import random
import requests
import rsa
import time
import re
from urllib import parse
from CDNDrivePro.util import *
from .BaseApi import BaseApi

class AliApi(BaseApi):

    default_url = lambda self, hash: f"https://ae01.alicdn.com/kf/{hash}.png"
    extract_hash = lambda self, s: re.findall(r"\w{34}", s)[0]    

    def __init__(self):
        super().__init__()
        self.cookies = load_cookies('ali')
        
    def meta2real(self, url):
        if re.match(r"^aldrive://\w{34}$", url):
            return self.default_url(self.extract_hash(url))
        else:
            return None
            
    def real2meta(self, url):
        return 'aldrive://' + self.extract_hash(url)
        
    def set_cookies(self, cookie_str):
        self.cookies = parse_cookies(cookie_str)
        save_cookies('ali', self.cookies)
        
    def image_upload(self, img):
            
        url = 'https://kfupload.alibaba.com/mupload'
        files = {'file': (f"{time.time()}.png", img, 'image/png')}
        data = {
            'scene': 'aeMessageCenterImageRule', 
            'name': f'{time.time()}.png'
        }
        try:
            j = request_retry(
                'POST', url, 
                data=data, 
                files=files, 
                headers=AliApi.default_hdrs,
                cookies=self.cookies
            ).json()
        except Exception as ex:
            return {'code': 114514, 'message': str(ex)}
        
        j['code'] = int(j['code'])
        if j['code'] != 0:
            j['message'] = f"错误代码 {j['code']}"
        else:
            j['data'] = j['url']
        return j
        
def main():
    op = sys.argv[1]
    if op not in ['cookies', 'upload']:
        return
        
    api = AliApi()
    if op == 'cookies':
        cookies = sys.argv[2]
        api.set_cookies(cookies)
        print('已设置')
    else:
        fname = sys.argv[2]
        img = open(fname, 'rb').read()
        r = api.image_upload(img)
        if r['code'] == 0:
            print(r['data'])
        else:
            print('上传失败：' + r['message'])
    
if __name__ == '__main__': main()