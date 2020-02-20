# -*- coding: utf-8 -*-
#import tools.config as config
#import os
import traceback
import time
import hmai.hmai_base_aimodel
#import pickle
import pandas as pd
#import numpy as np
import pickle
import jieba
#import fasttext
import re
import configparser
#import urllib.request
from langconv import *

# 加载ai模型和进行图片分类的核心类
class DefaultModelServer(hmai.hmai_base_aimodel.BaseModelServer):


    # 模型初始化，在init中，即对象实例化中，初始化模型
    def __init__(self, title):
        super(DefaultModelServer, self).__init__(title)

        # 读取敏感词库
        with open('ai/{}/fenlei_mingan'.format(title), 'rb') as f:
            self.mingan_dict = pickle.load(f)

        # 读取jieba补充词库
        self.jieba_kw= jieba.Tokenizer(dictionary="ai/keyword/jieba_kwdict.txt")

        #jieba.load_userdict("ai/{}/jieba_buchong.txt".format(title))

        # 读取停止词库
        self.stopwords = pd.read_csv("ai/{}/stopwords.txt".format(title), index_col=False, quoting=3, sep="\t", names=['stopword'],
                                     encoding='utf-8').values
        #
        # # 加载fasttext模型
        # self.ft_model = fasttext.load_model('file/classifier.model.bin', label_prefix='__label__')

        cp = configparser.ConfigParser()
        cp.read('./ai/{}/labels.ini'.format(title),encoding='utf-8')
        kvs = cp.items("labels")
        #kvs_cn = cp.items('labels_cn')
        # kvs_cate = cp.items('cate')
        #self.label_to_cate = {3: 'violation_politics', 2: 'normal_politics', 1: 'normal'}
        self.kind_book = []
        #self.kind_book_cn = []
        self.label_to_cate = {}
        for kv in kvs:
            self.kind_book.append(kv[1])

        # for kv in kvs_cn:
        #     self.kind_book_cn.append(kv[1])

        #num = 1
        # for kv in kvs_cate:
        #     self.label_to_cate[num] = kv[1]
        #     num += 1

        self.ok = True
        self.title = title

    # 清洗分词函数
    def participle_kw(self, text, add_var_1=0):
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
        segs = self.jieba_kw.lcut(segs)
        #全模式
        #segs = jieba.lcut(text, cut_all=True)
        segs = list(filter(lambda x: len(x) > 0, segs))
        if add_var_1 == 2:
            segs = list(filter(lambda x: x not in self.stopwords, segs))
        segs = list(filter(lambda x: x != ' ', segs))

        return segs

    # # fasttext类别预测函数
    # def fasttest_juge(self, text):
    #
    #     res = [' '.join(text)]
    #     labels = self.ft_model.predict(res)
    #
    #     return self.label_to_cate[int(labels[0][0])]

    # 敏感词判断函数
    def juge(self, text):

        weigui_word = []
        weigui_kind = []

        for word in text:
            if word in self.mingan_dict:
                weigui_word.append(word)
                weigui_kind.append(self.mingan_dict[word])
            else:
                continue


        return weigui_word, weigui_kind

    # 繁体化简体函数
    def fan2jian(self, text):

        line = Converter('zh-hans').convert(text)
        line.encode('utf-8')
        return line



    def jieba_buchong(self):
        # 遍历敏感字典中的词并增加到分词词库当中

        vocab_txt = []

        for word in self.mingan_dict:
            vocab_txt.append(word + ' 1\n')

        with open('/data/ai_g7/jieba_kwdict.txt', 'w') as f:
            f.writelines(vocab_txt)
        with open('ai/{}/jieba_kwdict.txt'.format(self.title), 'w') as f:
            f.writelines(vocab_txt)

    def search(self, word):

        if word in self.mingan_dict:
            kind = self.mingan_dict[word]
            for i in range(len(self.kind_book)):
                if kind == self.kind_book[i]:
                    return self.kind_book[i]
        else:
            return None



    def increase(self, word, kind_num):

        kind = self.kind_book[int(kind_num)]
        self.mingan_dict[word] = kind

        # 存储新敏感词库
        with open('ai/{}/fenlei_mingan'.format(self.title), 'wb') as f:
            pickle.dump(self.mingan_dict, f)

        # 存储新jieba分词库
        #print('更新jieba词库中……')
        self.jieba_buchong()
        print(word)
        jieba.add_word(word)

    def change(self, word, kind_num):

        kind = self.kind_book[int(kind_num)]
        self.mingan_dict[word] = kind

        # 存储新敏感词库
        with open('ai/{}/fenlei_mingan'.format(self.title), 'wb') as f:
            pickle.dump(self.mingan_dict, f)

    def delete(self, word):


        self.mingan_dict.pop(word)

        # 存储新敏感词库
        with open('ai/{}/fenlei_mingan'.format(self.title), 'wb') as f:
            pickle.dump(self.mingan_dict, f)

    def allwords(self):

        return ','.join(self.mingan_dict.keys())


    def manage_word(self,todo,word,kindnum):
        ret = '1'

        if todo=='increase':
            self.increase(word,kindnum)
            #return '已将"'+word+'"增加为“'+self.kind_book[int(kindnum)]+'”类别'
            return ret

        elif todo =='change':
            if word in self.mingan_dict:
                self.change(word,kindnum)
                #return '已将"'+word+'"更改为“'+self.kind_book[int(kindnum)]+'”类别'
                return ret
            else:
                return '-1'

        elif todo =='delete':
            if word in self.mingan_dict:
                self.delete(word)

            else:
                return '-1'

        elif todo == 'search':
            if word in self.mingan_dict:
                return self.search(word)
            else:
                return '-1'

        elif todo == 'notice':
            if word == '1':

                with open('/data/ai_g7/sensitive_words', 'rb') as f:
                    self.mingan_dict = pickle.load(f)

                self.jieba_kw = jieba.Tokenizer(dictionary="/data/ai_g7/jieba_kwdict.txt")
                print ('update successful')
                return '1'
            else:
                return '-1'
        else:

            return '-2'

    # def predict_mps(self, ai_t_res, text_data, title, logger=None, needLocation=False, placeai_addition=False):
    #     ret = self.predict(text_data, title, logger, needLocation, placeai_addition)
    #     ai_t_res.append(ret)

    # 预测的方法
    def predict(self, text_data, title, logger=None, needLocation=False, placeai_addition='n', add_var_1=0, add_var_2=0, add_var_3=0, fr="f"):
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
            par_words = self.participle_kw(text_data, add_var_1)
            # cate = self.fasttest_juge(par_words)
            # dic['cate'] = cate
            words,kind = self.juge(par_words)
            if words == []:
                dic['code'] = '0'

            else:

                having_word = []
                num = len(self.kind_book)

                sublists = [0]*num
                for i in range(num):
                    sublists[i] = [i]

                dics = [0]*num

                for i in range(num):
                    dics[i] = {}
                    dics[i]['class'] = self.kind_book[i]

                for i in range(len(kind)):
                    subdict = {}

                    if words[i] not in having_word:
                        for l in range(num):
                            if kind[i] == self.kind_book[l]:
                                subdict['word']=words[i]

                                subdict['num']=words.count(words[i])

                                sublists[l].append(subdict)

                        having_word.append(words[i])
                    else:
                        pass
                for i in range(num):
                    dics[i]['words'] = sublists[i][1:]
                    if sublists[i] != [] and len(dics[i]['words']) >0 :
                        dic['code'] = 1
                        dic['mr'].append(dics[i])

        except (Exception) as e:
            self.ok = True
            exstr = traceback.format_exc()
            # logger.error("game_screen_predict_error  " + exstr)
            dic['!error'] = exstr
            dic['code'] = '-1'
            dic['error'] = 'exception'
            dic['error_mes'] = 'keyword error at:{}'.format(
                time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time())))

            return dic
        # dic 是用于反馈详细信息的字典对象， 另一个是 分类结果的 概率
        self.ok = True
        return dic

if __name__ == '__main__':
    print("runing")
    a = DefaultModelServer('keyword')
    while(1):
        input_word = input('请输入需要检测的语段：')
        res = a.predict(input_word,'keyword')
#        res = a.juge(input_word)
        print (res)

