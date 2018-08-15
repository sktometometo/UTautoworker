#!/usr/bin/env python
# -*- coding:utf-8 -*-

from selenium import webdriver
import sys
import time

userid = "7204472798"
passwd = "3JrogtdpEgGWBNm@"
url    = "https://ut-ppsweb.adm.u-tokyo.ac.jp/cws/srwtimerec"

driver = webdriver.Chrome("/mnt/data/trusty/home/sktometometo/Projects/autoworker/chromedriver")
driver.get(url)

time.sleep(1)

form_id = driver.find_element_by_name('user_id')
form_pw = driver.find_element_by_name('password')

time.sleep(1)

form_id.send_keys(userid)
form_pw.send_keys(passwd)

time.sleep(1)

driver.find_element_by_name('syussya').click()
#driver.find_element_by_name('taisya').click()

time.sleep(1)

driver.close()

sys.exit(0)
