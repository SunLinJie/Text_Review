# -*- coding: utf-8 -*-
import hmai.hmai_gate_nlp as aigate

import hmai.hmai_group_nlp as aigroup
#import hmai.hmai_group_m as aigroup_m
import time
#import tools.gputool as gputool


def main():
    gate = aigate.AI_gate()
    # host = os.getenv('HOST', '0.0.0.0')
    # port = os.getenv('PORT', 5000)
    # ai 服务ip
    HOST = "0.0.0.0"
    # ai 服务端口
    PORT = gate.default_port

    #if gate.gpu_device == -1:
        #print("min_GPU_memery:{}, no gup to use!".format(gate.min_gpu_mem))
        #return exit(0)

    myaigroup = aigroup.AiGroup(gate.ai_group_list, gate.disulog)

    gate.set_group(myaigroup)

    startTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print("")
    print("   ------------------------------- ")
    print("   |          HAIMA AI         | ")
    print("   ------------------------------- ")
    print("   {} Starting at:{}".format(gate.group_name, startTime))
    print("   Aimodel:{}, Version:{}".format(gate.models_str, gate.version))
    print("   Max_s_qps:{}/second ".format(gate.my_s_limiter))
    print("   Max_5s_qps:{}/5second ".format(gate.my_5s_limiter))
    print("   AI server protocols version:{}".format(gate.pro_ver))
    #print(gputool.gpustatus_2(gate.gpu_device))
    print(" \n")

    gate.disulog.info("{} server starting at:{}".format(gate.group_name, startTime))

    # make web aii
    app = gate.make_app(myaigroup)
    # 启动 web api
    app.run(host=HOST, port=PORT)



if __name__ == '__main__':

    main()
