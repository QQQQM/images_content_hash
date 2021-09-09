
import os
import time
import json
import random
import pymysql
import requests

class sql_maneger(object):
    def __init__(self, name, save_path, num, start = 0):   # 输入表名，查询条数，开始条数 
        self.sql_name = name
        self.save_path = save_path
        self.lookup_start = start
        self.lookup_num = num
        self.conn = pymysql.connect(host = 'localhost', port = 3306, user = "root", passwd = "123456", db = "test")
        self.cur = self.conn.cursor()  
        self.image_id_list = self.lookup()
        self.ip_proxy = ""
        self.ip_proxy_num = 0
        self.ip_pool = []
        self.manifest_info = ""

    
    def lookup(self):
        sql = "select name from " + self.sql_name + " limit " + str(self.lookup_start) + "," + str(self.lookup_num) + ";"
        cnt = self.cur.execute(sql)
        list = []
        for _ in range(cnt):
            result = self.cur.fetchone()
            list.append(result[0].replace("+","/"))
        return list

    def get_ippool(self):
        response = requests.get("https://ip.jiangxianli.com/api/proxy_ips")
        response_data = json.loads(response.text)["data"]
        next_page_url = response_data["next_page_url"]
        while(1):
            length = len(response_data["data"])
            print("正在请求：", next_page_url)
            # print(length)
            for i in range(length):
                ip = response_data["data"][i]["ip"] + ":" + response_data["data"][i]["port"]
                if ip not in self.ip_pool : self.ip_pool.append(ip)
            if next_page_url == None : break          
            response = requests.get(next_page_url)
            response_data = json.loads(response.text)["data"]
            next_page_url = response_data["next_page_url"]
        print("ip代理池为：", self.ip_pool)
    
    def update_proxy(self):
        cnt = 0
        while(1):
            cnt += 1
            length = len(self.ip_pool)-1
            num = random.randint(0,length)
            proxy = {'https': self.ip_pool[num]}
            try:
                response = requests.get("https://httpbin.org/ip", timeout=3, proxies=proxy)
                if response.status_code == 200:
                    print(response.text)
                    break
            except:
                print(f'requests failed {cnt} time')
                self.ip_pool.pop(num)
                if length <= 5:
                    print("ip代理池中的ip数量小于5个，正在补充...")
                    time.sleep(10)
                    self.get_ippool()
        self.ip_proxy_num = num
        self.ip_proxy = self.ip_pool[num]
        print("当前ip代理为：",self.ip_proxy,", ip代理池数量为：",len(self.ip_pool))
        

    
    # def read_json(self):
    #     with open(self.save_path,'r',encoding='utf8')as fp:
    #         json_data = json.load(fp)
    #         print(json_data)

    def get_manifest(self):
        for cnt, image in enumerate(self.image_id_list):
            print(cnt,"----------", image)
            # if cnt%80 == 79:
            #     self.update_proxy()
            proxy = {'https': self.ip_proxy}

            image_name = image.split(":")[0]
            image_tag = image.split(":")[1]
            response = requests.get("https://auth.docker.io/token?service=registry.docker.io&scope=repository:" + image_name + ":pull")
            token = json.loads(response.text)["token"]
            print(token)
            headers = {'Authorization': 'Bearer ' + token,
                        'Accept': 'application/vnd.docker.distribution.manifest.v2+json'
                        # 'Accept': 'application/vnd.docker.distribution.manifest.list.v2+json',
                        # 'Accept': 'application/vnd.docker.distribution.manifest.v1+json'
                        }

            while(1):
                try:
                    print("正在尝试获取manifest...")
                    r = requests.get('https://registry-1.docker.io/v2/' + image_name + '/manifests/' + image_tag, headers=headers, timeout=5, proxies=proxy ) # , proxies=proxy
                    self.manifest_info = r.text
                    print(r.status_code)
                    print(self.manifest_info)
                    if r.status_code == 404 :
                        print("可能错误：manifest不存在，选择跳过...")
                        break

                    if r.status_code == 401 :
                        print("可能错误：未授权，选择跳过...")
                        break

                    if r.status_code == 200 :                        
                        print(cnt, "=== 当前ip代理为：", self.ip_proxy)
                        break
                    else:
                        self.ip_pool.pop(self.ip_proxy_num)
                        print("获取manifest失败（可能是次数限制1）！正在尝试更换代理....")
                        self.update_proxy()

                except:
                    self.ip_pool.pop(self.ip_proxy_num)
                    print("获取manifest失败（很有可能是次数限制2）！正在尝试更换代理....")
                    self.update_proxy()
            


            # command = "bash ./simple.sh " + self.save_path + " " + image
            # data = os.popen(command)
            # data = json.loads(data.read())
            # json_str = json.dumps(data, sort_keys=True, indent=2)
            # print(json_str)

    def commit(self):
        self.conn.commit()
    
    def quit(self):
        self.cur.close()
        self.conn.close()

def main():
    sql = sql_maneger("dockerfile", "./data", 1000,963)  # 输入表名，json数据位置，查询条数，开始条数 
    sql.get_ippool()
    sql.update_proxy()
    sql.get_manifest()
    
    
    sql.quit()


if __name__ == "__main__":
    main()