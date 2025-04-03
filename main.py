#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  5 09:05:20 2025

@author: oh
"""
'''
파이썬 크롤러 제작
    yfinance 를 호출하여 데이터를 수집하고 가공하여,
    MYSQL 서버로 데이터를 저장하는 역할.

df = fdr.StockListing("KRX") # NASDAQ
df = fdr.DataReader('AAPL', '2022')
stock = yf.download(종목코드, start = 시작날짜, end = 종료날짜)

작업 순서
1. 파이썬 패키지 임포트
2. MYSQL 접속 정보
3. 실제 주식 데이터를 가져오는 함수 생성 getStock() <= getCompany() 에서 호출
    데이터 가공 및 MYSQL 에 저장
4. 크롤링 할 기업의 목록을 데이터베이스로 읽어오는 함수 생성 getCompany()
5. 파일을 실행할 때 처음 실행되는 코드 if __name__ == '__main__'
'''

# 1. 파이썬 패키지 임포트
from datetime import datetime, timedelta
import pymysql
import yfinance as yf

# 2. MYSQL 접속 정보
hostName = "Localhost"
userName = "root"
password = "0301"
dbName = "us_stock"

mysql_conn = pymysql.connect(host = hostName,
                             user = userName,
                             password = password,
                             db = dbName)

# 3. 실제 주식 데이터를 가져오는 함수 생성 getStock(종목코드, 시작날짜, 종료날짜) <=
# getCompany() 에서 호출, 데이터 가공 및 MYSQL 에 저장

def getStock(_symbol, _start_date, _end_date):
    
    mysql_cur = mysql_conn.cursor()
    
    # 크롤링하려는 날짜의 데이터가 존재하면 삭제
    mysql_cur.execute("delete from us_stock.stock where date >= %s and date <= %s and symbol = %s",
                      (_start_date, _end_date, _symbol))
    mysql_conn.commit()

    # yf.download 함수를 통해 주식 데이터를 가져와 stock_price 변수에 저장
    try:
        stock_price = yf.download(_symbol, start = _start_date, end = _end_date)
        print(stock_price)
        
        # 데이터프레임 형태의 데이터를 각 변수에 저장
        for index, row in stock_price.iterrows():
            print('s3' * 20)
            _date = index.strftime("%Y-%m-%d")
            _open = float(row["Open"])
            _high = float(row["High"])
            _low = float(row["Low"])
            _close = float(row["Close"])
            _adj_close = float(101309500)
            print('s4' * 20)
            _volume = float(row["Volume"])
            
            # stock 테이블에 크롤링한 데이터를 입력
            mysql_cur.execute("insert into us_stock.stock (date, symbol, open, high, low, close, adj_close, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                                          (_date, _symbol, _open, _high, _low, _close, _adj_close, _volume))
            print('s5' * 20)
        mysql_conn.commit()
        
        # 크롤링한 데이터의 마지막 날짜를 기록
        mysql_cur.execute("update us_stock.nasdaq_company set open = %s, high = %s, low = %s, close = %s, adj_close = %s, volume = %s, last_crawel_date_stock = %s where symbol = %s", 
                                  (_open, _high, _low, _close, _adj_close, _volume, _date, _symbol))
        print('s6' * 20)
        mysql_conn.commit()
        
    # 오류를 출력하고 로직 종료
    except Exception as e:
        print("error for getStock() : " + str(e))
        mysql_conn.commit()
        mysql_conn.close()
        
        return {"error for getStock() " : str(e)}
#--------------------------------------------------------
# 4. 크롤링 할 기업의 목록을 데이터베이스로 읽어오는 함수 생성 getCompany()

def getCompany():
    
    # mysql 커서 실행
    mysql_cur = mysql_conn.cursor()
    
    # 수집할 주식 데이터의 날짜를 정의
    today = datetime.today() + timedelta(days = 1)
    
    # 기업 목록을 가져오는 쿼리를 호출
    try:
        mysql_cur.execute("select symbol, company_name, ipo_year, last_crawel_date_stock from us_stock.nasdaq_company where is_delete is null;")
        results = mysql_cur.fetchall()
        print(results)
        
        # 크롤링한 데이터를 목적에 맞는 변수에 데이터를 할당한다. 이때 변수에 할당할 데이터가 존재하지 않으면 else 문이 실행되어 별도의 데이터가 할당된다.
        for row in results:
            _symbol = row[0]
            _company_name = row[1]
            
            if row[2] is None or row[2] == 0:
                _ipo_year = '1970'
            else:
                _ipo_year = row[2]
                
            if row[3] is None:
                _last_crawel_date_stock = str(_ipo_year) + "-01-01"
            else:
                _last_crawel_date_stock = row[3]
                
            print(_symbol)
            if "." in _symbol:
                print(_symbol)
            else:
                if "/" in _symbol:
                    print(_symbol)
                else:
                    getStock(_symbol, _last_crawel_date_stock,
                             today.strftime("%Y-%m-%d"))
    
    # 오류를 출력하고 로직 종료
    except Exception as e:
        print("error for getCompany() : " + str(e))
        mysql_conn.commit()
        mysql_conn.close()
        
        return {"error for getCompany() " : str(e)}
#--------------------------------------
# 5.
if __name__ == "__main__":
    getCompany()
































