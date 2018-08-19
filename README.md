README
======

Yahoo-ffl is a quick script to help download fantasy football stats from Yahoo. It's currently configured to do it using the Selenium webdriver and to retrieve the projected stats for the current (2017-2018) season. It should be straightforward to tweak the script to pull data for other league formats and settings. Pull requests to make it more flexible are welcome.

To get it working:

- Install the selenium library (pip install -r requirements.txt)
- Download the latest [ChromeDriver](http://chromedriver.chromium.org/downloads)
- Create a settings.py file containg your Yahoo username, password, and league id
- Run the script using "python scrape.py"
- To test the script you can modify some of the constants (END_WEEK, PAGES_PER_WEEK) in order to make sure the data is correct.

--------------------

Notes: Depending on your league scoring settings the scraper might not work as expected since the set of columns displayed on the page vary due to differences in league settings. In that case, you should be able to update the code in scrape.py to come up with a new set of xpath expressions.

For those that are lazy, you can download the appropriate stats-###YEAR###.csv file which contains the data pulled using my league's PPR settings.
