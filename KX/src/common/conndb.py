#  -*- coding:utf-8 -*-
'''
Created on 2016年10月21日

@author: fub
'''
import MySQLdb
import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
import cx_Oracle

class Conndb():
    '''
    classdocs
    '''

    def __init__(self,host,user,passwd,db,port):
        

        self.host=host
        self.user=user
        self.passwd=passwd
        self.db=db
        self.port=port 
        
    def connMysql(self):
        try:
            conndb=MySQLdb.Connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db,port=self.port)
            cur=conndb.cursor()
            
            return cur
        except MySQLdb.Error,e:
            print (e.args[0], e.args[1])
            
    def connOra(self):

        tns=cx_Oracle.makedsn(self.host,self.port,self.db)
        conn=cx_Oracle.connect(self.user,self.passwd,tns)
        #conn = cx_Oracle.connect(self.user+'/'+self.passwd+'@'+self.host+'/'+self.db)
        cursor = conn.cursor()
        
        return cursor,conn
    
    def fetch_one_ora(self,sql):
        
        (cursor,conn)=self.connOra()
        cursor.execute(sql)
        conn.commit()
        
        result=cursor.fetchone()
        cursor.close ()  
        conn.close () 
        
        return result
    
    def fetch_all_ora(self,sql):
        
        (cursor,conn)=self.connOra()
        cursor.execute(sql)
        conn.commit()
        
        result=cursor.fetchall()
        
        cursor.close ()  
        conn.close () 
        
        return result
    
    def update(self):
        pass
    
    def deleteOra(self,sql):
        (cursor,conn)=self.connOra()
        cursor.execute(sql)
        conn.commit()
    
    def fetch_one(self, sql):

        cur=self.conn()
        cur.execute(sql)
        result=cur.fetchone()
    
        return result
    def fetch_all(self,sql):
        
        cur=self.conn()
        cur.execute(sql)
        result=cur.fetchall()

        return result
    
    def commit(self,conndb):
        
        conndb.close
        conndb.close