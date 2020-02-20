# -*- coding: utf-8 -*-
# 1.0.0  wudongsheng
import sys
sys.path.append("..")

import tools.config as config

#import aimodel_ssd_1
import traceback
import  importlib
#import os

class AiGroup():
    default_ai_pipline = []
    group_servers = {}
    disulog = None
    overload_counter = {}

    def __init__(self, group, logger):

        self.default_ai_pipline = group


        #print(group)
        for ai in group:

            model = config.get_ai_model(ai)
            # print (model)
            aClass='aimodel_{}'.format(model)
            modelClass = importlib.import_module(aClass) #动态加载
            self.group_servers[ai] = modelClass.DefaultModelServer(ai)

            #overload 技术器置0
            self.overload_counter[ai] = 0


        # 日志记录器
        self.disulog = logger

    def set_ai(self, ai_title, ai_server):
        """
        :param ai_title: ai服务标题， 字符串
        :param ai_server: ai服务,  DefaultModelServer对象实例
        """
        self.group_server[ai_title] = ai_server

    # 按ai服务标题，获得实际的ai服务
    def get_ai(self, ai_title):
        """
        :param ai_title: ai服务标题， 字符串
        :returns: ai服务,  DefaultModelServer对象实例
        """
        return self.group_servers[ai_title]

    # 按用户请求， 执行 所有该执行的 ai
    def doais(self, image_data, req_ais, needLocation=False,  placeai_addition=False, fr='f',
              add_var_1=0, add_var_2=0, add_var_3=0
              ):

        """ai_title
        :param image_data: 图片数据 二进制数据
        :param req_ai: 用户请求的ai服务 list


        """
        # result是返回给请求方的结果（json）
        result = []

        continue_ai = 1

        # 按default_ai_pipline 顺序遍历整个ai group
        for ai_title in req_ais:
            # ais_values[ai_title] = 0
            # 如果也在用户请求的ai服务列表中
            if ai_title in self.default_ai_pipline:
                # 执行预测 ai 分类
                # 先获取对应的 ai 服务
                ai_server = self.get_ai(ai_title)

                if ai_server is not None and continue_ai == 1:
                    # 对图片分类进行预测
                    ai_return = ai_server.predict(image_data, ai_title, self.disulog, needLocation,
                                                  placeai_addition,
                                                  add_var_1,
                                                  add_var_2,
                                                  add_var_3,
                                                  fr
                                                  )

                    # 构造返回结果
                    self.update_res(result, ai_return, ai_title)



        return result

    def manage_word(self,todo,word,kindnum):
        ai_server = self.get_ai('keyword')

        ret = ai_server.manage_word(todo, word, kindnum)

        return ret
    def allwords(self):
        ai_server = self.get_ai('keyword')
        if ai_server == None:
            return None
        return  ai_server.allwords()


    # 一个小工具函数，用于拼接 返回结果（字典类型）
    def update_res(self, result, res, ai_title):
        """
        :param result: 是对请求者的最终返回值 字典
        :param res: 执行某个ai分类返回的字典数据类型 字典
        :param ai_title: ai服务的名称
        :returns: 拼接的结果
        """

        if res['code'] == '-1':
            try:
                self.disulog.error(res['model'] + "_error: " + res['!error'])
                del res['!error']
                #res.pop['!error']
                v=self.overload_counter[res['model']]
                self.overload_counter[res['model']] = v+1
            except Exception:
                exstr = traceback.format_exc()
                self.disulog.error(res['model'] + "_error: del res['!error'] fail"+exstr )
            # 说明ai分类执行过程中没有出错，正确返回
            # res.pop('statu')
        result.append(res)

        return result

