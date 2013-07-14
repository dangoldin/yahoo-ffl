from scrapy.spider import BaseSpider
from scrapy.http import FormRequest, Request
from scrapy.selector import HtmlXPathSelector

from scrapeffl.items import ScrapefflPlayerItem

import re

RE_CNT = re.compile('count=(\d+)')
RE_WEEK = re.compile('stat1=S_PW_(\d+)')

class YahooFFLSpider(BaseSpider):
    name = 'yahooffl'
    #allowed_domains = ['football.fantasysports.yahoo.com']
    allowed_domains = ['yahoo.com']
    start_urls = ['https://login.yahoo.com/config/login?']
    base_url = 'http://football.fantasysports.yahoo.com/f1/{}/players?status=ALL&pos=O&stat1=S_PW_{}&count=0'

    def parse(self, response):
        return [FormRequest.from_response(response,
                    formdata={'login': self.settings['YAHOO_USERNAME'], 'passwd': self.settings['YAHOO_PASSWORD']},
                    callback=self.after_login)]

    def parse_stats(self, response):
        hxs = HtmlXPathSelector(response)

        # Parse the next url
        next_page = hxs.select('//ul[@class="pagingnavlist"]/li[contains(@class,"last")]/a/@href')
        next_page_url = 'http://football.fantasysports.yahoo.com' + next_page.extract()[0]
        count = int(RE_CNT.findall(next_page_url)[0]) # Don't go past a certain threshold of players
        current_week = int(RE_WEEK.findall(next_page_url)[0])

        self.log('Next url is at count {} with week {}'.format(count, current_week))

        if current_week <= 17:
            # Parse the stats
            stat_rows = hxs.select('//table[@id="statTable0"]/tbody/tr')
            xpath_map = {
                'name': 'td[contains(@class,"player")]/div[contains(@class,"ysf-player-name")]/a/text()',
                'position': 'td[contains(@class,"player")]/div[contains(@class,"ysf-player-detail")]/ul/li[contains(@class,"ysf-player-team-pos")]/span/text()',
                'opp': 'td[contains(@class,"opp")]/text()',
                'passing_yds': 'td[@class="stat"][1]/text()',
                'passing_tds': 'td[@class="stat"][2]/text()',
                'passing_int': 'td[@class="stat"][3]/text()',
                'rushing_yds': 'td[@class="stat"][4]/text()',
                'rushing_tds': 'td[@class="stat"][5]/text()',
                'receiving_recs': 'td[@class="stat"][6]/text()',
                'receiving_yds': 'td[@class="stat"][7]/text()',
                'receiving_tds': 'td[@class="stat"][8]/text()',
                'return_tds': 'td[@class="stat"][9]/text()',
                'misc_twopt': 'td[@class="stat"][10]/text()',
                'fumbles': 'td[@class="stat"][11]/text()',
                'points': 'td[contains(@class,"pts")]/text()',
            }
            for stat_row in stat_rows:
                stats_item = ScrapefflPlayerItem()
                stats_item['week'] = current_week
                for col_name, xpath in xpath_map.items():
                    stats_item[col_name] = stat_row.select(xpath).extract()
                yield stats_item

        # Jump to next week if we go past the threshold of players        
            if count > self.settings['MAX_STATS_PER_WEEK']:
                yield Request(self.base_url.format(self.settings['YAHOO_LEAGUEID'], current_week + 1), callback=self.parse_stats)
            else:
                yield Request(next_page_url, callback=self.parse_stats)                

    def after_login(self, response):
        # check login succeed before going on
        if "authentication failed" in response.body:
            self.log("Login failed", level=log.ERROR)
            return
        else:
            # Start scraping at week 1 by specifying the league ID and the start week
            return Request(self.base_url.format(self.settings['YAHOO_LEAGUEID'], '1'),
                    callback=self.parse_stats)