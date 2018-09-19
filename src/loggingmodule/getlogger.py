import logging
from logging.handlers import RotatingFileHandler
import time
class GetLogger():
    def __init__(self,name=None ,logfileloc=None, debuglevel=None):
        if name== None and logfileloc ==None :
            raise  Exception("Expected parameter: name, loffileloc and optional parameter debuglevel ")
        if debuglevel==None:
            debuglevel = 2
        self.name = name
        self.logfileloc = logfileloc
        self.debuglevel = debuglevel
        self.logger=None
    def getlogger(self):
        self.logger = logging.getLogger(self.name)
        if self.debuglevel==0:
            self.logger.setLevel(logging.DEBUG)
        if self.debuglevel == 1:
            self.logger.setLevel(logging.INFO)
        if self.debuglevel == 2:
            self.logger.setLevel(logging.ERROR)
        handler = logging.handlers.RotatingFileHandler(self.logfileloc, maxBytes=200000000, backupCount=100)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

        loggerobj = self.logger
        return loggerobj

    def getlogger1(self):
        if self.logger==None:
            self.logger=logging.getLogger(self.name)
            self.logger.setLevel(logging.DEBUG)
            formatter_=logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s',"%Y-%m-%d %H:%M:%S")
            formatter_.converter=time.gmtime
            if self.debuglevel == 0:
                handler=logging.NullHandler()
            elif self.debuglevel == 1:
                try:
                    handler=RotatingFileHandler(self.logfileloc,mode='a',maxBytes=5*1024*1024,backupCount=2,encoding=None,delay=0)
                    handler.setLevel(logging.ERROR)
                except Exception as e:
                    self.logger.error("Exception while creating handler in debug level 1"+str(e))
            elif self.debuglevel == 2:
                try:
                    handler=RotatingFileHandler(self.logfileloc,mode='a',maxBytes=5*1024*1024,backupCount=2,encoding=None,delay=0)
                    # handler.setLevel(logging.INFO)
                    handler.setLevel(logging.DEBUG)
                    # handler.setLevel(logging.ERROR)
                except Exception as e:
                    self.logger.error("Exception while creating handler in debug level 1"+str(e))
            handler.setFormatter(formatter_)
            self.logger.addHandler(handler)
        loggerobj=self.logger
        return loggerobj
if __name__=="__main__":
    obj = GetLogger("prashant","../../logs/mylog.log",0)
    logger = obj.getlogger()
    logger.error("hi")