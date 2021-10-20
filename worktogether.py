import math

import certifi
import threading
from IPython import embed
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WINDOW_NUM = 4
lock = threading.Lock()


class Util:
    @staticmethod
    def get_only_int(string):
        return int(''.join(filter(str.isdigit, string)))


class CrawlBot:
    driver = None

    def open_window(self):
        options = Options()

        chromedriver_autoinstaller.install(True)
        chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
        self.driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver', options=options)

    def go(self, url: str):
        self.driver.get(url)

    def wait(self, sec=10, forced=False):
        if forced:
            time.sleep(sec)
        else:
            self.driver.implicitly_wait(sec)

    def find(self, value):
        if self.driver is None:
            raise Exception('창 띄워')
        return self.driver.find_element(by=By.CSS_SELECTOR, value=value)

    def finds(self, value):
        if self.driver is None:
            raise Exception('창 띄워')
        return self.driver.find_elements(by=By.CSS_SELECTOR, value=value)


class ListCrawlBot(CrawlBot):
    RESULT_SIZE = 1000

    def run_crawl(self):
        def crawl_infos():
            a_tags = self.finds('table.board_list > tbody > tr > td.title > p.link > a')
            return [a_tag.get_attribute('href') for a_tag in a_tags]

        self.open_window()
        self.go(f'https://www.worktogether.or.kr/empInfo/empInfoSrch/list/dtlEmpSrchList.do?preferentialGbn=Y|D&resultCnt={self.RESULT_SIZE}')
        links = crawl_infos()
        total_count = Util.get_only_int(self.find('fieldset.search_contol > span > strong').text)
        for pageIndex in range(2, math.ceil(total_count / self.RESULT_SIZE) + 1):
            self.go(f'https://www.worktogether.or.kr/empInfo/empInfoSrch/list/dtlEmpSrchList.do?preferentialGbn=Y|D&resultCnt={self.RESULT_SIZE}&pageIndex={pageIndex}')
            links.extend(crawl_infos())

        return links


class DetailCrawlBot(CrawlBot):
    employment_infos = []

    def __init__(self, _employment_infos):
        self.employment_infos = _employment_infos

    def get_employment_infos_count(self):
        return len(self.employment_infos)

    def run_crawl(self):
        pass


if __name__ == "__main__":
    list_crawl_bot = ListCrawlBot()
    detail_links = list_crawl_bot.run_crawl()
    print(len(detail_links))
    print(detail_links[:4])
    # SIZE = len(user_infos) // WINDOW_NUM
    # REMAINDER = math.ceil(len(user_infos) / WINDOW_NUM - SIZE)
    # bots = []
    # threads = []
    # for i in range(WINDOW_NUM):
    #     index = SIZE if i == WINDOW_NUM - 1 else SIZE + REMAINDER
    #     bot = CrawlBot(num=i)
    #     bots.append(bot)
    #
    # for bot in bots:
    #     print(bot.port, '포트에서', bot.get_user_infos_count(), '개 채용정보 수집을 시작합니다.')
    #     t = threading.Thread(target=bot.run_draw)
    #     t.start()
    #     threads.append(t)
    #     time.sleep(2)
    #
    # for t in threads:
    #     t.join()  # 스레드가 종료될 때까지 기다린다.
