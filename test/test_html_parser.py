import asyncio
from unittest import TestCase

import aiohttp

from src.html_parser import Parser


async def async_request_write(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print("url:", url)
            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])

            html = await response.text()
            filename = url.replace("/", "__").replace(":", "__") + ".html"
            with open("pages/" + filename, "w") as fw:
                fw.write(html)
            return html


class TestHtmlParser(TestCase):

    def test_parse_feed(self):
        with open("pages/feed.html", "r") as f:
            content = f.read()
            r = Parser.parse_feed(content)
            keys = list(r.keys())
            self.assertEqual(len(r), 3)
            self.assertEqual('https://kommersant.ru//doc/5651418', keys[0])
            self.assertEqual('https://kommersant.ru//doc/5651185', keys[1])
            self.assertEqual('https://kommersant.ru//doc/5651153', keys[2])


    def test_async_download(self):
        with open("pages/feed.html", "r") as f:
            content = f.read()
            r = Parser.parse_feed(content)
            loop = asyncio.get_event_loop()

            # first we create futures and collect them into array
            futures = []
            for url in list(r.keys()):
                f = asyncio.ensure_future(async_request_write(url))
                futures.append(f)

            # second we run these futures together, so pages are downloaded asyncronuosly
            loop.run_until_complete(asyncio.wait(futures))

            # loop through finished futures to get the results
            for fut in futures:
                response = fut.result()
                self.assertTrue(len(response) > 0)
                self.assertTrue("doctype" in response.lower())


    def test_article_parse_page(self):
        with open("pages/article.html", "r") as f:
            html = f.read()
            art = Parser.parse_article(html)
            self.assertTrue(len(art.headline) > 0)
            self.assertTrue(len(art.topic) > 0)
            self.assertTrue(len(art.text) > 0)
            self.assertTrue(len(art.parsing_errors) == 0)
























