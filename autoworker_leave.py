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

def sendResult( flag, address, worktype ):
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

def readSchedule( filepath ):
    with open( filepath, "r" ) as f:
        list_schedule = []
        reader = csv.reader( f, delimiter = "," )
        header = next(reader)
        for row in reader:
            list_schedule.append( row )
        return list_schedule
        # [ day of week, start time, end time ]

def readConfig( filepath ):
    with open( filepath, "r" ) as f:
        dict_config = {}
        reader = csv.reader( f, delimiter="," )
        for row in reader:
            dict_config[row[0]] = row[1]
        return dict_config["userid"], \
               dict_config["passwd"], \
               dict_config["url"], \
               dict_config["pathdrv"], \
               dict_config["address"]

def main():

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

    #driver.find_element_by_name('syussya').click()
    driver.find_element_by_name('taisya').click()

    time.sleep(1)

    isSucceed=False
    try:
        driver.find_element_by_name("user_id")
    except:
        isSucceed=True
        # succedd

    sendResult( isSucceed, address, "leave" )

    driver.close()
    display.stop()
    sys.exit()

if __name__ == "__main__":
    main()
