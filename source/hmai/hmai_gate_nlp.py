# -*- coding: utf-8 -*-
# 2.0.1  wudongsheng
import sys
sys.path.append("..")
import urllib.request
import traceback
import json
import ailog
import os
from tools import config
import base64
from flask import Flask, request, Response, make_response
import codecs
from tools.errortool import make_error

#import tools.gputool as gputool
from flask_limiter import Limiter
import time
#import prometheus_client
#from prometheus_client import Counter



# from flask_limiter.util import get_remote_address

class AI_gate():
    def __init__(self):
        self.firstTime = True
        self.ai_group_list = config.get_open_ais()
        self.models_str = "#".join(self.ai_group_list)
        # print(str(ai_group_list))
        self.disulog = ailog.AILog()
        self.qps_counter = 0

        pars_dic = config.get_com_conf()

        default_s_limit = int(pars_dic['default_s_qps'])
        default_5s_limit = int(pars_dic['default_5s_qps'])
        self.default_port = int(pars_dic['port'])
        self.version = pars_dic['version']
        self.group_name = pars_dic['group_name']
        self.min_gpu_mem = int(pars_dic['min_gpu_mem'])

        # 通讯协议版本
        self.pro_ver = pars_dic['pro_ver']
        #======== no GPU ================================
        #self.gpu_device = gputool.getBestGpu(self.min_gpu_mem)
        self.gpu_device = -1

        #print("GPU checking:=====:{}".format(self.gpu_device))
        #os.environ['CUDA_VISIBLE_DEVICES'] = '{}'.format(self.gpu_device)
        # =========================================================

        # 通过环境变量 设定接口限速(请求数/s)，可以中启动docker时设定
        self.my_s_limiter = os.getenv('AI_LIMIT_S')
        self.my_5s_limiter = os.getenv('AI_LIMIT_5S')

        if self.my_s_limiter == None:
            self.my_s_limiter = default_s_limit
        if self.my_5s_limiter == None:
            self.my_5s_limiter = default_5s_limit

        self.start_time = time.time()
        self.main_counter=0

    # 定义限速器访问技术的 key
    def get_myrequest(self):
        try:
            aigroup = urllib.request.unquote(request.form.get('aigroup'))
        except:
            aigroup ='None'
        return aigroup
    #把aigroup实例传进来，这样，在后面的 /metric 中，就可以访问aigroup中的overload计数了
    def set_group(self, aigroup):
        self.myaigroup = aigroup
    # api 服务入口函数==============================================
    def make_app(self, myaigroup):
        app = Flask(__name__)
        #self.requests_total = Counter("request_count", "Total request count of the ai")
        #limiter = Limiter(app, key_func=self.get_myrequest)
        limiter = Limiter(
            app,
            key_func=self.get_myrequest,
            default_limits=["{}/second".format(self.my_s_limiter), "{}/5seconds".format(self.my_5s_limiter)]
        )
        limiter.init_app(app)

        # =========================================================
        def health():
            dic={}
            now = time.time()
            try:
                #no image ,but text =======================================
                data='这是一段测试文本，公安部，法制，最高法院，司法独立'
                health_str = myaigroup.doais(data, self.ai_group_list)
                #print(health_str)
                ret = 'ok'
                for one_value in health_str:
                    if one_value['code'] == '-1':
                        ret = '-1'
                now2 = time.time()
                dic['health']=ret
                dic['speed']=str(round(now2-now,4))
                return dic
            except Exception:
                exstr = traceback.format_exc()
                self.disulog.error(exstr)
                dic['health'] = "-1"
                dic['speed'] = '-1'
                return dic


        #===========================================================
        # 当超过限速，返回错误信息
        @app.errorhandler(429)
        def ratelimit_handler(e):
            mes = 'max_s_qps is={} max_5s_qps is={}'.format(str(self. my_s_limiter), str(self.my_5s_limiter))
            ret = make_error(self.models_str, 'up_qps', mes)
            ret.update({"pro_ver": "{}".format(self.pro_ver)})
            self.qps_counter= self.qps_counter+1

            print(e.description)
            return Response(json.dumps(ret), mimetype='application/json')

        @app.route('/logfiles')
        @limiter.exempt
        def logfiles():
            strs = []
            list = os.listdir('./log')
            for i in list:
                strs.append(i + '\n')
            return ''.join(strs)

        @app.route('/logfile')
        @limiter.exempt
        def logfile():

            rf = request.args.get('f')
            strs = []
            with open('./log/' + rf, 'r') as f:
                while 1:
                    lines = f.readlines(100)
                    if not lines:
                        break
                    for line in lines:
                        strs.append(line)
            return ''.join(strs)

        @app.route('/about')
        @limiter.exempt
        def ais():
            return 'server:{}, aimodel:{}, version:{}\n'.format(self.group_name, self.models_str, self.version)

        @app.route('/ais_all')
        @limiter.exempt
        def ais_all():
            strs = []

            for i in self.ai_group_list:
                strs.append('\n')
                strs.append(i)
                strs.append('\n--------------\n')
                num = 0
                with codecs.open('./ai/' + i + '/labels.txt', 'r', 'utf-8') as f:
                    while 1:
                        lines = f.readlines(30)
                        if not lines:
                            break
                        for line in lines:
                            strs.append(line)
                            num = num + 1

            return ''.join(strs)




        @app.route('/areyouok')
        @limiter.exempt
        def areyouok():
            dic = health()
            return 'health:{}, speed:{}s/per_dectection\n'.format(dic['health'],dic['speed'])


        """
        @app.route('/gpu')
        @limiter.exempt
        def gpu():
            return gputool.gpustatus_2(self.gpu_device)+"\n"

           # self.gpustatus_2()
        """




        @app.route('/metrics')
        @limiter.exempt
        def metrics():
            #a 是ai服务的基本信息
            a='#Server information\n' \
              '#server: {}\n' \
              '#aimodel: {}\n' \
              '#version: {}\n' \
              '#pro_ver: {}\n' \
              '#max_qps_s {}\n' \
              '#max_qps_5s {}\n' \
              .format(self.group_name,
                       self.models_str.replace('#','_'),
                       self.version,
                       self.pro_ver,
                       str(self.my_s_limiter),
                       str(self.my_5s_limiter)
                      )
            dic = health()
            o_counter = self.myaigroup.overload_counter

            keys =o_counter.keys()

            if dic['health'] =='ok':

                h_statu= 1
            else:
                h_statu = 0
            #b是简况检查结果
            b = '#check one image on all models for testint health\nai_health {}\n' \
                'ai_one_request_duration_seconds {}\n'.format(h_statu, dic['speed'])



            #c 是超过qps限额的信息
            c = "#up qpscounter\n"
            c=c+"up_qps_total {}\n".format(str(self.qps_counter))
            #========= no gpu =====================================
            #d 是gpu信息 [这个模型不需要GPU信息]
            #d = "#gpu status\n{}\n".format(gputool.gpustatus_1(self.gpu_device))

            #e是核心ai接口信息
            # ovsm 是总overload次数
            ovsm = 0
            ee=""
            for key in keys:
                ee = ee + "{}_model_overload_total {}\n".format(key, str(o_counter[key]))
                ovsm = ovsm + o_counter[key]
            #e= prometheus_client.generate_latest(self.requests_total).decode('utf-8')
            #main_counter是系统技术器，记录实际调用所有模型 predict方法的次数
            if self.main_counter == 0:
                overload_ratio = 0
            else:
                overload_ratio = round((ovsm/self.main_counter), 4)
            e= "#core ai interface request times\n" \
               "request_access_ai_total {}\n" \
               "request_not_overload_total {}\n" \
               "request_overload_ratio {}\n".\
                format(self.main_counter,(self.main_counter-ovsm),overload_ratio)


            e = e + "server_overload_total {}\n".format(ovsm)
            e = e+ee


            f= "#ai server start time: {}\n".format(self.start_time)

            return Response("{}{}{}{}{}".format(a,b,c,e,f), mimetype="text/plain")

        @app.route('/manage', methods=['POST'])
        @limiter.exempt
        def mamage_word():

            #这里会有中文问题，要解决掉==============================
            try:
                word = urllib.request.unquote(request.form.get('word'))
                todo = urllib.request.unquote(request.form.get('todo'))
                if todo =="change" or todo =="increase":
                    kindnum = urllib.request.unquote(request.form.get('kindnum'))
                else:
                    kindnum = 0

            except (Exception) :
                dic = {}
                dic['todo'] = todo
                dic['code'] = '-2'
                return Response(json.dumps(dic), mimetype='application/json')
            ret = myaigroup.manage_word(todo, word, kindnum)
            dic = {}
            dic['todo'] = todo
            dic['code'] = ret
            return Response(json.dumps(dic), mimetype='application/json')

        @app.route('/allwords')
        @limiter.exempt
        def allwords():
            password = request.args.get('pass')
            if password =='ilovehmaiproject':
                return myaigroup.allwords()
            else:
                return "你好， 欢迎关注 hmai ！"



        @app.route('/ai', methods=['POST'])
        # 自定义限制器覆盖了默认限制器,参数说明如下:
        # 1. param limit_value: 访问限制阈值
        # 2. param error_message: 错误的返回信息(注意,暂不支持中文,如果使用中文,请自定义错误页)
        # 3. param methods: 对哪些方法启用限制器?
        @limiter.limit("{}/second".format(self.my_s_limiter))
        @limiter.limit("{}/5seconds".format(self.my_5s_limiter))
        def get_tasks():

            self.main_counter = self.main_counter+1
            #====== 校验 aigroup 参数传点
            try:
                group=urllib.request.unquote(request.form.get('aigroup'))
                if group != self.group_name:
                    ret = make_error(self.models_str, 'aigroup', 'aigroup error：{}'.format(group))
                    ret.update({"pro_ver": "{}".format(self.pro_ver)})
                    return Response(json.dumps(ret), mimetype='application/json')

            except:
                ret = make_error(self.models_str, 'aigroup', 'no aigroup')
                ret.update({"pro_ver": "{}".format(self.pro_ver)})
                return Response(json.dumps(ret), mimetype='application/json')

            #==== 校验addition_info_in_place_ai参数，只有place模型需要使用这个参数
            try:

                req_addition_info_in_place_ai = urllib.request.unquote(request.form.get('addition_info_in_place_ai'))

                if req_addition_info_in_place_ai != 'y':
                    req_addition_info_in_place_ai = False
                else:
                    req_addition_info_in_place_ai = True
            except:
                req_addition_info_in_place_ai = False
            #==== 校验debug参数，开debug，回回传picid
            try:
                req_debug = urllib.request.unquote(request.form.get('debug'))
                if req_debug != 'y':
                    req_debug = False
                else:
                    req_debug = True
            except:
                req_debug = False
            # === 校验 loc参数，是否显示坐标，flags， face模型使用该参数
            try:
                req_loc = urllib.request.unquote(request.form.get('loc'))
                if req_loc != 'y':
                    req_loc = False
                else:
                    req_loc = True
            except:
                req_loc = False
            #=================================================================================
            #=== 校验附加参数1, 如果没有传入，则默认值 0
            try:
                req_add_var_1 = urllib.request.unquote(request.form.get('add_var_1'))
                if req_add_var_1 != '0':
                    pass
                else:
                    req_add_var_1 = '0'
            except:
                req_add_var_1 = '0'

            #=== 校验附加参数2, 如果没有传入，则默认值 0
            try:
                req_add_var_2 = urllib.request.unquote(request.form.get('add_var_2'))
                if req_add_var_2 != '0':
                    pass
                else:
                    req_add_var_2 = '0'
            except:
                req_add_var_2 = '0'

            #=== 校验附加参数3, 如果没有传入，则默认值 0
            try:
                req_add_var_3 = urllib.request.unquote(request.form.get('add_var_3'))
                if req_add_var_3 != '0':
                    pass
                else:
                    req_add_var_3 = '0'
            except:
                req_add_var_3 = '0'
            # =================================================================================



            # === 校验fr参数，默认f,代表fpr优先策略，如果是r,代表recall优先
            try:

                req_fr = urllib.request.unquote(request.form.get('fr'))

                if req_fr != 'r':
                    req_fr = 'f'
                else:
                    req_fr = 'r'
            except:
                req_fr = 'f'


            try:

                image_data = None
                try:
                    # 获取文字数据

                    image_data = urllib.request.unquote((request.form.get('textdata')))

                except Exception:
                    # print('ba64 exp')
                    image_data = None

                #if image_data == None:
                    #req_imgurl = urllib.request.unquote(request.form.get('imgurl'))

                req_ais_str = urllib.request.unquote(request.form.get('ais'))

                if req_ais_str != 'ALL_GROUP':
                    req_ais = req_ais_str.split('#')
                    ais_ok = True
                    ais_num = len(req_ais)
                    if ais_num <1:
                        ais_ok = False
                    for i in range(0,ais_num):
                        if req_ais[i] not in self.ai_group_list:
                            ais_ok = False
                            break

                    if ais_ok != True:
                        ret = make_error(self.models_str, 'ainame', '{} bad ais parameter '.format(req_ais_str))
                        ret.update({"pro_ver": "{}".format(self.pro_ver)})
                        self.disulog.error(ret)
                        return Response(json.dumps(ret), mimetype='application/json')

                else:
                    req_ais = self.ai_group_list

            except (Exception) :
                exstr = traceback.format_exc()
                print(exstr)
                # result={'error':'001 : param error'}
                ret = make_error(self.models_str, 'imgdata', exstr+'fail fot geting image from data')
                ret.update({"pro_ver": "{}".format(self.pro_ver)})
                self.disulog.error(ret)
                return Response(json.dumps(ret), mimetype='application/json')

            if image_data == None:
                ret = make_error(self.models_str, 'textdata',  'empty!')
                ret.update({"pro_ver": "{}".format(self.pro_ver)})
                self.disulog.error(ret)
                return Response(json.dumps(ret), mimetype='application/json')

            try:


                if len(req_ais) <= 0:
                    ret = make_error(self.ai_group_list, 'ainame', 'no req ai name')
                    ret.update({'pro_ver': self.pro_ver})
                    return Response(json.dumps(ret), mimetype='application/json')
                add_var_1 = int(req_add_var_1)
                add_var_2 = int(req_add_var_2)
                add_var_3 = int(req_add_var_3)
                result_1 = myaigroup.doais(image_data, req_ais,
                                           needLocation=req_loc,
                                           placeai_addition=req_addition_info_in_place_ai,
                                           fr=req_fr,
                                           add_var_1 = add_var_1,
                                           add_var_2 = add_var_2,
                                           add_var_3 = add_var_3
                                           )

                result = {}

                result['result'] = result_1
                result.update({"pro_ver": "{}".format(self.pro_ver)})
                if req_debug:
                    result.update({"picid": "{}".format(urllib.request.unquote(request.form.get('picid')))})

                return Response(json.dumps(result), mimetype='application/json')


            except (Exception) as e:
                exstr = traceback.format_exc()
                self.disulog.error(exstr)
                return '{}'

        try:
            if self.firstTime:
                dic = health()
                dic = health()
                self.firstTime = False
            else:
                dic = health()

            print('   启动检查结果：{}, 单次处理时间：{}秒'.format(dic['health'], dic['speed']))

        except Exception:
            exstr = traceback.format_exc()
            self.disulog.error(exstr)
            print ('   启动检查结果：失败')

        return app


