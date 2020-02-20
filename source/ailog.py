#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
该日志类可以把不同级别的日志输出到不同的日志文件中
'''

import os
#cimport sys
import time
import logging
import inspect

import logging.handlers



handlers = {logging.NOTSET:"./log/ai-notset.log",
            logging.DEBUG:"./log/ai-debug.log",
            logging.INFO:"./log/ai-info.log",
            logging.WARNING:"./log/ai-warning.log",
            logging.ERROR:"./log/ai-error.log",
            logging.CRITICAL:"./log/ai-critical.log"
            }


def createHandlers():
    logLevels = handlers.keys()
    for level in logLevels:
        path = os.path.abspath(handlers[level])
        #handlers[level] = logging.FileHandler(path)
        handlers[level] = logging.handlers.TimedRotatingFileHandler(path, when='H', interval=1, backupCount=120, encoding= "utf8")



#加载模块时创建全局变量
createHandlers()

class AILog(object):
    def printfNow(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    
    def __init__(self,level=logging.NOTSET):
        #file_hanlder = logging.FileHandler(filename='example.log', encoding='utf-8')
        self.__loggers = {}
        logLevels = handlers.keys()
        for level in logLevels:
            logger = logging.getLogger(str(level))
            #如果不指定level，获得的handler似乎是同一个handler?
            logger.addHandler(handlers[level])
            logger.setLevel(level)
            self.__loggers.update({level:logger})

    def getLogMessage(self,level,message):
        frame,filename,lineNo,functionName,code,unknowField = inspect.stack()[2]
        '''日志格式：[时间] [类型] [记录代码] 信息'''
        return "[%s] [%s] [%s - %s ] %s" %(self.printfNow(),level,filename,lineNo,message)
    
    def info(self,message):
        message = self.getLogMessage("info",message)
        self.__loggers[logging.INFO].info(message)
    
    def error(self,message):
        message = self.getLogMessage("error",message)
        self.__loggers[logging.ERROR].error(message)
    
    def warning(self,message):
        message = self.getLogMessage("warning",message)
        self.__loggers[logging.WARNING].warning(message)

    
    def debug(self,message):
        message = self.getLogMessage("debug",message)
        self.__loggers[logging.DEBUG].debug(message)

    
    def critical(self,message):
        message = self.getLogMessage("critical",message)
        self.__loggers[logging.CRITICAL].critical(message)

if __name__ == "__main__":
    logger = AILog()
    logger.debug("debug")
    #logger = TNLog()
    logger.info("info")
    #logger = TNLog()
    logger.warning("warning")
    #logger = TNLog()
    logger.error("error 错误")
    #logger = TNLog()
    logger.critical("critical")