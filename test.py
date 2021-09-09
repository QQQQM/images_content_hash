import json
import time
from os import PRIO_PGRP, pread, system, times
import random
import requests


def renew ():
    response = requests.get("https://ip.jiangxianli.com/api/proxy_ip")
    ip = json.loads(response.text)["data"]["ip"]
    port = json.loads(response.text)["data"]["port"]
    pp = ip + ":" + port
    return pp

pp = renew()
print(pp)

proxy = {'https': pp}

trytimes = 5
for i in range(trytimes):
    try:
        response = requests.get("https://httpbin.org/ip", proxies=proxy)
        if response.status_code == 200:
            break
    except:
        print(f'requests failed {i} time')
        time.sleep(5)
        pp = renew()
        print(pp)   
print(response.text)


response = requests.get("https://auth.docker.io/token?service=registry.docker.io&scope=repository:000019950000/ubu3:pull")
token = json.loads(response.text)["token"]
print(token)

headers = {'Authorization': 'Bearer ' + token,
            'Accept': 'application/vnd.docker.distribution.manifest.v2+json'
            # 'Accept': 'application/vnd.docker.distribution.manifest.list.v2+json',
            # 'Accept': 'application/vnd.docker.distribution.manifest.v1+json'
            }
r = requests.get("https://registry-1.docker.io/v2/000019950000/ubu3/manifests/latest", headers=headers,proxies=proxy)

print(r.status_code)
print(r.text)

