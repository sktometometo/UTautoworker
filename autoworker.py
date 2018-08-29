#!/usr/bin/env python
# -*- coding:utf-8 -*-

from selenium import webdriver
from pyvirtualdisplay import Display
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

def readSchedule( filepath ):
    """

    各行
    曜日 ( 0-6 ), 開始時間 ( 24時間表示 ), 終了時間 ( 24時間表示 )
    """
    with open( filepath, "r" ) as f:
        list_schedule = []
        reader = csv.reader( f, delimiter="," )

def readConfig( filepath ):
    """
    csv から 設定を読み込む
    """
    with open( filepath, "r" ) as f:
        dict_config = {}
        reader = csv.reader( f, delimiter="," )
        for row in enumerate(reader):
            dict_config[row[1][0]] = row[1][1]
        return dict_config["userid"], \
               dict_config["passwd"], \
               dict_config["url"], \
               dict_config["pathdrv"], \
               dict_config["address"]


def sendResult( flag, address, worktype ):
    """
    実行結果をメールで送信
    """
    from_address = address
    to_address = address
    charset = "ISO-2022-JP"
    subject = "[JSK][RA]Result of autoworker"
    if flag:
        text = "Succeeded"
    else:
        text = "Failed"
    if worktype == "go":
        text = text + " syussya"
    else:
        text = text + " taisya"
    msg = MIMEText( text, "plain",charset )
    msg["Subject"] = Header(subject,charset)
    #msg["From"] = from_address
    msg["To"] = to_address
    msg["Date"] = formatdate(localtime=True)

    s = smtplib.SMTP()
    s.connect()
    s.sendmail( from_address, [to_address], msg.as_string() )
    s.close()

def autoworker(worktype):

    display = Display( visible=0, size=(1024,768) )
    display.start()

    userid, passwd, url, pathdrv, address = readConfig("./config.csv")

    driver = webdriver.Chrome( pathdrv )
    driver.get(url)

    time.sleep(1)

    form_id = driver.find_element_by_name('user_id')
    form_pw = driver.find_element_by_name('password')

    time.sleep(1)

    form_id.send_keys(userid)
    form_pw.send_keys(passwd)

    time.sleep(1)

    if worktype == "go":
        driver.find_element_by_name('syussya').click()
    else:
        driver.find_element_by_name('taisya').click()

    time.sleep(1)

    isSucceed=False
    try:
        driver.find_element_by_name("user_id")
    except:
        isSucceed=True

    sendResult( isSucceed, address, "go" )

    driver.close()
    display.stop()
