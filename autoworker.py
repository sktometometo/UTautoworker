#!/usr/bin/env python
# -*- coding:utf-8 -*-

from selenium import webdriver
from pyvirtualdisplay import Display
import os
import sys
import time
import csv
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate
import smtplib
import sched
import datetime
import threading

def debugprint( level, string_msg ):
    """
    標準出力へ時刻とメッセージを出力
    """
    level_list = [ "INFO", "WARNING", "ERROR", "DEBUG" ]
    if level in level_list:
        with open( filepath_log, "a" ) as f:
            print( str( datetime.datetime.now() ) + " : " + level + " : " + string_msg, file=f )

def readSchedule( filepath ):
    """
    各行のフォーマット
    曜日 ( 0-6 ), 開始時間 ( 24時間表示 hour ), 開始時間 ( minitus), 終了時間 ( 24時間表示 ), 終了時間 ( minites )
    """
    try:
        with open( filepath, "r" ) as f:
            list_schedule = []
            reader = csv.reader( f, delimiter="," )
            header = next(reader)
            for row in reader:
                list_schedule.append( [ \
                    int(row[0]), int(row[1]), int(row[2]), int(row[3]), int(row[4]) \
                ] )
        for schedule in list_schedule:
            debugprint( "INFO", "readSchedule(), schedule:" + str(schedule) )
        debugprint( "INFO", "readSchedule() succeeded" ) 
        return list_schedule
    except ( IndexError, ValueError ):
        debugprint( "ERROR", "readSchedule() failed. config file syntax error" )
    except:
        debugprint( "ERROR", "readSchedule() failed. Unexpected error." ) 
        raise

def readConfig( filepath ):
    """
    csv から 設定を読み込む
    """
    try:
        with open( filepath, "r" ) as f:
            dict_config = {}
            reader = csv.reader( f, delimiter="," )
            for row in reader:
                dict_config[row[0]] = row[1]
        debugprint( "INFO", "readConfig() succeeded." )
        return dict_config["userid"], \
               dict_config["passwd"], \
               dict_config["url"], \
               dict_config["pathdrv"]
    except ( IndexError, ValueError ):
        debugprint( "ERROR", "readConfig() failed. config file syntax error" )
    except:
        debugprint( "ERROR", "readConfig() failed. Unexpected error." ) 
        raise

def autoworker( worktype ):
    """
    """
    print( "autoworker is working. worktype = " + worktype )
    try:
        # 仮想ディスプレイ
        display = Display( visible=0, size=(1024,768) )
        display.start()
        debugprint( "INFO", "in autoworker(), virtual display has been opened." )

        # 設定ファイル読み込み
        userid, passwd, url, pathdrv = readConfig("./config.csv")
        debugprint( "INFO", "in autoworker(), config file has been read." )

        # chrome を開いて, 打刻ページを開く
        driver = webdriver.Chrome( pathdrv )
        driver.get(url)
        time.sleep(1)
        debugprint( "INFO", "in autoworker(), chrome has been run." )

        # フォームへの認証情報入力
        form_id = driver.find_element_by_name('user_id')
        form_pw = driver.find_element_by_name('password')
        form_id.send_keys(userid)
        form_pw.send_keys(passwd)
        time.sleep(1)
        debugprint( "INFO", "in autoworker(), form has been filt." )

        # ボタンのクリック
        if worktype == "go":
            driver.find_element_by_name('syussya').click()
        else:
            driver.find_element_by_name('taisya').click()
        time.sleep(1)
        debugprint( "INFO", "in autoworker(), button has been clicked." )

        # 成否判定
        try:
            driver.find_element_by_name("user_id")
        except:
            debugprint( "ERROR", "in autoworker(), " + str( worktype ) + "has failed." )
        else:
            debugprint( "INFO", "in autoworker(), " + str( worktype ) + "has succeed." )

        # chromeを閉じて, 仮想ディスプレイを消去
        driver.close()
        display.stop()
        debugprint( "INFO", "autoworker() exit" )
    except:
        debugprint( "ERROR", "autoworker() exit. Unexpected error." )
        raise

def schedule():
    """
    """
    try:
        debugprint( "INFO", "schedule(), started.")
        list_schedule = readSchedule( filepath_schedule )

        today = datetime.datetime.now()
        nextmonthday = today + datetime.timedelta(31)
        list_syussya, list_taisya = createSchedulesInMonth( today.year, today.month, list_schedule )
        list_syussya_nextmonth, list_taisya_nextmonth = createSchedulesInMonth( nextmonthday.year, nextmonthday.month, list_schedule )
        list_syussya.extend( list_syussya_nextmonth )
        list_taisya.extend(  list_taisya_nextmonth )
        debugprint( "INFO", "schedule() has got schedules" )
        
        schedule_obj  = sched.scheduler( time.time, time.sleep )

        for i, ( time_syussya, time_taisya ) in enumerate( zip( list_syussya, list_taisya ) ):
            schedule_obj.enterabs( time.mktime(time_syussya.timetuple()), 2*i + 1, autoworker, ("go",) )
            schedule_obj.enterabs( time.mktime(time_taisya.timetuple()),  2*i + 2, autoworker, ("taisya",) )
        
        if not is_debug:
            debugprint( "INFO", "schedule() run" )
            schedule_obj.run()
        else:
            debugprint( "DEBUG", "schdule(), debug, not run" )
            for i, ( time_syussya, time_taisya ) in enumerate( zip( list_syussya, list_taisya ) ):
                debugprint( "DEBUG", "schedule(), syussya, " + str( time_syussya ) )
                debugprint( "DEBUG", "schedule(), taisya,  " + str( time_taisya ) )

    except:
        debugprint( "ERROR", "schedule(), got unexpected error." )
        raise
    else:
        debugprint( "INFO", "schedule(), finish." )

def createSchedulesInMonth( year, month, list_schedule ):
    """
    """
    day_1st = datetime.datetime( year, month, 1 )
    delta_oneday = datetime.timedelta( days=1 )
    day = day_1st
    list_syussya = []
    list_taisya  = []
    now = datetime.datetime.now()
    while day.month == month:
        # do something
        for schedule in list_schedule: 
            if day.weekday() == schedule[0]:
                time_syussya = datetime.datetime( day.year, day.month, day.day, schedule[1], schedule[2] )
                time_taisya  = datetime.datetime( day.year, day.month, day.day, schedule[3], schedule[4] )
                if ( now - time_syussya ).days < 0:
                    list_syussya.append( time_syussya )
                if ( now - time_taisya ).days  < 0:
                    list_taisya.append(  time_taisya )
        day = day + delta_oneday
    return list_syussya, list_taisya

def main():
    debugprint( "INFO", "main(), start of program." )
    print("started time:" + str( datetime.datetime.now() ) )
    thread_obj = threading.Thread( target=schedule, daemon=True )
    thread_obj.start()
    while True:
        stop = input("Input \"stop\" and press enter to stop program. > ")
        if stop == "stop":
            debugprint( "INFO", "main(), stop of program" )
            sys.exit()

is_debug = False
filepath_schedule = os.path.abspath("./schedule.csv")
filepath_config   = os.path.abspath("./config.csv")
filepath_log      = os.path.abspath("./autoworker.log")

if __name__ == "__main__":
    main()
