# Scrapy settings for scrapeffl project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'scrapeffl'

SPIDER_MODULES = ['scrapeffl.spiders']
NEWSPIDER_MODULE = 'scrapeffl.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'scrapeffl (+http://www.yourdomain.com)'

AUTOTHROTTLE_ENABLED = True

# User defined settings

MAX_STATS_PER_WEEK = 250

YAHOO_USERNAME = '' 
YAHOO_PASSWORD = ''
YAHOO_LEAGUEID = ''

try:
    from settings_local import *
except ImportError:
    pass