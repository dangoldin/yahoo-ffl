# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class ScrapefflPlayerItem(Item):
    name = Field()
    position = Field()
    week = Field()
    opp = Field()
    passing_yds = Field()
    passing_tds = Field()
    passing_int = Field()
    rushing_yds = Field()
    rushing_tds = Field()
    receiving_recs = Field()
    receiving_yds = Field()
    receiving_tds = Field()
    return_tds = Field()
    misc_twopt = Field()
    fumbles = Field()
    points = Field()
