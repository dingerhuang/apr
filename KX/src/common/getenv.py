#  -*- coding:utf-8 -*-
'''
Created on 2017年4月26日

@author: fub
'''
import ConfigParser

class GetEnv():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.cf = ConfigParser.ConfigParser()
        self.cf.read("E:\\workspace\\KX\\src\\config\\env.conf")
        
        self.bodycf=ConfigParser.ConfigParser()
        self.bodycf.read("E:\\workspace\\KX\\src\\config\\body.conf")
        
        self.sqlcf=ConfigParser.ConfigParser()
        self.sqlcf.read("E:\\workspace\\KX\\src\\config\\sql.conf")
    
    def getOracleIp(self,beta):
        oracleIp=self.cf.get(beta, 'oracleIp')
 
        return oracleIp
    
    def getMysqlPort(self,beta):
        mysqlPort=self.cf.get(beta, 'mysqlPort')
 
        return mysqlPort
    
    def getOraclePort(self,beta):
        oraclePort=self.cf.get(beta, 'oraclePort')
 
        return oraclePort
    
    def getOracleUser(self,beta):
        oracleUser=self.cf.get(beta, 'oracleUser')
 
        return oracleUser
    
    def getOraclePasswd(self,beta):
        oraclePasswd=self.cf.get(beta, 'oraclePasswd')
 
        return oraclePasswd
    
    def getOracleDbName(self,beta):
        oracleDbName=self.cf.get(beta, 'oracleDbName')
 
        return oracleDbName
    
    def getMysqlIp(self,beta):
        myslqIp=self.cf.get(beta, 'mysqlIp')
 
        return myslqIp
    
    def getMysqlUser(self,beta):
        mysqlUser=self.cf.get(beta, 'mysqlUser')
 
        return mysqlUser
    
    def getMysqlPasswd(self,beta):
        mysqlPasswd=self.cf.get(beta, 'mysqlPasswd')
 
        return mysqlPasswd
    
    def getMysqlDbName(self,beta):
        myslqDbName=self.cf.get(beta, 'myslqDbName')
 
        return myslqDbName
    
    def getMethod(self,beta):
        method=self.cf.get(beta, 'method')
        
        return method

    def getUrl(self,beta):
        url=self.cf.get(beta, 'postUrl')
        
        return url
    
    def getHeader(self,beta):
        headers=self.cf.get(beta, 'headers')
        
        return headers
    
    def getMytaskBody(self,sec):
        body1=self.bodycf.get(sec, 'body1')
        body2=self.bodycf.get(sec, 'body2')
        
        return body1,body2
    
    def getSql(self,sec):
        sql=self.sqlcf.get(sec, 'sql')
        
        return sql
    