import os

import openpyxl
from pandas import DataFrame
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import platform
import re
import datetime

# set up driver path
print("System platform :", platform.system())
if platform.system() == 'Windows':
    chrome_driver_executable_path = "./drivers/win32/chromedriver.exe"
elif platform.system() == 'Darwin':
    chrome_driver_executable_path = "./drivers/mac64/chromedriver"
elif platform.system() == 'Linux':
    chrome_driver_executable_path = "./drivers/linux64/chromedriver"
else:
    print('There was a problem while detecting the operating system')
    quit()

root_url = 'https://www.dofusbook.net'


class Crawler:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_experimental_option('prefs', {'intl.accept_languages': 'fr_FR'})
        self.__pages_browser = webdriver.Chrome(executable_path=chrome_driver_executable_path, options=options)
        self.__stuff_browser = webdriver.Chrome(executable_path=chrome_driver_executable_path, options=options)

    def quit(self):
        self.__stuff_browser.quit()
        self.__pages_browser.quit()
        print('Chrome instance shut down')

    def get_builds(self, user_limit: int = 0, filename: str = 'results.xlsx', get_stats=True):
        users_url = '/fr/communaute/membres?page='
        page = 1

        users = []

        # get all users with at least 1 character
        while True:
            self.__pages_browser.get(root_url + users_url + str(page))
            try:
                WebDriverWait(self.__pages_browser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'user-card')))
            except TimeoutException:
                break

            page_results = self.__pages_browser.find_elements_by_class_name('user-card')

            for res in page_results:
                n_chars = int(res.find_elements_by_class_name('pt-2')[-1].text)
                if n_chars > 0:
                    url = res.find_element_by_class_name('link').get_attribute('href').replace('profil', 'equipements')
                    users.append(url)

                if 0 < user_limit <= len(users):
                    break

            print('Discovered users:', len(users))
            if 0 < user_limit <= len(users):
                break

            page += 1

        # get all stuffs from users
        wb = openpyxl.Workbook()
        ws = wb.active

        ws.append(['name', 'url', 'views', 'items',
                   'points de vie',
                   'PA',
                   'PM',
                   'PO',
                   'initiative',
                   'invocation',
                   'prospection',
                   'critique',
                   'soin',
                   'vitalite',
                   'sagesse',
                   'force',
                   'intelligence',
                   'chance',
                   'agilite',
                   'puissance',
                   'fuite',
                   'esquive PA',
                   'esquive PM',
                   'pods',
                   'bouclier',
                   'niveau du stuff',
                   'tacle',
                   'retrait PA',
                   'retrait PM',
                   'dmg pieges',
                   'pui pieges',
                   'renvoi dmg',
                   'dmg neutre',
                   'dmg terre',
                   'dmg feu',
                   'dmg eau',
                   'dmg air',
                   'res neutre',
                   'res terre',
                   'res feu',
                   'res eau',
                   'res air',
                   'res% neutre',
                   'res% terre',
                   'res% feu',
                   'res% eau',
                   'res% air',
                   'dmg melee',
                   'dmg distance',
                   'dmg armes',
                   'dmg sorts',
                   'dmg critique',
                   'dmg poussee',
                   'res melee',
                   'res distance',
                   'res armes',
                   'res sorts',
                   'res critiques',
                   'res poussee'])

        progress = 0
        for u in users:
            page = 1

            while True:
                self.__pages_browser.get(u + '?page=' + str(page))

                try:
                    WebDriverWait(self.__pages_browser, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'stuff-card')))
                except TimeoutException:
                    print('timeout')
                    break

                page_results = self.__pages_browser.find_elements_by_class_name('stuff-card')

                for res in page_results:
                    infos = res.find_element_by_class_name('infos').text
                    level, views = re.findall(r'\d+', infos)[-2:]
                    views = int(views)

                    if int(level) < 200:
                        continue
                    items = [i.find_element_by_tag_name('img').get_attribute('alt') for i in
                             res.find_elements_by_class_name('item')]

                    first_iter = True
                    items_str = ''
                    for item in items:
                        if not first_iter:
                            items_str += '; '
                        first_iter = False
                        items_str += item

                    name = res.find_element_by_class_name('title').text
                    url = res.find_element_by_class_name('link').get_attribute('href')

                    stats = []
                    if get_stats:
                        self.__stuff_browser.get(url)
                        try:
                            WebDriverWait(self.__stuff_browser, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'stats-main')))
                        except TimeoutException:
                            break

                        stats = [int(i.text.replace('%', '')) for i in
                                 self.__stuff_browser.find_elements_by_class_name('number') if i.text != '']

                    ws.append([name, url, views] + [items_str] + stats)

                page += 1
                if (len(self.__pages_browser.find_elements_by_class_name('pagination')) == 0
                        or str(page) not in self.__pages_browser.find_element_by_class_name('pagination').text):
                    break

            progress += 1
            print('Scanned users: ' + str(progress) + '/' + str(len(users)) + ' ' + str(datetime.datetime.now()))

            # convert urls to clickable hyperlinks
            for row in ws.iter_rows():
                for cell in row:
                    if str(cell.value).startswith('https://'):
                        cell.hyperlink = cell.value

            if os.path.exists(filename):
                os.remove(filename)
            wb.save(filename)
