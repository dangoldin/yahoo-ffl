import urllib,urllib2,re,sys,os,time
from BeautifulSoup import BeautifulSoup
import ClientCookie
import ClientForm

class YahooFFLReader:
    def __init__(self,name,pw):
        self.name = name
        self.base_url = 'http://football.fantasysports.yahoo.com/'
        self.pw = pw
        self.logged_in = False
    
    def login(self):
        print 'Logging in'
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
        print 'Retrieving leagues'
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
        f = open('/home/dan/Dropbox/dev/web/yahoo-ffl/tmp2.html', 'w')
        f.write(text)
        f.close()
        soup = BeautifulSoup(text)
        team_info = soup.find('div', {'class':'teams'})
        teams = {}
        for info in team_info.findAll('a', {'class':'team'}):
            teams[info.string] = {'url':info['href']}
        print teams
        self.teams = teams

    def retrieve_player_stats(self):
        print 'Retrieving player stats'
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
        num_pages = 1
        user_stats = []
        for page in range(num_pages):
            count = str(25 * page)
            #for week in range(1,17):
            for week in range(1,2):
                print 'Getting page',page,'for week',week
                stat = 'S_PW_' + str(week)
                fp = ClientCookie.urlopen(self.base_url+'f1/315538/players?status=ALL&pos=O&stat1='+stat+'&count='+count)
                lines = fp.readlines()
                fp.close()
                print "Cleaning up text"
                text = "".join(lines)
                text = text.replace("\n","")
                text = text.replace("\r","")
                text = re.sub(r'<\/html>.+','</html>',text,re.MULTILINE);
                print "Converting to parse tree"
                soup = BeautifulSoup(text)
                print "Extracting info"
                re_odd = re.compile(R'odd')
                re_even = re.compile(R'even')
                for info in soup.find('table', {'id':'statTable0'}).findAll('tr'):
                    c = info['class']
                    if re_odd.match(c) is not None or re_even.match(c) is not None:
                        name = info.find(attrs={'class':'name'}).string
                        (projected,actual,owned) = [x.string for x in info.findAll(attrs={'class':re.compile('stat wide')})]
                        (passingYds,passingTDs,passingInts,rushingYds,rushingTDs,receivingRecs,receivingYds,receivingTDs,returnTDs,twoPts,lostFumbles) = \
                        [self.to_num(x.string) for x in info.findAll(attrs={'class':'stat'})]
                        user_stats.append([name,week,projected,actual,owned,passingYds,passingTDs,passingInts,rushingYds,rushingTDs,receivingRecs,receivingYds,receivingTDs,returnTDs,twoPts,lostFumbles])
                time.sleep(13)
        self.user_stats = user_stats
        
    def write_stats(self):
        fields = ['name','week','projected','actual','owned','passingYds','passingTDs','passingInts','rushingYds','rushingTDs','receivingRecs','receivingYds','receivingTDs','returnTDs','twoPts','lostFumbles']
        f = open('/home/dan/Dropbox/dev/web/yahoo-ffl/data.csv', 'w')
        f.write(",".join(fields) + "\n")
        for vals in self.user_stats:
            f.write(",".join([ str(vals[x]) for x in range(len(fields))]) + "\n")
        f.close()
    
    def to_num(self,str):
        str = str.replace(',','')
        return float(str)

def main(name,pw):
    reader = YahooFFLReader(name,pw)
    #time.sleep(5)
    #reader.retrieve_leagues()
    #time.sleep(5)
    reader.retrieve_player_stats()
    #time.sleep(5)
    reader.write_stats()
    
if __name__ == "__main__":
    name = sys.argv[1]
    pw = sys.argv[2]
    main(name,pw)
