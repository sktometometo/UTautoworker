# UT autoworker

This is a 

# Requirements

- Firefox
- Python3
- Selenium
- pyvirtualdisplay

# Usage

## Selenium configuration
Download [firefox webdriver](https://github.com/mozilla/geckodriver/) and put it in the UTautoworker directory.

```
$ cd <UT autoworker directory>
$ wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
$ tar xvzf geckodriver-v0.24.0-linux64.tar.gz
```

## configuration file editing
Open config.csv and replace "test" string with your account information and the URL of shuttaikin page.

## scheduling csv file editing
Open schedule.csv and add your weekly working schedules.
Descriptions about each field of csv file are below

|:---------------|:------------------------|
|曜日|0-6で月-日,0が月曜日になることに注意|
|開始時間(hour)|0-23で勤務開始の時間を記入|
|開始時間(minutes)|0-59で勤務開始の分を記入|
|終了時間(hour)|0-23で勤務終了の時間を記入|
|終了時間(minutes)|0-59で勤務終了の分を記入|

## run
run the script from command line.

```
$ cd <UT autoworker directory>
$ python UTautoworker.py ./config.csv ./schedule.csv ./geckodriver <year> <month>
```
