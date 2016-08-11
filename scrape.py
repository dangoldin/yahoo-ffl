from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time, re, csv

import settings

RE_REMOVE_HTML = re.compile('<.+?>')

SLEEP_SECONDS = 5
END_WEEK = 1
PAGES_PER_WEEK = 2
YAHOO_RESULTS_PER_PAGE = 25

fields = ['week','name','position', 'opp', 'passing_yds', 'passing_tds', 'passing_int',
    'rushing_att', 'rushing_yds', 'rushing_tds', 'receiving_tgt', 'receiving_rec', 'receiving_yds', 'receiving_tds',
    'return_tds', 'twopt', 'fumbles', 'points' ]

XPATH_MAP = {
    'name': 'td[contains(@class,"player")]/div/div/div[contains(@class,"ysf-player-name")]/a',
    'position': 'td[contains(@class,"player")]/div/div/div[contains(@class,"ysf-player-name")]/span',
    'opp': 'td//div[contains(@class,"ysf-player-detail")]/span',
    'passing_yds': 'td[16]',
    'passing_tds': 'td[17]',
    'passing_int': 'td[18]',
    'rushing_att': 'td[13]',
    'rushing_yds': 'td[14]',
    'rushing_tds': 'td[15]',
    'receiving_tgt': 'td[9]',
    'receiving_rec': 'td[10]',
    'receiving_yds': 'td[11]',
    'receiving_tds': 'td[12]',
    'return_tds': 'td[19]',
    'twopt': 'td[20]',
    'fumbles': 'td[21]',
    'points': 'td[5]',
}

stats = []

def process_stats_row(stat_row, week):
    stats_item = {}
    stats_item['week'] = week
    for col_name, xpath in XPATH_MAP.items():
        stats_item[col_name] = RE_REMOVE_HTML.sub('', stat_row.find_element_by_xpath(xpath).get_attribute('innerHTML'))
    return stats_item

def process_page(driver, week, cnt):
    print 'Getting stats for week', week, 'count', cnt

    url = 'http://football.fantasysports.yahoo.com/f1/%s/players?status=A&pos=O&cut_type=9&stat1=S_PW_%d&myteam=0&sort=PR&sdir=1&count=%d' % (str(settings.YAHOO_LEAGUEID), week, cnt)
    driver.get(url)

    base_xpath = "//div[contains(concat(' ',normalize-space(@class),' '),' players ')]/table/tbody/tr"

    rows = driver.find_elements_by_xpath(base_xpath)

    stats = []
    for row in rows:
        stats_item = process_stats_row(row, week)
        stats.append(stats_item)

    print 'Sleeping for', SLEEP_SECONDS
    time.sleep(SLEEP_SECONDS)
    return stats

def login(driver):
    driver.get("http://football.fantasysports.yahoo.com/f1/{0}".format(settings.YAHOO_LEAGUEID))

    username = driver.find_element_by_name('username')
    username.send_keys(settings.YAHOO_USERNAME)
    driver.find_element_by_id("login-signin").click()

    time.sleep(SLEEP_SECONDS)

    password = driver.find_element_by_name('passwd')
    password.send_keys(settings.YAHOO_PASSWORD)
    driver.find_element_by_id("login-signin").click()

def write_stats(stats, out):
    print 'Writing to file', out
    with open('stats.csv','w') as f:
        w = csv.DictWriter(f, delimiter=',', fieldnames=fields)
        w.writeheader()
        for row in stats:
            w.writerow(row)

def get_stats():
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(30)

    login(driver)

    time.sleep(SLEEP_SECONDS)

    stats = []
    for week in range(1, END_WEEK + 1):
        for cnt in range(0, PAGES_PER_WEEK*YAHOO_RESULTS_PER_PAGE, YAHOO_RESULTS_PER_PAGE):
            page_stats = process_page(driver, week, cnt)
            stats.extend(page_stats)

    write_stats(stats, 'stats.csv')

    driver.close()

if __name__ == '__main__':
    get_stats()

