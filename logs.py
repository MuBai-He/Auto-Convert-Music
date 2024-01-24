import logging
import os
import time

class LogsBase():

    def __init__(self,name):
        # 控制台日志
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        
        # 日志配置
        root_dir=os.path.dirname(os.path.abspath(__file__))
        log_dir=os.path.join(root_dir,"logs")
        if not os.path.exists(log_dir):
           os.mkdir(log_dir)

        self.my_logging = logging.getLogger(name)#创建日志收集器
        self.my_logging.setLevel('DEBUG')#设置日志收集级别
        ch = logging.StreamHandler()#输出到控制台
        self.my_logging.setLevel('INFO')#设置日志输出级别
        self.my_logging.addHandler(ch)#对接，添加渠道

        #创建文件处理器fh，log_file为日志存放的文件夹
        log_file=os.path.join(log_dir,"{}_log.txt".format(time.strftime("%Y-%m-%d",time.localtime())))
        fh = logging.FileHandler(log_file,encoding="UTF-8")
        fh.setLevel('INFO')#设置日志输出级别
        self.my_logging.addHandler(fh)#对接，添加渠道

        #指定输出的格式
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(name)s 日志信息:%(message)s')
        #规定日志输出的时候按照formatter格式来打印
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
    
    def debug(self, message):
        self.my_logging.debug(message)
    
    def info(self, message):
        self.my_logging.info(message)
    
    def warning(self, message):
        self.my_logging.warning(message)
    
    def error(self, message):
        self.my_logging.error(message)