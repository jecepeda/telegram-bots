from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
import aiohttp
import asyncio
import lxml

driver = webdriver.PhantomJS(executable_path="phantomjs-2.1.1-linux-x86_64/bin/phantomjs")
driver.get("http://it-ebooks.info/")

search = driver.find_element_by_id('q')
search.send_keys('Python')
search.send_keys(Keys.RETURN)

links = driver.find_elements_by_css_selector('a.gs-title')
hrefs = (p_link.get_attribute('href') for p_link in links)
hrefs = (str(href) for href in hrefs if href is not None)
hrefs = set(hrefs)

regex = re.compile(r'(http://it-ebooks.info/book/\d*/)')
hrefs = [href for href in hrefs if regex.match(href)]


async def find_book_download_link(book_url):
    with aiohttp.ClientSession() as session:
        async with session.get(book_url) as response:
            print(book_url, 'loaded')


loop = asyncio.get_event_loop()
tasks = []
for href in hrefs:
    task = loop.create_task(find_book_download_link(href))
    tasks.append(task)
loop.run_forever()
driver.close()
