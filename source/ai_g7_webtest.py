import requests
import base64
import json
import time
import os
import urllib3


# 构建请求串
def mak_req(img_domain='', filename='', aigroup='ai_g7', ais='keyword',
            textdata='', debug='y', loc='y', addition_info_in_place_ai='y',
            todo='', word='', kindnum=4):
    # if filename !='':
    rs = {}

    if textdata == '':
        rs.update({"imgurl": img_domain + filename})
        rs.update({"textdata": '0'})
    else:
        rs.update({"textdata": textdata})
        # rs.update({"imgurl": ''})
    if debug != '':
        rs.update({"debug": debug})
    if debug == 'y':
        rs.update({"picid": filename})
    if loc == 'y' or loc != 'n':
        rs.update({"loc": loc})
    if addition_info_in_place_ai == 'y' or addition_info_in_place_ai == 'n':
        rs.update({'addition_info_in_place_ai': addition_info_in_place_ai})
    # 请求的aigroup
    rs.update({"ais": ais})

    if aigroup == '':  # aigrou如果为空, 构造使用默认aigroup
        aigroup = self.aigroup
        rs.update({'aigroup': self.aigroup})
    elif aigroup == 'del':  # 如果aigroup 为del ，构造 请求中不加aigroup字段，应该返回错误
        print()
    elif aigroup == 'empty':  # 如果aigroup 为empty ，构造 请求中aigroup置空，应该返回错误
        rs.update({'aigroup': ''})
    else:
        rs.update({'aigroup': aigroup})

    if todo != '':
        rs.update({"todo": todo})

    if word != '':
        rs.update({"word": word})

    if kindnum != '':
        rs.update({"kindnum": kindnum})
    # print(str(rs))
    return rs


# 进行ai_group 请求，得到返回结果
def do_req(rs, ai_url):
    # do  http ai request
    http = urllib3.PoolManager()

    r = http.request(
        'post',
        ai_url,
        fields=rs
    )
    # print(r.data.decode())

    return r

if __name__=='__main__':

    url = 'http://172.16.208.144:5006'

    aiurl = '{}/ai'.format(url)
    textdata = '法轮功'
    rs = mak_req(filename='22123456', textdata=textdata, aigroup='ai_g7', ais='keyword')
    print (rs)
    r = do_req(rs, aiurl)
    d = json.loads(r.data.decode())
    print (d)

    # aiurl = '{}/manage'.format(url)
    # textdata = ''
    # rs = mak_req(aigroup='ai_g7', ais='keyword', todo='increase', word="囚禁", kindnum=1)
    #
    # print (rs)
    # r = do_req(rs, aiurl)
    # r.data.decode()
    # d = json.loads(r.data.decode())
    # print (d)