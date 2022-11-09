import asyncio

import requests

from html_parser import Parser
from utils import async_request, get_header

""" This program is just a quick cheat sheet of how to use async stuff in python"""

if __name__ == "__main__":

    # Request the news-feed
    url = "https://www.kommersant.ru/finance?page=3"
    html = requests.get(url, headers=get_header()).text
    html = html.replace(">", ">\n")

    # Find links to the specific articles
    # url2headline is a dict (url: str) -> (headline: str)
    url2headline = Parser.parse_feed(html)
    print ("found", len(url2headline), "news in this feed")

    loop = asyncio.get_event_loop()

    # 1. we create futures and collect them into array
    futures = []
    for url in list(url2headline.keys()):
        # every future will hold Article or None when finished
        # here we pass a functor 'Parser.parse_article' which will be called when page is downloaded
        # and async_request() will return parsing result
        f = asyncio.ensure_future(async_request(url, Parser.parse_article))
        futures.append(f)

    # 2. we run these futures together, so pages are downloaded and processed asyncronuosly
    loop.run_until_complete(asyncio.wait(futures))

    print (f"found {len(futures)} articles:")

    for f in futures:
        r = f.result()
        if r is None:
            continue
        print (f"topic: {r.topic}, headline: {r.headline}")





