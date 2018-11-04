#  -*- coding:utf-8 -*-
'''
Created on 2017年4月25日

@author: fub
'''

from src.apr.checkApr import CheckApr
import threading
beta="betaB"
checkapr=CheckApr()
_cookie=checkapr.getCookie()
#初始化数据库,每个环境只需在第一次使用时执行
#checkapr.initDB(beta)
threads = []
t1 = threading.Thread(target=checkapr.allotCheck,args=(beta,_cookie,))
threads.append(t1)
t2 = threading.Thread(target=checkapr.qualityCheck,args=(beta,_cookie,))
threads.append(t2)
if __name__ == '__main__':
    #我的任务和贷款审批质检,默认两个任务一起
    for t in threads:
        t.setDaemon(True)
        t.start()
    t.join()
    #贷款审批质检
    #checkapr.qualityCheck(beta, _cookie)
    #我的任务
    #checkapr.allotCheck(beta, _cookie)

    