from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor
import urllib
import threading
import asyncio
import aiohttp
import lxml
import lxml.html
import re
import aiotg
import uuid

driver = webdriver.PhantomJS()
driver_lock = threading.Lock()
driver_executor = ThreadPoolExecutor(max_workers=1)
SEARCH_URL = "https://cse.google.com/cse?cx=013493258683483688568:xhfa6ctm1ki&q={0}#gsc.tab=0&gsc.q={0}&gsc.page={1}"
BOOK_DOWNLOAD_LINK_XPATH = "/html/body/table/tbody/tr[2]/td/div[2]/table/tbody/tr/td[2]/table/tbody/tr[11]/td[2]/a"


def search_urls(query, page=1):
    query = urllib.parse.quote_plus(query)
    search_url = SEARCH_URL.format(query, page)
    with driver_lock:
        driver.get(search_url)
        tree = lxml.html.fromstring(driver.page_source)
        links = tree.cssselect('a.gs-title')
        hrefs = (p_link.attrib.get('href', None) for p_link in links)
        hrefs = (str(href) for href in hrefs if href is not None)
        hrefs = set(hrefs)
        regex = re.compile(r'(http://it-ebooks.info/book/\d*/)')
        hrefs = [href for href in hrefs if regex.match(href)]
        return hrefs


async def find_book_download_link(book_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(book_url) as response:
            body = await response.text()
            tree = lxml.html.fromstring(body)
            download = tree.xpath("//text()[. = 'Download:']")[0].getparent()
            download = download.getnext()[0]
            return {'link': download.attrib['href'],
                    'title': download.text}


class NotFound(Exception):
    pass


async def search_books(loop, query, page=1):
    book_urls = await loop.run_in_executor(
        driver_executor, search_urls, query, page)
    tasks = []
    for url in book_urls:
        tasks.append(find_book_download_link(url))
    if tasks:
        results, _ = await asyncio.wait(tasks)
        results = [r.result() for r in results]
    else:
        raise NotFound()
    return results


bot = aiotg.Bot(api_token="209580635:AAEP4TsSOn9d9XvO9IHfRFiuV2ZUAL2Heao")
loop = asyncio.get_event_loop()

next_pages = {}


def generate_answer(results, query, page):
    answer_template = "[{title}]({link})"
    answer = '\n'.join(answer_template.format(**r) for r in results)
    next_page = str(uuid.uuid4()).replace('-', '')
    next_pages[next_page] = (search_books(loop, query, page=page + 1),
                             page + 1, query)
    answer += '\n\n Para ver mas resultados, pulsa: /next{}'.format(next_page)
    return answer


@bot.command(r"/buscar (.+)")
async def search(chat, match):
    query = match.group(1)
    results = await search_books(loop, query)
    answer = generate_answer(results, query, 1)
    await chat.reply(answer, parse_mode="Markdown")


@bot.command(r"/next(.+)")
async def next(chat, match):
    uuid = match.group(1)
    data = next_pages.get(uuid, None)
    if data is None:
        await chat.reply("Id invalido")
        return
    coro, page, query = data
    del next_pages[uuid]
    try:
        results = await coro
        answer = generate_answer(results, query, page)
        await chat.reply(answer, parse_mode="Markdown")
    except NotFound:
        await chat.reply("No hay mas resultados")


if __name__ == '__main__':
    loop.run_until_complete(bot.loop())
