from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

import time
import re
import csv
import sys
import random

import settings

RE_REMOVE_HTML = re.compile("<.+?>")

SLEEP_SECONDS = 3
START_WEEK = 1
END_WEEK = 17
PAGES_PER_WEEK = 4
YAHOO_RESULTS_PER_PAGE = (
    25  # Static but used to calculate offsets for loading new pages
)

# Modify these as necessary based on league settings
fields = [
    "week",
    "name",
    "position",
    "team",
    "opp",
    "bye_week",
    "passing_yds",
    "passing_tds",
    "passing_int",
    "rushing_att",
    "rushing_yds",
    "rushing_tds",
    "receiving_tgt",
    "receiving_rec",
    "receiving_yds",
    "receiving_tds",
    "return_tds",
    "twopt",
    "fumbles",
    "points",
    "o_rank",
    "projected",
    "pct_rostered",
]

# TODO: Try to get these automatically
XPATH_MAP = {
    "name": 'td//div[contains(@class,"ysf-player-name")]/a',
    "position": 'td//div[contains(@class,"ysf-player-name")]/span',
    "opp": 'td//div[contains(@class,"ysf-player-detail")]/span',
    "passing_yds": "td[14]",
    "passing_tds": "td[15]",
    "passing_int": "td[16]",
    "rushing_att": "td[19]",
    "rushing_yds": "td[20]",
    "rushing_tds": "td[21]",
    "receiving_rec": "td[22]",
    "receiving_yds": "td[23]",
    "receiving_tds": "td[24]",
    "receiving_tgt": "td[25]",
    "return_tds": "td[27]",
    "twopt": "td[28]",
    "fumbles": "td[29]",
    "bye_week": "td[7]",
    "points": "td[8]",
    "o_rank": "td[9]",
    "projected": "td[10]",
    "pct_rostered": "td[11]",
}


def process_stats_row(stat_row, week):
    stats_item = {}
    stats_item["week"] = week
    for col_name, xpath in XPATH_MAP.items():
        stats_item[col_name] = RE_REMOVE_HTML.sub(
            "", stat_row.find_element_by_xpath(
                xpath).get_attribute("innerHTML")
        )
    # Custom logic for team, position, and opponent
    stats_item["opp"] = stats_item["opp"].split(" ")[-1]
    team, position = stats_item["position"].split(" - ")
    stats_item["position"] = position
    stats_item["team"] = team
    return stats_item


def process_page(driver, week, cnt):
    print("Getting stats for week", week, "count", cnt)

    url = (
        "http://football.fantasysports.yahoo.com/f1/%s/players?status=A&pos=O&cut_type=9&stat1=S_PW_%d&myteam=0&sort=PR&sdir=1&count=%d"
        % (str(settings.YAHOO_LEAGUEID), week, cnt)
    )
    driver.get(url)

    base_xpath = "//div[contains(concat(' ',normalize-space(@class),' '),' players ')]/table/tbody/tr"

    rows = driver.find_elements_by_xpath(base_xpath)
    print(f"Fetched {len(rows)} rows")

    stats = []
    for row in rows:
        stats_item = process_stats_row(row, week)
        stats.append(stats_item)

    driver.find_element_by_tag_name("body").send_keys(Keys.END)

    print("Sleeping for", SLEEP_SECONDS)
    time.sleep(random.randint(SLEEP_SECONDS, SLEEP_SECONDS * 2))
    return stats


def login(driver):
    driver.get("https://login.yahoo.com/")

    username = driver.find_element_by_name("username")
    username.send_keys(settings.YAHOO_USERNAME)
    driver.find_element_by_id("login-signin").send_keys(Keys.RETURN)

    time.sleep(SLEEP_SECONDS)

    password = driver.find_element_by_name("password")
    password.send_keys(settings.YAHOO_PASSWORD)
    driver.find_element_by_id("login-signin").send_keys(Keys.RETURN)


def write_stats(stats, out):
    print("Writing to file", out)
    with open(out, "w") as f:
        w = csv.DictWriter(f, delimiter=",", fieldnames=fields)
        w.writeheader()
        w.writerows(stats)


def get_stats(outfile):
    chrome_options = Options()
    chrome_options.add_extension("chrome-ublock.crx")
    chrome_options.add_argument("--enable-extensions")

    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.set_page_load_timeout(30)

    print("Logging in")
    login(driver)

    time.sleep(SLEEP_SECONDS)

    stats = []
    succeeded = True
    try:
        for week in range(START_WEEK, END_WEEK + 1):
            for cnt in range(
                0, PAGES_PER_WEEK * YAHOO_RESULTS_PER_PAGE, YAHOO_RESULTS_PER_PAGE
            ):
                try:
                    page_stats = process_page(driver, week, cnt)
                except Exception as e:
                    print("Failed to process page, sleeping and retrying", e)
                    time.sleep(SLEEP_SECONDS * 5)
                    page_stats = process_page(driver, week, cnt)
                stats.extend(page_stats)
    except Exception as e:
        succeeded = False
        print(
            f"Failed to process week at week {week} and cnt {cnt}, giving up and writing stats", e)

    write_stats(stats, outfile)

    if succeeded:
        driver.close()


if __name__ == "__main__":
    outfile_name = "stats.csv"
    if len(sys.argv) > 1:
        outfile_name = sys.argv[1]

    get_stats(outfile_name)
