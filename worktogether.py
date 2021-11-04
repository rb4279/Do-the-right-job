import json
import math

import certifi
import threading
from IPython import embed
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
import time

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException

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
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")

        chromedriver_autoinstaller.install(True)
        chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
        service = Service(f'./{chrome_ver}/chromedriver')

        self.driver = webdriver.Chrome(service=service, options=options)

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

    def done(self):
        return self.driver.close()


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
    target_links = []

    def __init__(self, _target_links):
        self.target_links = _target_links

    def get_target_links_count(self):
        return len(self.target_links)

    def run_crawl(self, detail_list):
        self.open_window()
        for target_link in self.target_links:
            try:
                self.go(target_link)
                job = self.find('#content > div.company-detail > div.leftBox > div.empdetail > table:nth-child(2) > tbody > tr:nth-child(1) > td').text
                address = self.find('#content > div.company-detail > div.leftBox > div.inner > div.detail-table > table > tbody > tr:nth-child(5) > td').text
                contents = self.find('#content > div.company-detail > div.leftBox > div.empdetail > table:nth-child(2) > tbody > tr:nth-child(3) > td').text
                detail_list.append({
                    'job': job,
                    'address': address,
                    'contents': contents,
                })
            except UnexpectedAlertPresentException:
                # 마감된 채용 정보 얼럿이 뜨는 경우 패스
                continue

        print('crawl done')

class JobCodeCrawlBot(CrawlBot):
    URL_FORM = "https://www.worktogether.or.kr/jobMap/jobMapByName.do?jobCd={job_code}"
    JOB_CODES = ['0111', '0112', '0121', '0122', '0123', '0124', '0131', '0132', '0133', '0134', '0135', '0136', '0137', '0139', '0141', '0142', '0143', '0151', '0152', '0159', '0161', '0162', '0163', '0169', '0210', '0221', '0222', '0231', '0232', '0233', '0234', '0241', '0242', '0243', '0244', '0251', '0252', '0253', '0254', '0255', '0261', '0262', '0263', '0264', '0271', '0272', '0281', '0282', '0283', '0284', '0291', '0292', '0293', '0294', '0295', '0299', '0311', '0312', '0313', '0314', '0315', '0319', '0321', '0322', '0323', '0324', '0325', '0329', '0331', '0332', '1101', '1102', '1211', '1212', '1221', '1222', '1223', '1311', '1312', '1320', '1331', '1332', '1333', '1339', '1341', '1342', '1343', '1344', '1349', '1350', '1360', '1401', '1402', '1403', '1404', '1405', '1406', '1407', '1511', '1512', '1513', '1521', '1522', '1531', '1532', '1533', '1541', '1542', '1551', '1552', '1553', '1554', '1555', '1561', '1562', '1571', '1572', '1581', '1582', '1583', '1584', '1585', '1591', '1599', '2111', '2112', '2121', '2122', '2123', '2129', '2130', '2141', '2142', '2143', '2144', '2145', '2149', '2151', '2152', '2153', '2211', '2212', '2213', '2214', '2219', '2220', '2311', '2312', '2313', '2314', '2315', '2321', '2329', '2331', '2339', '2401', '2402', '2403', '2501', '2502', '2503', '2509', '3011', '3012', '3013', '3014', '3020', '3030', '3040', '3050', '3061', '3062', '3063', '3064', '3065', '3066', '3067', '3069', '3071', '3072', '3073', '3074', '3075', '3076', '3079', '4111', '4112', '4113', '4120', '4131', '4132', '4141', '4142', '4143', '4144', '4145', '4146', '4147', '4149', '4151', '4152', '4153', '4154', '4155', '4161', '4162', '4163', '4164', '4165', '4166', '4167', '4169', '4171', '4172', '4201', '4202', '4203', '4204', '4209', '5111', '5112', '5113', '5114', '5115', '5119', '5121', '5122', '5123', '5124', '5129', '5211', '5212', '5213', '5221', '5222', '5230', '5240', '5311', '5312', '5313', '5314', '5315', '5316', '5317', '5319', '5321', '5322', '5323', '5324', '5329', '5411', '5412', '5413', '5419', '5420', '5501', '5502', '5611', '5612', '5613', '5614', '5615', '5616', '5621', '5622', '5623', '5624', '5629', '6110', '6121', '6122', '6123', '6124', '6125', '6129', '6130', '6140', '6151', '6152', '6153', '6154', '6155', '6156', '6157', '6161', '6162', '6171', '6179', '6211', '6212', '6213', '6214', '6219', '6221', '6222', '6223', '6229', '6230', '6241', '6242', '6243', '6244', '6249', '7011', '7012', '7013', '7014', '7015', '7016', '7017', '7019', '7021', '7022', '7023', '7024', '7025', '7026', '7027', '7029', '7031', '7032', '7039', '7040', '7051', '7052', '7059', '7060', '8111', '8112', '8113', '8114', '8115', '8116', '8119', '8121', '8122', '8123', '8124', '8129', '8131', '8132', '8140', '8150', '8161', '8162', '8171', '8172', '8173', '8211', '8212', '8221', '8222', '8223', '8224', '8231', '8232', '8233', '8234', '8241', '8242', '8251', '8252', '8261', '8262', '8263', '8264', '8269', '8311', '8312', '8313', '8321', '8322', '8329', '8330', '8340', '8351', '8352', '8360', '8411', '8412', '8419', '8421', '8422', '8423', '8511', '8512', '8519', '8521', '8522', '8523', '8524', '8531', '8532', '8611', '8612', '8613', '8621', '8622', '8623', '8629', '8631', '8632', '8633', '8634', '8639', '8641', '8642', '8643', '8649', '8711', '8712', '8721', '8722', '8723', '8729', '8731', '8732', '8733', '8734', '8735', '8739', '8811', '8812', '8821', '8822', '8823', '8829', '8831', '8832', '8833', '8841', '8842', '8851', '8852', '8853', '8859', '8900', '9011', '9012', '9013', '9014', '9015', '9021', '9022', '9029', '9031', '9039', '9041', '9042', '9050']
    # JOB_CODES = ['0111', '0112', '0121', ]

    def run_crawl(self):
        self.open_window()
        job_infos = []
        for job_code in self.JOB_CODES:
            self.go(self.URL_FORM.format(job_code=job_code))
            job_infos.append({
                'name': self.find('table.board_detail > tbody > tr > th').text,
                'descriptions': [td_tag.text for td_tag in self.finds('table.board_detail > tbody > tr > td') if '해당 내용이 없습니다' not in td_tag.text],
            })
        return job_infos


class DataLoader:
    @staticmethod
    def load_links():
        try:
            with open('job_detail_links.json', 'r', encoding='UTF-8') as f:
                dump_line = f.readline()
                links = json.loads(dump_line)
            return links
        except FileNotFoundError as e:
            list_crawl_bot = ListCrawlBot()
            detail_links = list_crawl_bot.run_crawl()

            with open('job_detail_links.json', 'w', encoding='UTF-8') as f:
                f.write(json.dumps(detail_links, ensure_ascii=False))
            list_crawl_bot.done()
            return detail_links

    @staticmethod
    def load_job_code_infos():
        try:
            with open('job_code_infos.json', 'r', encoding='UTF-8') as f:
                dump_line = f.readline()
                links = json.loads(dump_line)
            return links
        except FileNotFoundError as e:
            job_bot = JobCodeCrawlBot()
            job_code_infos = job_bot.run_crawl()

            with open('job_code_infos.json', 'w', encoding='UTF-8') as f:
                f.write(json.dumps(job_code_infos, ensure_ascii=False))
            job_bot.done()
            return job_code_infos

    @staticmethod
    def load_job_detail_infos():
        detail_links = DataLoader.load_links()
        SIZE = math.ceil(len(detail_links) / WINDOW_NUM)
        bots = []
        threads = []
        for i in range(WINDOW_NUM):
            bot = DetailCrawlBot(detail_links[i * SIZE:(i + 1) * SIZE])
            bots.append(bot)

        detail_list = []
        for bot in bots:
            t = threading.Thread(target=bot.run_crawl, args=(detail_list,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        with open('job_detail_list.json', 'w', encoding='UTF-8') as f:
                f.write(json.dumps(detail_list, ensure_ascii=False))
        return detail_list


if __name__ == "__main__":
    DataLoader.load_job_detail_infos()
