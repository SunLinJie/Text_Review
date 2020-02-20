# -*- coding: utf-8 -*-
import configparser
# 读取配置文件，返回各ai模型配置（返回字典类型）
def get_ai_conf():
    dic = {}
    cp = configparser.ConfigParser()
    cp.read('./ai/conf/conf.ini')
    secs = cp.sections()

    for se in secs:
        dic[se] = cp.get(se, "set")
        dic['{}_kind'.format(se)] = cp.get(se, "kind")

    return dic


def get_ai_set_value(section,key):
    str = None
    cp = configparser.ConfigParser()
    cp.read('./ai/conf/conf.ini')
    secs = cp.sections()

    for se in secs:
        if se == section:
            str = cp.get(se, key)
    return str

def get_open_ais():

    cp = configparser.ConfigParser()
    cp.read('./ai/conf/conf.ini')
    secs = cp.sections()

    return secs

def get_ai_model(title):

    cp = configparser.ConfigParser()
    cp.read('./ai/conf/ais.ini')
    return cp.get(title, "model")

def get_com_conf():

    cp = configparser.ConfigParser()
    cp.read('./ai/conf/common.ini')
    #secs = cp.sections()

    ret = cp.items('common')
    dic = {}
    for ite in ret:

        dic.update({ite[0]:ite[1]})

    return dic



    
    
if __name__ == '__main__':
    print(get_com_conf())
        