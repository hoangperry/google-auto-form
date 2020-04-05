from selenium_driver import WebDriver


if __name__ == '__main__':
    options = Options()
    options.add_argument('--dns-prefetch-disable')
    options.headless = False
    form = WebDriver(start_url, executable_path=os.getcwd() + '/chromedriver', options=options)
