# -*- coding: utf-8 -*-
#import tools.config as config
#import os
import traceback
import time
import hmai.hmai_base_aimodel
#import pickle
import pandas as pd
import numpy as np
#import numpy as np
import pickle
import jieba
import fasttext
import re
import configparser
#import urllib.request
#from pyfasttext import FastText
from langconv import *
import cherry

# 加载ai模型和进行图片分类的核心类
class DefaultModelServer(hmai.hmai_base_aimodel.BaseModelServer):


    # 模型初始化，在init中，即对象实例化中，初始化模型
    def __init__(self, title):
        super(DefaultModelServer, self).__init__(title)

        # # 读取敏感词库
        # with open('ai/{}/fenlei_mingan'.format(title), 'rb') as f:
        #     self.mingan_dict = pickle.load(f)

        #读取jieba补充词库

        #jieba.load_userdict("ai/{}/jieba_buchong.txt".format(title))
        self.jieba_fnlp = jieba.Tokenizer()

        # 读取停止词库
        self.stopwords = pd.read_csv("ai/{}/stopwords.txt".format(title), index_col=False, quoting=3, sep="\t", names=['stopword'],
                                     encoding='utf-8').values

        # 加载fasttext模型
        self.ft_model = fasttext.load_model('ai/{}/classifier.model.bin'.format(title), label_prefix='__label__')
        #self.ft_model = fasttext.load_model('ai/{}/classifier.model.bin'.format(title))
        #==============================
        #print('ai/{}/classifier.model.bin'.format(title))
        cp = configparser.ConfigParser()
        cp.read('./ai/{}/labels.ini'.format(title),encoding='utf-8')
        kvs = cp.items("labels")
        kvs_cn = cp.items('labels_cn')

        #self.label_to_cate = {3: 'violation_politics', 2: 'normal_politics', 1: 'normal'}
        self.kind_book = []
        self.kind_book_cn = []

        for kv in kvs:
            self.kind_book.append(kv[1])

        for kv in kvs_cn:
            self.kind_book_cn.append(kv[1])



        self.ok = True
        self.title = title

    # 清洗分词函数
    def participle_fnlp(self, text, add_var_1=0):
        '''

        :param text: 待处理文档
        :param add_var_1: 0为默认模式,1为只去除常见标点符号,2为去除停止词（含标点符号）
        :return:
        '''
        if add_var_1==1:
            segs = re.sub(r'\.|#|，|/|,|。|!|:|《|》|-|\?', '', text)
        else:
            segs = text
        #精确模式
        segs = self.jieba_fnlp.lcut(segs)
        #全模式
        #segs = jieba.lcut(text, cut_all=True)
        segs = list(filter(lambda x: len(x) > 0, segs))
        if add_var_1 == 2:
            segs = list(filter(lambda x: x not in self.stopwords, segs))
        segs = list(filter(lambda x: x != ' ', segs))

        #print(segs)
        #print(segs1)
        return segs

    # fasttext类别预测函数
    def fasttest_juge(self, text):
        try:
            res = [' '.join(text)]
            #print("res:{}".format(res))
            labels = self.ft_model.predict(res)
            #print("cate_num:{}".format(labels[0][0]))
            #===========================
            #print(labels[0][0])
        except:
            #exstr = traceback.format_exc()
            #print(exstr)
            labels = self.ft_model.predict("common")

        return labels[0][0], self.kind_book[int(labels[0][0])-1]
        #return self.label_to_cate[int(labels[0][0])]

    # 繁体化简体函数
    def fan2jian(self, text):

        line = Converter('zh-hans').convert(text)
        line.encode('utf-8')
        return line

    # 预测的方法
    def predict(self, text_data, title, logger=None, needLocation=False, placeai_addition='n', add_var_1=0, add_var_2=0, add_var_3=0,fr="f"):
        dic = {}
        dic['model'] = title
        dic['kind'] = self.ai_kind
        dic['mr'] = []
        #=============  overload 自动抛弃
        i = 0
        while self.ok == False:
            i += 1
            if i < self.overload_par['wait_num_1']:
                time.sleep(self.overload_par['wait_time_1'])
            elif i < (self.overload_par['wait_num_2'] + self.overload_par['wait_num_1']) and i >= self.overload_par[
                'wait_num_1']:
                time.sleep(self.overload_par['wait_time_2'])
            else:
                dic['!error'] = "overload"
                dic['code'] = '-1'
                dic['error'] = 'overload'
                dic['error_mes'] = "overload {}".format(time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time())))
                return dic

        self.ok = False
        #==================================
        try:
            # 将获得的文本全部转化为简体
            text_data = self.fan2jian(text_data)
            cate_label = self.kind_book[np.argmax(cherry.classify(model='harmful', text=[text_data]).probability[0])]

            if cate_label == "normal":
                dic['code'] = '0'


            else:
                dic['code']='1'
                subdic={}
                subdic['class']=cate_label
                dic['mr'].append(subdic)

            self.ok = True

            return dic

        except (Exception) as e:
            self.ok = True
            exstr = traceback.format_exc()
            # logger.error("game_screen_predict_error  " + exstr)
            dic['!error'] = exstr
            dic['code'] = '-1'
            dic['error'] = 'exception'
            dic['error_mes'] = 'fnlp error at:{}'.format(
                time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time())))
            return dic


if __name__ == '__main__':
    print("runing")
    a = DefaultModelServer('cherry')
    while(1):
        input_word = input('请输入需要检测的语段：')
        res = a.predict(input_word,'cherry')
#        res = a.juge(input_word)
        print (res)

