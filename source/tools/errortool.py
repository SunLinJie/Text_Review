import time
def make_error(models, error_label,mes):
    errors =['imgdata','exception','imgurl', 'ainame','up_qps','overload','aigroup','textdata']
    if error_label in(errors):
        ret = {}
        lists = []
        mes_ = "{} at {} ".format(mes,time.strftime('%Y-%m-%d-%H:%M:%S',time.localtime(time.time())))
        er = {'code': '-1', 'mr': [], 'model': models, 'error': error_label, 'error_mes':mes_}
        lists.append(er)
        ret['result'] = lists
        return ret
    else:
        print('bad error_label: {}'.format(error_label))
        return None