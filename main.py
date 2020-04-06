from selenium_driver import WebDriver
from selenium.webdriver.chrome.options import Options
import os
import yaml


if __name__ == '__main__':
    options = Options()
    options.add_argument('--dns-prefetch-disable')
    options.headless = False
    ques = yaml.safe_load(open('question_meta.yaml', encoding='utf-8'))
    form = WebDriver(ques, executable_path=os.getcwd() + '/chromedriver', options=options)
    form.run(100)
