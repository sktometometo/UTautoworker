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

## run
run the script from command line.

```
$ cd <UT autoworker directory>
$ python UTautoworker.py ./config.csv ./schedule.csv ./geckodriver <year> <month>
```
