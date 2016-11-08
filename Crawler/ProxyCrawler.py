__author__ = 'flappy'

try:
    # Python 3.4.
    from asyncio import JoinableQueue as Queue
except ImportError:
    # Python 3.5.
    from asyncio import Queue
import asyncio
import aiohttp
import urllib.request
import cgi
import sys
import time
import traceback
import logging

from bs4 import BeautifulSoup


LOGGER = logging.getLogger()

class ProxyCrawler:

    def __init__(self, roots, loop=None):
        self.Q = Queue()
        self.init_urls()
        self.loop = loop or asyncio.get_event_loop()

        self.session = aiohttp.ClientSession(loop=self.loop)
        self.agents = []
        self.agents = set()

    def init_urls(self):
        for page in range(1, 101):
            # self.Q.put_nowait(('http://www.xicidaili.com/nn/%s' % page, 1))
            self.Q.put_nowait(('http://www.xicidaili.com/nn/%d' % page, 1))


    @asyncio.coroutine
    def fetch(self, url, max_redirects):
        # url, max_redirects = yield from self.Q.get()
        print(url, max_redirects)
        try:
            headers={
                'User-Agent':'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25',
                'Host':'www.xicidaili.com',
                'Referer':'http://www.xicidaili.com/n'
            }
            proxy = "http://171.38.188.172:8123"
            response = yield from self.session.get(
                    url, proxy=proxy, allow_redirects=False, headers=headers)
        except aiohttp.ClientError as client_error:
            exception = client_error
            LOGGER.error(client_error)
            return
        try:
            yield from self.process(response)
        finally:
            # pass
            yield from response.release() # todo, 弄懂release什么意思

    @asyncio.coroutine
    def process(self, response):
        text = yield from self.parse_response(response)
        try: # 坑, 如果没给下面有bug得代码加 try...except... 会一只阻塞在这里, 说明Exception不会导致上面yield from推出。。。。
            soup = BeautifulSoup(text, 'lxml')

            # trs = soup.select('li > a')#.find_all('a')
            # print(trs)
            # print(type(trs))
            # for tag in trs:
                # print(tag)
                # if 'href' in tag.attrs:
                #     print(tag.string, tag['href'])
                # else:
                #     print(tag)
                # print(tr['href'])
            #     for href in tr.find_all('a'):
            #         print('href:')
            #         print(type(href))
            #         print(href)
            #         print(href['href'])
            # print('\ntrs\n\n')
            # print(trs)
            trs = soup.find('table',id="ip_list").findAll('tr')
            for tr in trs[1:]:
                tds = tr.findAll('td')
                ip = tds[1].text.strip()
                port = tds[2].text.strip()
                protocol = tds[5].text.strip()
                agent = '%s://%s:%s' % (protocol, ip, port)
                self.agents.add(agent)
        except Exception as e:
            print(e)

    @asyncio.coroutine
    def parse_response(self, response):
        text = None
        if response.status == 200:
            content_type = response.headers.get('content-type')
            pdict = {}

            if content_type:
                content_type, pdict = cgi.parse_header(content_type)

            encoding = pdict.get('charset', 'utf-8')
            if content_type in ('text/html', 'application/xml'):
                text = yield from response.text()
                soup = BeautifulSoup(text, 'lxml')
                # print(text)
        return text

    @asyncio.coroutine
    def work(self):
        """Process queue items forever."""
        try:
            while True:
                url, max_redirects = yield from self.Q.get()
                yield from self.fetch(url, max_redirects)
                self.Q.task_done()
        except asyncio.CancelledError:
            pass

    @asyncio.coroutine
    def crawl(self):
        workers = [asyncio.Task(self.work(), loop=self.loop)
                   for _ in range(10)]
        self.t0 = time.time()
        yield from self.Q.join()
        self.t1 = time.time()
        for w in workers:
            w.cancel()

    def close(self):
        """Close resources."""
        self.session.close()


if __name__ == '__main__':
    loop = asyncio.SelectorEventLoop()
    asyncio.set_event_loop(loop)

    roots = {''}

    crawler = ProxyCrawler(roots)
    try:
        loop.run_until_complete(crawler.crawl())  # Crawler gonna crawl.
    except KeyboardInterrupt:
        sys.stderr.flush()
        print('\nInterrupted\n')
    finally:
        crawler.close()
        loop.stop()
        loop.run_forever()
        loop.close()
        with open('proxy.txt', 'w') as fid:
            for agent in crawler.agents:
                fid.write(agent+'\n')
        print('-----DONE-----')

