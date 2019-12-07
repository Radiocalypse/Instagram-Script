# import dependencies
import re
import json
import time
import easygui as gui
import pandas as pd
from selenium import webdriver
from datetime import datetime, timedelta
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from pandas.io.json import json_normalize


def instagram_scraping():
   # open web browser to tag feed
   hashtag = ''.join(field_values)
   browser = webdriver.Chrome()
   browser.get('https://www.instagram.com/explore/tags/' + hashtag)

   # parse HTML source page
   page_length = browser.execute_script("window.scrollTo(0, document.body.scrollHeight/1.5);")
   links = []
   source = browser.page_source
   data = bs(source, 'html.parser')
   body = data.find('body')
   script = body.find('span')
   for link in script.findAll('a'):
       if re.match("/p", link.get('href')):
           links.append('https://www.instagram.com' + link.get('href'))

   time.sleep(5)  # sleep time is required, otherwise Instagram may interrupt the script and won't scroll through pages

   page_length = browser.execute_script(
       "window.scrollTo(0, document.body.scrollHeight/1.5, document.body.scrollHeight/3.0);")
   source = browser.page_source
   data = bs(source, 'html.parser')
   body = data.find('body')
   script = body.find('span')
   for link in script.findAll('a'):
       if re.match("/p", link.get('href')):
           links.append('https://www.instagram.com' + link.get('href'))

   # get information for each image/post in the page
   result = pd.DataFrame()
   for i in range(len(links)):
       page = urlopen(links[i]).read()
       data = bs(page, 'html.parser')
       body = data.find('body')
       script = body.find('script')
       raw = script.text.strip().replace('window._sharedData =', '').replace(';', '')
       json_data = json.loads(raw)
       posts = json_data['entry_data']['PostPage'][0]['graphql']
       posts = json.dumps(posts)
       posts = json.loads(posts)
       x = pd.DataFrame.from_dict(json_normalize(posts), orient='columns')
       x.columns = x.columns.str.replace("shortcode_media.", "")
       result = result.append(x, sort=True)

   # remove posts that are older than one hour
   current_time = datetime.now()
   one_hour_ago = current_time - timedelta(minutes=60)
   timestamps = result['shortcode_media.taken_at_timestamp']
   one_hour_ago = datetime.timestamp(one_hour_ago)
   result = result.loc[(timestamps > one_hour_ago), :]
   export_file = result.to_csv('posts.csv')  # export the remaining data to a CSV file
   if export_file == False:
       error = gui.msgbox(
           "Oh no! The program crashed! Make sure to only input one tag. If you entered one tag and the program still"
           "crashed, let us know and we'll get right on it!")
   else:
       success = gui.msgbox(
           "The program has run successfully! Look for a CSV file called 'posts' (should be in the same folder as this"
           "program)")


# user input
chromedriver_install = gui.ynbox(
   'Make sure chromedriver is installed and press OK (chromedriver.chromium.org to install). MAKE SURE TO INSTALL YOUR'
   'VERSION OF CHROME! You can check your version from the browser: Help > About Google Chrome',
   'chromedriver', ['OK', 'Cancel'])
msg = "Enter an Instagram tag below (without the '#')"
title = "Hashtag"
field_names = ["Tag"]

if chromedriver_install == True:
   chromedriver_in_path = gui.ynbox(
       'Make sure this program is in a folder, and make sure chromedriver is in the same folder. Then press OK',
       'chromedriver', ['OK', 'Cancel'])

if chromedriver_install and chromedriver_in_path:
   warning = gui.ynbox(
       "Lastly, a Chrome tab will open when the script runs. DO NOT CLOSE IT! Another message box will appear after"
       "the program runs. Once it does, press OK and then you may close the window",
       'Prior Warning', ['OK', 'Cancel'])

if chromedriver_install and chromedriver_in_path and warning:
   field_values = gui.multenterbox(msg, title, field_names)
   if field_values in (None, 'Cancel'):
       program_closed = gui.msgbox("The program has been closed", "Program Closed")
   else:
       instagram_scraping()
