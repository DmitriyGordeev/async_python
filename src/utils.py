import aiohttp


def get_header():
    return ({'User-Agent':
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                    (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', \
                'Accept-Language': 'en-US, en;q=0.5'})


async def async_request(url, action):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print("url:", url)
            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])

            html = await response.text()
            r = action(html)
            return r