import urllib,urllib2,re,sys,os,time
from BeautifulSoup import BeautifulSoup
import ClientCookie
import ClientForm

import logging
FORMAT = '%(levelname)s %(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class YahooFFLReader:
    def __init__(self,name,pw):
        self.name = name
        self.base_url = 'http://football.fantasysports.yahoo.com/'
        self.pw = pw
        self.logged_in = False

    def login(self):
        logger.info('Logging in')
        if not self.logged_in:
            return
        cookieJar = ClientCookie.CookieJar()
        opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cookieJar))
        opener.addheaders = [("User-agent","Mozilla/5.0 (compatible)")]
        ClientCookie.install_opener(opener)
        fp = ClientCookie.urlopen("http://login.yahoo.com")
        forms = ClientForm.ParseResponse(fp)
        fp.close()
        form = forms[0]
        form["login"]  = self.name
        form["passwd"] = self.pw
        fp = ClientCookie.urlopen(form.click())
        fp.close()

    def retrieve_leagues(self):
        logger.info('Retrieving leagues')
        cookieJar = ClientCookie.CookieJar()
        opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cookieJar))
        opener.addheaders = [("User-agent","Mozilla/5.0 (compatible)")]
        ClientCookie.install_opener(opener)
        fp = ClientCookie.urlopen("http://login.yahoo.com")
        forms = ClientForm.ParseResponse(fp)
        fp.close()
        form = forms[0]
        form["login"]  = self.name
        form["passwd"] = self.pw
        fp = ClientCookie.urlopen(form.click())
        fp.close()
        fp = ClientCookie.urlopen(self.base_url)
        lines = fp.readlines()
        fp.close()
        text = "\n".join(lines)
        f = open('temp.html', 'w')
        f.write(text)
        f.close()
        soup = BeautifulSoup(text)
        team_info = soup.find('div', {'class':'teams'})
        teams = {}
        for info in team_info.findAll('a', {'class':'team'}):
            teams[info.string] = {
                'url' : info['href'],
                'league' : info['href'].split('/')[2]
                }
        logger.info('Teams: ' + str(teams))
        self.teams = teams

    def retrieve_player_stats(self, league_id, num_pages):
        logger.info('Retrieving player stats')
        cookieJar = ClientCookie.CookieJar()
        opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cookieJar))
        opener.addheaders = [("User-agent","Mozilla/5.0 (compatible)")]
        ClientCookie.install_opener(opener)
        fp = ClientCookie.urlopen("http://login.yahoo.com")
        forms = ClientForm.ParseResponse(fp)
        fp.close()
        form = forms[0]
        form["login"]  = self.name
        form["passwd"] = self.pw
        fp = ClientCookie.urlopen(form.click())
        fp.close()
        week_stats = []
        for week in range(1,17):
            stats = []
            for page in range(num_pages):
                count = str(25 * page)
                logger.info('Getting page %d for week %d' % (page,week))
                stat = 'S_PW_' + str(week)
                url = self.base_url+'f1/%s/players?status=ALL&pos=O&stat1=%s&count=%s' % (league_id, stat, count)
                logger.debug('Retrieving url at %s' % url)
                fp = ClientCookie.urlopen(url)
                lines = fp.readlines()
                fp.close()
                logger.info('Cleaning up text')
                text = "".join(lines)
                text = text.replace("\n","")
                text = text.replace("\r","")
                text = re.sub(r'<\/html>.+','</html>',text,re.MULTILINE);
                logger.info('Converting to parse tree')
                soup = BeautifulSoup(text)
                logger.info('Extracting info')
                re_odd = re.compile(R'odd')
                re_even = re.compile(R'even')
                categories = []
                header_row = soup.find('tr', {'class': 'headerRow1'})
                for th in header_row.findAll('th'):
                    categories.append(th.text)
                self.categories = categories
                for info in soup.find('table', {'id':'statTable0'}).findAll('tr'):
                    c = info['class']
                    if re_odd.match(c) is not None or re_even.match(c) is not None:
                        vals = [td.text for td in info.findAll('td')]
                        stats.append(vals)
            week_stats.append(stats)
            time.sleep(4)
        self.week_stats = week_stats

    def write_stats(self):
        logger.info('Writing stats')
        f = open('data.csv', 'w')
        f.write('week,' + ",".join(self.categories) + "\n")
        for i, week_stats in enumerate(self.week_stats):
            for row in week_stats:
                write_row = '%d,' % (i+1) + ",".join(row) + "\n"
                f.write(write_row)
        f.close()

    def to_num(self,str):
        str = str.replace(',','')
        return float(str)

def main(name,pw):
    num_pages = 10
    reader = YahooFFLReader(name,pw)
    #reader.retrieve_leagues()
    #time.sleep(5)
    reader.retrieve_player_stats('192418',num_pages)
    reader.write_stats()

if __name__ == "__main__":
    name = sys.argv[1]
    pw = sys.argv[2]
    main(name,pw)