from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import re
import time
import os
import json
import requests
import shutil


img_conter = 0


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def write_to_file(filename, obj_to_write):
    file_out = open(filename, mode='w', encoding='utf-8')
    file_out.write(json.dumps(obj_to_write, ensure_ascii=False, indent=4))
    file_out.close()


class WebDriver:
    def __init__(self, homepage, executable_path=None, options=None, timeout=15, wait=15):

        if options is not None:
            self.driver = webdriver.Chrome(executable_path=executable_path, chrome_options=options)
        else:
            self.driver = webdriver.Chrome(executable_path=executable_path)
        self.homepage = homepage
        self.driver.set_page_load_timeout(timeout)
        self.wait = WebDriverWait(self.driver, wait)
        self.html = None
        self.driver.implicitly_wait(wait)
        try:
            os.mkdir('download/')
        except Exception as ex:
            print(ex)

    def get_html(self, url):
        try:
            self.driver.get(url)
            page_source = self.driver.page_source
            page_source = re.sub(r'<br\s*[\/]?>', '\n', page_source)
            page_source = re.sub(r'<\s*\/p>', '</p>\n', page_source)

            self.html = BeautifulSoup(page_source, "lxml")
            time.sleep(0.5)
        except TimeoutException as toe:
            print(toe)
            self.driver.refresh()
            print(url)
        except Exception as ex:
            print(ex)

    def execute_script(self, script):
        try:
            self.driver.execute_script(script)
        except Exception as ex:
            print(ex)
            # return to start url
            self.get_html(self.homepage)
