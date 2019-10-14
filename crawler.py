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
import pickle

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

        if os.path.exists('./users.pkl'):
            print('userlist found, loading from file')
            with open('./users.pkl', 'rb') as f:
                users = pickle.load(f)
        else:
            users = []
            # get all users with at least 1 character
            while True:
                self.__pages_browser.get(root_url + users_url + str(page))
                try:
                    WebDriverWait(self.__pages_browser, 60).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'user-card')))
                except TimeoutException:
                    print('timeout')
                    self.__pages_browser.get(root_url + users_url + str(page))
                    try:
                        WebDriverWait(self.__pages_browser, 60).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'user-card')))
                    except TimeoutException:
                        print('timeout')
                        break

                page_results = self.__pages_browser.find_elements_by_class_name('user-card')

                for res in page_results:
                    n_chars = int(res.find_elements_by_class_name('pt-2')[-1].text)
                    if n_chars > 0:
                        url = res.find_element_by_class_name('link').get_attribute('href').replace('profil',
                                                                                                   'equipements')
                        users.append(url)

                    if 0 < user_limit <= len(users):
                        break

                print('Discovered users: ' + str(len(users)) + ' - ' + str(datetime.datetime.now()))
                if 0 < user_limit <= len(users):
                    break

                page += 1

                with open('./users.pkl', 'wb') as f:
                    pickle.dump(users, f)

        # get all stuffs from users

        progress = {'user': 0, 'stuffs': []}
        if os.path.exists('./progress.pkl'):
            print('loading saved progress')
            with open('./progress.pkl', 'rb') as f:
                progress = pickle.load(f)

        for u in range(progress['user'], len(users)):
            page = 1

            while True:
                self.__pages_browser.get(users[u] + '?page=' + str(page))

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

                    progress['stuffs'].append(
                        [name, '=HYPERLINK("{}", "{}")'.format(url, "link"), views] + [items_str] + stats)

                page += 1
                if (len(self.__pages_browser.find_elements_by_class_name('pagination')) == 0
                        or str(page) not in self.__pages_browser.find_element_by_class_name('pagination').text):
                    break

            progress['user'] = u + 1
            print('Scanned users: ' + str(u) + '/' + str(len(users)) + ' - ' + str(datetime.datetime.now()))

            if u % 20 == 0 or u == len(users) - 1:
                print('Exporting to pkl')
                with open('./progress.pkl', 'wb') as f:
                    pickle.dump(progress, f)
                print('Export done')

                print('Exporting to xlsx')
                wb = openpyxl.Workbook(write_only=True)
                ws = wb.create_sheet()

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

                for row in progress['stuffs']:
                    ws.append(row)

                if os.path.exists(filename):
                    os.remove(filename)
                wb.save(filename)

                print('Export done')
