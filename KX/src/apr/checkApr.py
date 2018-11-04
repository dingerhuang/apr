#  -*- coding:utf-8 -*-
'''
Created on 2017年4月25日

@author: fub
'''
from selenium import webdriver
from src.common.getenv import GetEnv
from src.common.conndb import Conndb
import requests,re,time

class CheckApr():
    '''
    rect13   pos贷家庭岗
    rect12   pos贷单位岗
    rect122    sale现金贷单位电核岗
    rect123   sale 现金贷本人岗
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.env=GetEnv()
        self.reject_flag={}

    #测试过程中，手动修改数据库，导入线上数据等操作，会导致回去不到节点或者节点锁住
    def initDB(self,beta):
        sql=self.env.getSql("initSql1")
        self.executeOraDml(beta, sql)
        sql=self.env.getSql("initSql2")
        self.executeOraDml(beta, sql)
        sql=self.env.getSql("initSql3")
        self.executeOraDml(beta, sql)
        sql=self.env.getSql("initSql4")
        self.executeOraDml(beta, sql)
    #获取cookie
    def getCookie(self):
        #driver=webdriver.Firefox(executable_path = 'D:\\tools\\geckodriver\\geckodriver')
        driver=webdriver.Firefox()
        driver.get("http://10.40.10.150:8091/apr/login")
        driver.maximize_window()
        
        code=driver.find_element_by_xpath('//*[@id="loginFrom"]/table/tbody/tr/td/table/tbody/tr[3]/td[2]/img').get_attribute("src")
        code=code.split('=')[1]
        driver.find_element_by_xpath('//*[@id="username"]').send_keys('19200018')
        driver.find_element_by_xpath('//*[@id="password"]').send_keys('@test123')
        driver.find_element_by_xpath('//*[@id="random"]').send_keys(code)
        driver.find_element_by_xpath('//*[@id="loginFrom"]/table/tbody/tr/td/table/tbody/tr[4]/td/div/input').click()
        _cookie=driver.get_cookies()
        
        return _cookie[0]['value']
        
    #获取taskNo
    def getTaskNo(self):
        taskNo=""
        
        return taskNo
    
    #获取taskKey
    def getTaskKey(self):
        taskKey=""
        
        return taskKey
    #贷款审批质检
    def qualityCheck(self,beta,_cookie):
        print "贷款审批质检开始！"
        if self.getOraDatas(beta,"QCsql"):
            datas=self.getOraDatas(beta,"QCsql")
            for each_row in datas:
                busiKey=each_row[0]
                taskNo=each_row[1]
                taskKey=each_row[2]
                rect_name=each_row[3]
                chanSource=each_row[4]
                dict_remark={}
                dict_remark['busiKey']=busiKey
                dict_remark['taskNo']=taskNo
                dict_remark['taskKey']=taskKey
                remark=self.getOraDatas(beta,"remarksql",busiKey)[0][0]
                dict_remark['remark']=remark
                dict_remark['chanSource']=chanSource
                if rect_name == "rect122":
                    self.check_nodes(beta,_cookie,'auto_cash_work','body_question',dict_remark)
                    self.check_nodes(beta,_cookie,'auto_cash_work','body_check',dict_remark)
                    
                    print "合同号："+busiKey+"的"+rect_name+"节点质检通过！"
                elif rect_name == "rect123":
                    self.check_nodes(beta,_cookie,'auto_cash_self','body_question',dict_remark)
                    self.check_nodes(beta,_cookie,'auto_cash_self','body_check',dict_remark)
                    
                    print "合同号："+busiKey+"的"+rect_name+"节点质检通过！"
                elif rect_name == "rect125":
                    self.check_nodes(beta,_cookie,'auto_cash_info','body_question',dict_remark)
                    self.check_nodes(beta,_cookie,'auto_cash_info','body_check',dict_remark)
                    
                    print "合同号："+busiKey+"的"+rect_name+"节点质检通过！"
                elif rect_name == "rect126":
                    self.check_nodes(beta,_cookie,'auto_cash_family','body_question',dict_remark)
                    self.check_nodes(beta,_cookie,'auto_cash_family','body_check',dict_remark)
                    
                    print "合同号："+busiKey+"的"+rect_name+"节点质检通过！"
                elif rect_name == "rect33":
                    if not self.reject_flag.has_key(busiKey):
                        if re.match("rect-",remark):
                            self.check_nodes(beta,_cookie,'auto_cash_end_reject','body_check',dict_remark)
                            self.reject_flag[busiKey]='1'
                        elif remark == "notpass":
                            self.check_nodes(beta,_cookie,'auto_cash_end_notpass','body_check',dict_remark)
                        elif re.match('rect:',remark):
                            self.check_nodes(beta,_cookie,'auto_cash_end_reject_amount','body_check',dict_remark)
                        else:
                            self.check_nodes(beta,_cookie,'auto_cash_end','body_check',dict_remark)
                    else:
                        print "工单"+busiKey+"已经驳回，现进行通过处理！" 
                        self.check_nodes(beta,_cookie,'auto_cash_end','body_check',dict_remark) 
                        
                    print "合同号："+busiKey+"的"+rect_name+"节点质检通过！" 
                else:
                    print "节点："+rect_name+"不存在！"
                    
                    return "0"
        else:
            time.sleep(6)
            self.qualityCheck(beta,_cookie)
            
        self.qualityCheck(beta,_cookie)  
                
    #发送请求
    def sendReq(self,method,url,bodys,headers,_cookie):
        #格式转换字典、json
        headers=eval(headers)
        headers['Cookie']='JSESSIONID='+_cookie
        #bodys = json.dumps(bodys)
        _cookies=''
        try:
            if method=="post":
                response=requests.post(url,bodys,cookies=_cookies,headers=headers)    
            else:
                response=requests.get(url,bodys,headers=headers)
                
        except Exception,error:
            print error
            
        return response.status_code
    
    #替换body参数
    def packageBody(self,beta,section,option,*dict_remark):
        #bodys=re.sub('kxtest',reg,bodys)
        print dict_remark
        if dict_remark:
            dict_remark=eval(max(re.split('\(|,\)',str(dict_remark))))
        method=self.env.getMethod(beta)
        url=self.env.getUrl(beta)
        headers=self.env.bodycf.get(section, 'headers')
        bodys=self.env.bodycf.get(section, option)
        if re.search('busiKey',self.env.bodycf.get(section, option)):
            src_busiKey=self.env.bodycf.get(section, option).split('&busiKey=')[1].split('&')[0]
            busiKey=dict_remark['busiKey']
            bodys=bodys.replace(src_busiKey,busiKey)
        if re.search('taskNo',self.env.bodycf.get(section, option)):
            src_taskNo=self.env.bodycf.get(section, option).split('&taskNo=')[1].split('&')[0]
            taskNo=dict_remark['taskNo']
            bodys=bodys.replace(src_taskNo,taskNo)
        if re.search('taskKey',self.env.bodycf.get(section, option)):
            src_taskKey=self.env.bodycf.get(section, option).split('&taskKey=')[1].split('&')[0]
            taskKey=dict_remark['taskKey']
            bodys=bodys.replace(src_taskKey,taskKey)
        #贷款审批质检时有chanSource
        if re.search('chanSource=',self.env.bodycf.get(section, option)):
            src_chanSource="chanSource="+dict_remark['chanSource']+"&"
            bodys=re.sub(r'chanSource=.*?&',src_chanSource,bodys)
        #兜想花进件remark为空
        if dict_remark['remark'] == None:
            pass
        elif re.match('rect-',dict_remark['remark']):
            new_node=str(dict_remark['remark'].split('-')[0])+str(dict_remark['remark'].split('-')[-1])
            if "rect_pos_node" in str(bodys):
                bodys=bodys.replace('rect_pos_node',new_node)
            else:
                bodys=bodys.replace('rect_cash_node',new_node)
        elif re.match('rect:',dict_remark['remark']):
            new_suggestLoanAmt=dict_remark['remark'].split(':')[-1]
            bodys=bodys.replace('reject_suggestLoanAmt',new_suggestLoanAmt)
        else:
            pass
            
        print section+":"+option+":taskNo:"+taskNo+"数据组装完成"
        
        return method,url,headers,bodys
    
    #我得任务
    def getTask(self,beta,_cookie):
        method=self.env.getMethod(beta)
        url=self.env.getUrl(beta)
        headers=self.env.getHeader(beta)
        (body1,body2)=self.env.getMytaskBody("mytask")
        
        self.sendReq(method, url, body1, headers,_cookie)
        self.sendReq(method, url, body2, headers,_cookie)
        time.sleep(5)
        print "get mytask success!"
    
    #oracle数据
    def getOraDatas(self,beta,sqlconf,*busiKey):
        if len(busiKey) > 1:
            print "参数错误"
        elif len(busiKey) == 1:
            sql=self.env.getSql(sqlconf)
            sql=sql.replace('loanno',str(busiKey[0]))
        else:
            sql=self.env.getSql(sqlconf)
        datas=self.getOracleData(beta, sql)
        
        return datas
    
    #岗位节点判断
    def allotCheck(self,beta,_cookie):
        #修改sql limit 1避免返回值为列表*********************************
        print "allot分单开始！"
        if self.getOraDatas(beta,"tasksql"):
            datas=self.getOraDatas(beta,"tasksql")
            for each_row in datas:
                busiKey=each_row[0]
                taskNo=each_row[1]
                taskKey=each_row[2]
                rect_name=each_row[3]
                dict_remark={}
                dict_remark['busiKey']=busiKey
                dict_remark['taskNo']=taskNo
                dict_remark['taskKey']=taskKey
                remark=self.getOraDatas(beta,"remarksql",busiKey)[0][0]
                dict_remark['remark']=remark
                if rect_name == "rect13":
                    #sale pos贷家庭岗
                    self.check_nodes(beta,_cookie,'sale_pos_family','body_question',dict_remark)
                    self.check_nodes(beta,_cookie,'sale_pos_family','body_check',dict_remark)
                    
                    print "合同号："+busiKey+"的"+rect_name+"节点审核通过！"
                elif rect_name == "rect12":
                    #sale pos贷单位岗
                    self.check_nodes(beta,_cookie,'sale_pos_work','body_question',dict_remark)
                    self.check_nodes(beta,_cookie,'sale_pos_work','body_check',dict_remark)
                    
                    print "合同号："+busiKey+"的"+rect_name+"节点审核通过！"
                elif rect_name == "rect29":
                    #sale 深圳家庭岗
                    self.check_nodes(beta,_cookie,'sale_pos_work_sz','body_question',dict_remark)
                    self.check_nodes(beta,_cookie,'sale_pos_work_sz','body_check',dict_remark)
                    
                    print "合同号："+busiKey+"的"+rect_name+"节点审核通过！"
                elif rect_name == "rect18":
                    #sale pos贷复核岗,判断是否已经驳回过
                    if not self.reject_flag.has_key(busiKey):
                        if re.match("rect-",remark):
                            self.check_nodes(beta,_cookie,'sale_pos_end_reject','body_check',dict_remark)
                            self.reject_flag[busiKey]='1'
                        elif remark == "notpass":
                            self.check_nodes(beta,_cookie,'sale_pos_end_notpass','body_check',dict_remark)
                        else:
                            self.check_nodes(beta,_cookie,'sale_pos_end','body_check',dict_remark)
                    else:
                        print "工单"+busiKey+"已经驳回，现进行通过处理！"
                        self.check_nodes(beta,_cookie,'sale_pos_end','body_check',dict_remark)
                                
                    print "合同号："+busiKey+"的"+rect_name+"节点审核通过！"
                elif rect_name == "rect122":
                    #sale 现金贷单位岗
                    self.check_nodes(beta,_cookie,'sale_cash_work','body_question',dict_remark)
                    self.check_nodes(beta,_cookie,'sale_cash_work','body_check',dict_remark)
                    
                    print "合同号："+busiKey+"的"+rect_name+"节点审核通过！"
                elif rect_name == "rect123":
                    #sale 现金贷本人岗
                    self.check_nodes(beta,_cookie,'sale_cash_self','body_question',dict_remark)
                    self.check_nodes(beta,_cookie,'sale_cash_self','body_check',dict_remark)
        
                    print "合同号："+busiKey+"的"+rect_name+"节点审核通过！"
                elif rect_name == "rect126":
                    #sale 现金贷家庭岗
                    self.check_nodes(beta,_cookie,'sale_cash_family','body_question',dict_remark)
                    self.check_nodes(beta,_cookie,'sale_cash_family','body_check',dict_remark)
                    
                    print "合同号："+busiKey+"的"+rect_name+"节点审核通过！"
                elif rect_name == "rect125":
                    #sale 现金贷资料岗
                    self.check_nodes(beta,_cookie,'sale_cash_info','body_question',dict_remark)
                    self.check_nodes(beta,_cookie,'sale_cash_info','body_check',dict_remark)
                    
                    print "合同号："+busiKey+"的"+rect_name+"节点审核通过！"
                elif rect_name == "rect33":
                    #sale 现金贷复核岗，复核岗需进行判断根据 t_cust_base_info.remark字段进行判断通过还是返修（内外）
                    #判断是否已经驳回过
                    if not self.reject_flag.has_key(busiKey):
                        if re.match("rect-",remark):
                            self.check_nodes(beta,_cookie,'sale_cash_end_reject','body_check',dict_remark)
                            self.reject_flag[busiKey]='1'
                        elif remark == "notpass":
                            self.check_nodes(beta,_cookie,'sale_cash_end_notpass','body_check',dict_remark)
                        elif re.match('rect:',remark):
                            chanSource=self.getOraDatas(beta,"chanSourcesql",busiKey)[0][0]
                            dict_remark['chanSource']=chanSource
                            self.check_nodes(beta,_cookie,'sale_cash_end_reject_amount','body_check',dict_remark)
                        else:
                            self.check_nodes(beta,_cookie,'sale_cash_end','body_check',dict_remark)
                    else:
                        print "工单"+busiKey+"已经驳回，现进行通过处理！" 
                        self.check_nodes(beta,_cookie,'sale_cash_end','body_check',dict_remark) 
                        
                    print "合同号："+busiKey+"的"+rect_name+"节点审核通过！"         
                elif rect_name == "rect94" or rect_name == "rect38":
                    #sale 医美复核岗38号节点为临时测试发现，若有问题，请加逻辑
                    if not self.reject_flag.has_key('busiKey'):
                        if remark == "rect-94":
                            self.check_nodes(beta,_cookie,'sale_hospital_end_rect','body_check',dict_remark)
                            self.reject_flag[busiKey]='1'
                        elif remark == "notpass":
                            self.check_nodes(beta,_cookie,'sale_hospital_end_notpass','body_check',dict_remark)
                        else:
                            self.check_nodes(beta,_cookie,'sale_hospital_end','body_check',dict_remark)
                    else:
                        print "工单"+busiKey+"已经驳回，现进行通过处理！" 
                        self.check_nodes(beta,_cookie,'sale_hospital_end','body_check',dict_remark)
                        
                    print "合同号："+busiKey+"的"+rect_name+"节点审核通过！"
                elif rect_name == "rect302":
                    #无预约现金贷
                    if not self.reject_flag.has_key('busiKey'):
                        if re.match("rect-",remark):
                            self.check_nodes(beta,_cookie,'wyy','body_check',dict_remark)
                            self.reject_flag[busiKey]='1'
                        elif re.match("notpass",remark):
                            self.check_nodes(beta,_cookie,'wyy_notpass','body_question',dict_remark)
                            self.check_nodes(beta,_cookie,'wyy_notpass','body_check',dict_remark)
                        elif re.match("rect:",remark):
                            self.check_nodes(beta,_cookie,'wyy_rect','body_question',dict_remark)
                            self.check_nodes(beta,_cookie,'wyy_rect','body_check',dict_remark)
                        else:
                            self.check_nodes(beta,_cookie,'wyy_end','body_question',dict_remark)
                            self.check_nodes(beta,_cookie,'wyy_end','body_check',dict_remark)
                    else:
                        print "工单"+busiKey+"已经驳回，现进行通过处理！" 
                        self.check_nodes(beta,_cookie,'wyy','body_check',dict_remark)
                        
                    print "合同号："+busiKey+"的"+rect_name+"节点审核通过！"
                #新增兜想花岗位节点、柠檬进件也是用此节点，没有驳回选项
                elif rect_name == "rect323":
                    self.check_nodes(beta,_cookie,'dxh_end','body_check',dict_remark)
                else:
                    print "节点:"+rect_name+"不存在！"
                    
                    return "0"
            self.getTask(beta, _cookie)
            self.allotCheck(beta, _cookie)
        else:
            self.getTask(beta, _cookie)
            self.allotCheck(beta, _cookie)

    #准备发送
    def check_nodes(self,beta,_cookie,section, option , *dict_remark):
        if len(dict_remark) > 1:
            print "参数错误"
        elif len(dict_remark) == 1:
            (method, url, bodys, headers)=self.packageBody(beta, section, option,dict_remark)
        else:
            #问卷调查时可以不传dict_remark
            (method, url, bodys, headers)=self.packageBody(beta, section, option)
            
        self.sendReq(method, url, headers, bodys,_cookie)
    
    #获取mysql数据
    def getMysqlData(self,beta):
        host=self.env.getMysqlIp(beta)
        user=self.env.getMysqlUser(beta)
        passwd=self.env.getMysqlPasswd(beta)
        dbName=self.env.getMysqlDbName(beta)
        port=self.env.getMysqlPort(beta)
        conn=Conndb(host,user,passwd,dbName,port)
        conn.conn()
    #执行DML语句,删除脏数据
    def executeOraDml(self,beta,sql):
        host=self.env.getOracleIp(beta)
        user=self.env.getOracleUser(beta)
        passwd=self.env.getOraclePasswd(beta)
        dbName=self.env.getOracleDbName(beta)
        port=self.env.getOraclePort(beta)
        conn=Conndb(host,user,passwd,dbName,port)
        
        conn.deleteOra(sql)
    #获取oracle数据    
    def getOracleData(self,beta,sql):
        host=self.env.getOracleIp(beta)
        user=self.env.getOracleUser(beta)
        passwd=self.env.getOraclePasswd(beta)
        dbName=self.env.getOracleDbName(beta)
        port=self.env.getOraclePort(beta)
        conn=Conndb(host,user,passwd,dbName,port)   

        data=conn.fetch_all_ora(sql)
        
        return data
    #贷款审批质检,单个合同,二期实现
    def qualityCheckLoanNB(self,beta,_cookie,loan_no):
        print "贷款审批质检合同号开始！"
        if self.getOraDatas(beta,"QCLoanNBsql"):
            datas=self.getOraDatas(beta,"QCLoanNBsql")
            for each_row in datas:
                busiKey=each_row[0]
                taskNo=each_row[1]
                taskKey=each_row[2]
                rect_name=each_row[3]
                chanSource=each_row[4]
                dict_remark={}
                dict_remark['busiKey']=busiKey
                dict_remark['taskNo']=taskNo
                dict_remark['taskKey']=taskKey
                remark=self.getOraDatas(beta,"remarksql",busiKey)[0][0]
                dict_remark['remark']=remark
                dict_remark['chanSource']=chanSource
                if rect_name == "rect122":
                    self.check_nodes(beta,_cookie,'auto_cash_work','body_question',dict_remark)
                    self.check_nodes(beta,_cookie,'auto_cash_work','body_check',dict_remark)
                    
                    print "合同号："+busiKey+"的"+rect_name+"节点质检通过！"
                elif rect_name == "rect123":
                    self.check_nodes(beta,_cookie,'auto_cash_self','body_question',dict_remark)
                    self.check_nodes(beta,_cookie,'auto_cash_self','body_check',dict_remark)
                    
                    print "合同号："+busiKey+"的"+rect_name+"节点质检通过！"
                elif rect_name == "rect125":
                    self.check_nodes(beta,_cookie,'auto_cash_info','body_question',dict_remark)
                    self.check_nodes(beta,_cookie,'auto_cash_info','body_check',dict_remark)
                    
                    print "合同号："+busiKey+"的"+rect_name+"节点质检通过！"
                elif rect_name == "rect126":
                    self.check_nodes(beta,_cookie,'auto_cash_family','body_question',dict_remark)
                    self.check_nodes(beta,_cookie,'auto_cash_family','body_check',dict_remark)
                    
                    print "合同号："+busiKey+"的"+rect_name+"节点质检通过！"
                elif rect_name == "rect33":
                    if not self.reject_flag.has_key(busiKey):
                        if re.match("rect-",remark):
                            self.check_nodes(beta,_cookie,'auto_cash_end_reject','body_check',dict_remark)
                            self.reject_flag[busiKey]='1'
                        elif remark == "notpass":
                            self.check_nodes(beta,_cookie,'auto_cash_end_notpass','body_check',dict_remark)
                        elif re.match('rect:',remark):
                            self.check_nodes(beta,_cookie,'auto_cash_end_reject_amount','body_check',dict_remark)
                        else:
                            self.check_nodes(beta,_cookie,'auto_cash_end','body_check',dict_remark)
                    else:
                        print "工单"+busiKey+"已经驳回，现进行通过处理！" 
                        self.check_nodes(beta,_cookie,'auto_cash_end','body_check',dict_remark) 
                        
                    print "合同号："+busiKey+"的"+rect_name+"节点质检通过！" 
                else:
                    print "节点："+rect_name+"不存在！"
                    
                    return "0"
        else:
            time.sleep(6)
            self.qualityCheck(beta,_cookie)
            
        self.qualityCheck(beta,_cookie)  
            