#!/usr/bin/env python
# -*- coding:utf-8 -*-

from selenium import webdriver
import sys
import time
import csv

def readConfig( filepath ):

    with open( filepath, "r" ) as f:
        dict_config = {}
        reader = csv.reader( f, delimiter="," )
        for row in enumerate(reader):
            dict_config[row[1][0]] = row[1][1]
        return dict_config["userid"], \
               dict_config["passwd"], \
               dict_config["url"], \
               dict_config["pathdrv"]

def main():

    userid, passwd, url, pathdrv = readConfig("./config.csv")

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

    driver.close()

    sys.exit(0)

if __name__ == "__main__":
    main()
