from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import re
import time
import os
import json
import random
import bisect


def cdf(weights):
    total = sum(weights)
    result = []
    cumsum = 0
    for w in weights:
        cumsum += w
        result.append(cumsum / total)
    return result


def choose_with_p(weights, population):
    cdf_vals = cdf(weights)
    x = random.random()
    idx = bisect.bisect(cdf_vals, x)
    return population[idx]


def random_ans(dict_ques):
    if dict_ques['type'] == 'one':
        weights = list()
        population = list()
        for anss in dict_ques['answer']:
            weights.append(dict_ques['answer'][anss])
            population.append(anss)
        return choose_with_p(weights, population)

    elif dict_ques['type'] == 'many':
        list_ans = list()
        for anss in dict_ques['answer']:
            is_choice = choose_with_p(
                [dict_ques['answer'][anss], 1-dict_ques['answer'][anss]],
                [1, 0]
            )
            if is_choice == 1:
                list_ans.append(anss)
        return list_ans


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def write_to_file(filename, obj_to_write):
    file_out = open(filename, mode='w', encoding='utf-8')
    file_out.write(json.dumps(obj_to_write, ensure_ascii=False, indent=4))
    file_out.close()


class WebDriver:
    def __init__(self, meta_question, executable_path=None, options=None, timeout=15, wait=15):

        if options is not None:
            self.driver = webdriver.Chrome(executable_path=executable_path, chrome_options=options)
        else:
            self.driver = webdriver.Chrome(executable_path=executable_path)
        self.homepage = meta_question['url']
        self.meta_question = meta_question
        self.driver.set_page_load_timeout(timeout)
        self.wait = WebDriverWait(self.driver, wait)
        self.html = None
        self.driver.implicitly_wait(wait)
        self.total = 1
        try:
            os.mkdir('download/')
        except Exception as ex:
            print(ex)

    def get_html(self, url):
        try:
            self.driver.get(url)
            page_source = self.driver.page_source
            page_source = re.sub(r'<br\s*[/]?>', '\n', page_source)
            page_source = re.sub(r'<\s*/p>', '</p>\n', page_source)

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

    def run(self, gen_record=100):
        for i in range(gen_record):
            self.get_html(self.homepage)
            for page in range(self.meta_question['range']):
                blocks_ques = self.driver.find_elements_by_css_selector(
                    'div.freebirdFormviewerViewItemList div.freebirdFormviewerViewNumberedItemContainer'
                )
                for block in blocks_ques:
                    if block.find_element_by_css_selector('div.freebirdCustomFont').get_attribute('aria-level') != '3':
                        continue
                    try:
                        title_block = block.find_element_by_css_selector(
                            'div.freebirdFormviewerViewItemsItemItemTitle'
                        ).text.split('\n')[0].replace('*', '').strip()
                    except:
                        continue

                    for question_name, meta_qu in self.meta_question['page'].items():
                        if question_name != title_block.strip():
                            continue
                        answer_choice = random_ans(meta_qu)

                        if meta_qu['type'] == 'one':
                            ans_list = block.find_elements_by_css_selector(
                                'div.freebirdFormviewerViewItemsRadioOptionContainer'
                            )
                            for ans in ans_list:
                                if ans.text.strip() == answer_choice:
                                    ans.find_element_by_css_selector(
                                        'div.appsMaterialWizToggleRadiogroupElContainer'
                                    ).click()
                                    break
                        elif meta_qu['type'] == 'many':
                            ans_list = block.find_elements_by_css_selector(
                                'div.freebirdFormviewerViewItemsCheckboxOptionContainer'
                            )
                            for ans in ans_list:
                                if ans.text.strip() in answer_choice:
                                    ans.find_element_by_css_selector(
                                        'div.appsMaterialWizTogglePapercheckboxCheckbox'
                                    ).click()

                        elif meta_qu['type'] == 'range':
                            ans_range = random.randint(0, 6)
                            list_ans = block.find_elements_by_css_selector('label.freebirdMaterialScalecontentColumn')
                            list_ans[ans_range].click()

                        elif meta_qu['type'] == 'rank':
                            list_rank = block.find_elements_by_css_selector(
                                'div.appsMaterialWizToggleRadiogroupGroupContainer.exportGroupContainer.freebirdFormviewerViewItemsGridUngraded.freebirdFormviewerViewItemsGridRowGroup'
                            )
                            for row in list_rank:
                                ans_range = random.randint(0, 4)
                                list_ans = row.find_elements_by_css_selector(
                                    'div.appsMaterialWizToggleRadiogroupOffRadio'
                                )
                                list_ans[ans_range].click()

                if page < self.meta_question['range'] - 1:
                    self.driver.find_element_by_css_selector(
                        'div.freebirdFormviewerViewNavigationNoSubmitButton'
                    ).click()
                else:
                    self.driver.find_element_by_css_selector('div.freebirdThemedFilledButtonM2').click()
                    print(f'finish {self.total}')
                    self.total += 1
