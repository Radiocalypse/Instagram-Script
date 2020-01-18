# import dependencies
import re
import time
import json
import os.path
import pandas as pd
import easygui as gui
from selenium import webdriver
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
    links = list()
    source = browser.page_source
    data = bs(source, 'html.parser')
    body = data.find('body')
    main = body.find('main')
    script = main.find('article')
    for link in script.findAll('a'):
        if re.match("/p", link.get('href')):
            links.append('https://www.instagram.com' + link.get('href'))

    time.sleep(5)  # sleep time is required, otherwise Instagram may interrupt the script and won't scroll through pages

    # get information for each image/post in the page
    result = pd.DataFrame()
    for i in range(len(links)):
        page = urlopen(links[i]).read()
        data = bs(page, 'html.parser')
        body = data.find('body')
        script = body.find('script')
        raw = script.text.strip().replace('window._sharedData =', '').replace(';', '')
        temp = '"url":"' + links[i] + '","fact_check_overall_rating"'
        raw = raw.replace('"fact_check_overall_rating"', temp)
        json_data = json.loads(raw)
        posts = json_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']
        posts = json.dumps(posts)
        posts = json.loads(posts)
        # Only add posts to result if less than an hour old
        if posts['taken_at_timestamp'] >= (int(time.time()) - 3600):
            x = pd.DataFrame.from_dict(json_normalize(posts), orient='columns')
            result = result.append(x, sort=True)

    # export the data in result to a CSV file
    result.to_csv('posts.csv')

    if not os.path.isfile('posts.csv'):
        gui.msgbox(
            "Oh no! The program crashed! Make sure to only input one tag. If you entered one tag and the program still"
            "crashed, let us know and we'll get right on it!")
    else:
        gui.msgbox(
            "The program has run successfully! Look for a CSV file called 'posts' (should be in the same folder as this"
            " program)")


# user input
chromedriver_install = gui.ynbox(
    'Make sure the version of chromedriver installed corresponds with your version of Chrome. You can check your version from the browser: Help > About Google Chrome', 'chromedriver', ['OK', 'Cancel'])

if chromedriver_install:
    chromedriver_in_path = gui.ynbox(
        'Make sure the script and chromedriver are in the same folder, and make sure the folder is in your OS PATH variable. If the script fails because you have the wrong version of chromedriver, simply install the correct version and try again.',
        'chromedriver', ['OK', 'Cancel'])

if chromedriver_install and chromedriver_in_path:
    warning = gui.ynbox(
        "Lastly, a Chrome tab will open when the script runs. DO NOT CLOSE IT! Another message box will appear after"
        " the script runs. Once it does, press OK and then you may close the window",
        'Prior Warning', ['OK', 'Cancel'])

if chromedriver_install and chromedriver_in_path and warning:
    msg = "Enter an Instagram tag below (without the '#')"
    title = "Hashtag"
    field_names = ["Tag"]
    field_values = gui.multenterbox(msg, title, field_names)
    if field_values in (None, 'Cancel'):
        program_closed = gui.msgbox("The program has been closed", "Program Closed")
    else:
        instagram_scraping()
