#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from selenium import webdriver
from pyvirtualdisplay import Display
import os
import sys
import time
import csv
import random
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate
import smtplib
import sched
import datetime
import threading
import argparse

class Schedule(object):

    def __init__ ( self, weekday, starthours, startminutes, endhours, endminutes ):
        """
        """
        self.weekday = int(weekday)
        self.starthours = int(starthours)
        self.startminutes = int(startminutes)
        self.endhours = int(endhours)
        self.endminutes = int(endminutes)

    def __str__( self ):
        return "Schedule[ weekday: {}, start: {}:{}, end: {}:{} ]".format(
                    self.weekday, self.starthours, self.startminutes, self.endhours, self.endminutes )

    def getWeekday( self ):
        return self.weekday

    def getStartHours( self ):
        return self.starthours

    def getStartMinutes( self ):
        return self.startminutes

    def getEndHours( self ):
        return self.endhours

    def getEndMinutes( self ):
        return self.endminutes

class UTautoworker(object):

    def __init__( self, filepath_config, filepath_schedule, filepath_firefoxdriver, isDebug=False, debugOutput=sys.stdout ):

        self.filepath_config = filepath_config
        self.filepath_schedule = filepath_schedule
        self.filepath_firefoxdriver = filepath_firefoxdriver

        self.isDebug = isDebug
        self.debugOutput = debugOutput

        self.scheduler = sched.scheduler( time.time, time.sleep )
        self.list_schedhandler_syussya = []
        self.list_schedhandler_taisya = []

        self.list_weeklyschedules = self.loadWeeklySchedules( self.filepath_schedule )

        """
        try:
            self.list_weeklyschedules = self.loadWeeklySchedule( self.filepath_schedule )
        except as e:
            self.debugPrint( "ERROR", "construction of instance of UTautoworker failed. " )
            sys.exit(-1)
        """

    def debugPrint( self, level, string_msg ):
        """
        標準出力へ時刻とメッセージを出力
        """
        if self.debugOutput is None:
            return

        level_list = [ "INFO", "WARNING", "ERROR", "DEBUG" ]
        if level in level_list:
            print( str( datetime.datetime.now() ) 
                      + " : " 
                      + level 
                      + " : " 
                      + string_msg, file=self.debugOutput, flush=True )
        else:
            print( str( datetime.datetime.now() ) 
                      + " : " 
                      + "ERROR" 
                      + " : " 
                      + "Recieved unknown log level in debugPrint()", file=self.debugOutput, flush=True )

    def loadConfig( self, filepath_config ):
        """
        """
        with open( filepath_config, "r" ) as f:
            dict_config = {}
            reader = csv.reader( f, delimiter="," )
            for row in reader:
                dict_config[row[0]] = row[1]
        self.debugPrint( "INFO", "readConfig() succeeded." )
        return dict_config["userid"], \
               dict_config["passwd"], \
               dict_config["url"]

    def loadWeeklySchedules( self, filepath_schedule ):
        """
        各行のフォーマット
        曜日 ( 0-6 ), 開始時間 ( 24時間表示 hour ), 開始時間 ( minitus), 終了時間 ( 24時間表示 ), 終了時間 ( minites )
        """
        with open( filepath_schedule, "r" ) as f:
            list_schedule = []
            reader = csv.reader( f, delimiter="," )
            header = next(reader)
            for row in reader:
                list_schedule.append( 
                        Schedule( int(row[0]), 
                                  int(row[1]), 
                                  int(row[2]), 
                                  int(row[3]), 
                                  int(row[4])  ) 
                        )
        for schedule in list_schedule:
            self.debugPrint( "INFO", "UTautoworker.loadWeeklySchedules(), schedule: " + str(schedule) )
        self.debugPrint( "INFO", "UTautoworker.loadWeeklySchedules(), succeeded" ) 
        return list_schedule

    def createSchedules( self, year, month ):
        """
        月の出退勤スケジュールを作成する.

        -----------------------------------
        Parameters:
            year - 
        """

        # day に year年month月の最初の日を入れる
        day_1st = datetime.datetime( year, month, 1 )
        delta_oneday = datetime.timedelta( days=1 )
        day = day_1st

        list_syussya = []
        list_taisya  = []
        now = datetime.datetime.now()

        while day.month == month:
            for schedule in self.list_weeklyschedules: 
                if day.weekday() == schedule.getWeekday():
                    time_syussya = datetime.datetime( 
                                        day.year, 
                                        day.month, 
                                        day.day, 
                                        schedule.getStartHours(), 
                                        schedule.getStartMinutes() )
                    time_taisya  = datetime.datetime( 
                                        day.year, 
                                        day.month, 
                                        day.day, 
                                        schedule.getEndHours(), 
                                        schedule.getEndMinutes() )
                    list_syussya.append( time_syussya )
                    list_taisya.append(  time_taisya )
            day = day + delta_oneday

        return list_syussya, list_taisya

    def initSchedulerUntilMonth( self, year, month ):
        """
        """
        self.debugPrint( "INFO", "initSchedulerUntilMonth started" )
        today = datetime.datetime.now()
        startyear = today.year
        startmonth = today.month
        endyear = year
        endmonth = month
        
        while True:
            if startyear > endyear:
                break
            elif startyear == endyear and startmonth > endmonth:
                break

            self.initScheduler( startyear, startmonth )

            startmonth += 1
            if startmonth >= 13:
                startmonth = 1
                startyear += 1

    def initScheduler( self, year, month ):
        """
        """
        self.debugPrint( "INFO","initScheduler() started" )

        list_syussya, list_taisya = self.createSchedules( year, month )

        time_margin_insec = 5
        time_margin_range_min =  1 * 60 / time_margin_insec #  1 min
        time_margin_range_max = 20 * 60 / time_margin_insec # 20 min

        for index, ( time_syussya, time_taisya ) in enumerate( zip( list_syussya, list_taisya ) ):
            time_syussya = \
                time.mktime(time_syussya.timetuple()) \
                - time_margin_insec \
                  * random.randint( time_margin_range_min, time_margin_range_max )
            time_taisya  = \
                time.mktime(time_taisya.timetuple()) \
                + time_margin_insec \
                  * random.randint( time_margin_range_min, time_margin_range_max)
            datetime_syussya = datetime.datetime.fromtimestamp( time_syussya )
            datetime_taisya  = datetime.datetime.fromtimestamp( time_taisya )

            handler_syussya = \
                self.scheduler.enterabs( time_syussya, 2*index + 1, self.autoworker, ("syussya",datetime_syussya,) )
            handler_taisya  = \
                self.scheduler.enterabs( time_taisya,  2*index + 2, self.autoworker, ("taisya",datetime_taisya,) )

            self.list_schedhandler_syussya.append( [datetime_syussya,handler_syussya] )
            self.list_schedhandler_taisya.append(  [datetime_taisya,handler_taisya] )

        self.debugPrint( "INFO", "initScheduler() finish." )

    def printScheduler( self ):
        """
        """
        list_schedhandler = [ x + ["syussya"] for x in self.list_schedhandler_syussya ] \
                          + [ x + ["taisya"]  for x in self.list_schedhandler_taisya ]
        list_schedhandler.sort( key=lambda x: x[0] )
        if self.isDebug:
            for index, schedhandler in enumerate( list_schedhandler ):
                print( str(index) + " : " + str( schedhandler[0] ) + " : " + str( schedhandler[2] ) + " : " + str( schedhandler[1] ) )
        else:
            for index, schedhandler in enumerate( list_schedhandler ):
                print( str(index) + " : " + str( schedhandler[0] ) + " : " + str( schedhandler[2] ) )

    def cancelScheduler( self, index ):
        """
        """
        list_schedhandler = [ x + ["syussya"] for x in self.list_schedhandler_syussya ] \
                          + [ x + ["taisya"]  for x in self.list_schedhandler_taisya ]
        list_schedhandler.sort( key=lambda x: x[0] )
        targetschedhandler = list_schedhandler[index]
        eventID = targetschedhandler[1]

        self.scheduler.cancel( eventID )
        if eventID in [ x[1] for x in self.list_schedhandler_syussya ]:
            del self.list_schedhandler_syussya[ [ x[1] for x in self.list_schedhandler_syussya ].index( eventID ) ]
        if eventID in [ x[1] for x in self.list_schedhandler_taisya ]:
            del self.list_schedhandler_taisya[ [ x[1] for x in self.list_schedhandler_taisya ].index( eventID ) ]

        print(" Canceled scheduled " + str(targetschedhandler[2]) + " at " + str( targetschedhandler[0] ) )

    def autoworker( self, worktype, worktime ):
        """
        """

        self.debugPrint( "INFO", "autoworker is working. worktype = " + worktype )

        if self.isDebug:

            self.debugPrint( "INFO", "autoworker runnnig in debug mode, worktype:{}, worktime{}".format( worktype, worktime ) )

            if worktime in [ x[0] for x in self.list_schedhandler_syussya ]:
                del self.list_schedhandler_syussya[ [ x[0] for x in self.list_schedhandler_syussya ].index(worktime) ]

            if worktime in [ x[0] for x in self.list_schedhandler_taisya ]:
                del self.list_schedhandler_taisya[ [ x[0] for x in self.list_schedhandler_taisya ].index(worktime) ]

            return

        # 仮想ディスプレイ
        display = Display( visible=0, size=(1024,768) )
        display.start()
        self.debugPrint( "INFO", "in autoworker(), virtual display has been opened." )

        # 設定ファイル読み込み
        userid, passwd, url = self.loadConfig( self.filepath_config )
        self.debugPrint( "INFO", "in autoworker(), config file has been read." )

        # Firefox を開いて, 打刻ページを開く
        driver = webdriver.Firefox( self.filepath_firefoxdriver )
        driver.get(url)
        time.sleep(1)
        self.debugPrint( "INFO", "in autoworker(), firefox has been run." )

        # フォームへの認証情報入力
        form_id = driver.find_element_by_name('user_id')
        form_pw = driver.find_element_by_name('password')
        form_id.send_keys(userid)
        form_pw.send_keys(passwd)
        time.sleep(1)
        self.debugPrint( "INFO", "in autoworker(), form has been filt." )

        # ボタンのクリック
        if worktype == "syussya":
            driver.find_element_by_name('syussya').click()
        elif worktype == "taisya":
            driver.find_element_by_name('taisya').click()
        else:
            self.debugPrint( "INFO", "in autoworker(), unknown worktype received." )
        time.sleep(1)
        self.debugPrint( "INFO", "in autoworker(), button has been clicked." )

        # 成否判定
        try:
            driver.find_element_by_name("user_id")
        except:
            self.debugPrint( "ERROR", "in autoworker(), " + str( worktype ) + "has failed." )
        else:
            self.debugPrint( "INFO", "in autoworker(), " + str( worktype ) + "has succeed." )

        # chromeを閉じて, 仮想ディスプレイを消去
        driver.close()
        display.stop()
        self.debugPrint( "INFO", "autoworker() exit" )

        if worktime in [ x[0] for x in self.list_schedhandler_syussya ]:
            del self.list_schedhandler_syussya[ [ x[0] for x in self.list_schedhandler_syussya ].index(worktime) ]

        if worktime in [ x[0] for x in self.list_schedhandler_taisya ]:
            del self.list_schedhandler_taisya[ [ x[0] for x in self.list_schedhandler_taisya ].index(worktime) ]


    def process( self ):
        """
        """
        self.debugPrint( "INFO", "process() thread started." )
        self.scheduler.run()

    def spin( self ):
        """
        """
        # thread_obj = threading.Thread( target=schedule, daemon=True )
        self.processthread = threading.Thread( target=self.process, daemon=True )
        self.processthread.start()

        while True:
            print(" \"stop\" and press enter to stop program. ")
            print(" \"list\" and press enter to list schedules. ")
            print(" \"cancel\" and press enter to cancel a schedule. ")
            inputline = input("Input > ")

            if inputline == "stop":
                self.debugPrint( "INFO", "spin(), stop of program" )
                sys.exit()

            elif inputline == "list": 
                print("schedules:")
                self.printScheduler()

            elif inputline == "cancel":
                x = input("input number of item to delete. > ")
                val = int(x)
                self.cancelScheduler( val )

            else:
                print("invalid input.")

if __name__ == "__main__":

    parser = argparse.ArgumentParser( description="UT autoworker." )

    parser.add_argument( "filepath_config", help="filepath to config csv file" )
    parser.add_argument( "filepath_schedule", help="filepath to schedule csv file" )
    parser.add_argument( "filepath_firefoxdriver", help="filepath to selenium firefox driver" )
    parser.add_argument( "year",  type=int, help="year you set on UT autoworker" )
    parser.add_argument( "month", type=int, help="month you ser on UT autoworker" )

    parser.add_argument( "-d", "--debug", help="turn debug mode on", action="store_true" )

    args = parser.parse_args()

    if args.debug:
        print("debug mode")
        hoge = UTautoworker( args.filepath_config, args.filepath_schedule, args.filepath_firefoxdriver, isDebug=True, debugOutput=sys.stdout )
    else:
        f = open( os.path.dirname( os.path.abspath(__file__) ) + "/debug.log", mode="w" )
        hoge = UTautoworker( args.filepath_config, args.filepath_schedule, args.filepath_firefoxdriver, isDebug=False, debugOutput=f )
    hoge.initSchedulerUntilMonth( args.year, args.month )

    list_schedhandler = [ x + ["syussya"] for x in hoge.list_schedhandler_syussya ] \
                      + [ x + ["taisya"]  for x in hoge.list_schedhandler_taisya ]
    list_schedhandler.sort( key=lambda x: x[0] )
    for schedhandler in list_schedhandler:
        if schedhandler[0] < datetime.datetime.now():
            hoge.scheduler.cancel( schedhandler[1] )    
            if schedhandler[0] in [ x[0] for x in hoge.list_schedhandler_syussya ]:
                del hoge.list_schedhandler_syussya[ [ x[0] for x in hoge.list_schedhandler_syussya ].index( schedhandler[0] ) ]
            if schedhandler[0] in [ x[0] for x in hoge.list_schedhandler_taisya ]:
                del hoge.list_schedhandler_taisya[ [ x[0] for x in hoge.list_schedhandler_taisya ].index( schedhandler[0] ) ]

    hoge.spin()
