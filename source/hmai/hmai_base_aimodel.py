# -*- coding: utf-8 -*-
# 1.0.0  wudongsheng
import tools.config as config
#import os


# 加载ai模型和进行图片分类的核心类
class BaseModelServer():


    # 模型初始化，在init中，即对象实例化中，初始化模型
    def __init__(self, title):

        self.ok = True
        self.title=title
        self.getOverload_pars(title)
        CHE_FILES = config.get_ai_conf()
        self.ai_kind = CHE_FILES["{}_kind".format(title)]


    def getOverload_pars(self, title):
        ret = {}
        ret['wait_num_1'] = int(config.get_ai_set_value(title, 'wait_num_1'))
        ret['wait_time_1'] = float(config.get_ai_set_value(title, 'wait_time_1'))
        ret['wait_num_2'] = int(config.get_ai_set_value(title, 'wait_num_2'))
        ret['wait_time_2'] = float(config.get_ai_set_value(title, 'wait_time_2'))
        self.overload_par = ret

    #这是使用多线程分别封装多个AI模型在一个AI服务中的预测函数
    # （接口函数，实际模型应该重新定义这个函数，但必须保存参数一致）
    def predict_mps(self, ai_t_res, image_data, title, logger=None, needLocation=False, placeai_addition=False,
                    add_var_1=0,
                    add_var_2=0,
                    add_var_3=0,
                    fr="f"
                    ):

        ret = self.predict(image_data, title, logger, needLocation, placeai_addition,
                           add_var_1,
                           add_var_2,
                           add_var_3,
                           fr,
                           )
        ai_t_res.append(ret)


    # 单模型预测的方法
    # 这是使用单线程封装单个AI模型在一个AI服务中的预测函数
    # （接口函数，实际模型应该重新定义这个函数，但必须保存参数一致）
    #image_data: 图片数据，不能空
    #title： 使用这个参数传入AI模型名，不能空
    #logger：可使用这个参数传入日志记录对象实例
    #needLocation：是否需要返回位置坐标，一般物体识别模型都返回识别出物体的坐标（minx, miny,maxx,maxy)
    #placeai_addition: 对于G3 （场景识别模型），此参数用于确定是否返回场景特征，例如（室内/室外。。。）
    #add_var_1,add_var_2, add_var_3 , 三个附加参数，如果不传入，默认为0
    #fr： 默认f,代表fpr优先策略（低错误率优先），如果是r,代表recall优先（召回率优先）
    #**

    def predict(self, image_data, title, logger=None, needLocation=False, placeai_addition=False,
                add_var_1=0,
                add_var_2=0,
                add_var_3=0,
                fr="f"
                ):
        pass
