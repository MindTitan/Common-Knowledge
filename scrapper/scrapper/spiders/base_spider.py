import mimetypes
import hashlib
import contextlib

from typing import Any, AsyncIterator

import requests
from bs4 import BeautifulSoup
from playwright.async_api import Page

from fake_useragent import UserAgent
from scrapy import Spider, Request
from scrapy.exceptions import CloseSpider
from scrapy.http import Response

from api.models import BaseObject
from scrapper.items import FileItem, MetadataItem, Metadata, ScrappedItem



class BaseSpider(Spider):
    # start_urls = ['https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf']
    # start_urls = ['https://calibre-ebook.com/downloads/demos/demo.docx']
    start_urls = [
        # "https://www.terviseamet.ee",
        # "https://www.tervisekassa.ee",
        # "https://www.ravimiamet.ee",
        # "https://www.sm.ee",
        # "https://www.sotsiaalkindlustusamet.ee",
        # "https://www.tootukassa.ee",
        # "https://elron.ee/",
        # "https://www.transpordiamet.ee", # ??????????????  -- requires selenium

        # "https://www.airport.ee",
        # "https://www.ts.ee",??????????????
       # "https://www.lkf.ee/et",
       #  "https://www.fi.ee",
       #  "https://www.eestipank.ee",
       #  "https://www.kredex.ee",
       #  "https://www.emta.ee",
       #  "https://www.fin.ee",
    #     "https://www.ti.ee",
    #     "https://www.eakl.ee",
    #     "https://www.tooelu.ee",
    #     "https://www.minukarjaar.ee",
    #     "https://www.just.ee",
    #     "https://www.notar.ee",
    #     "https://www.kohus.ee",
    #     "https://www.kpkoda.ee",
    #     "https://www.riigiteataja.ee",
    #     "https://www.korruptsioon.ee",
    #     "https://www.maaamet.ee",
    #     "https://www.tallinn.ee/et/ehitus",
    #     "https://www.hm.ee",
    #     "https://www.harno.ee",
    #     "https://www.politsei.ee",
    #     "https://www.valimised.ee",
    #     "https://integratsioon.ee/",
    #     "https://www.siseministeerium",
    #     "https://www.tja.ee",
    #     "https://www.kaitseministeerium.ee",
    #     "https://www.mil.ee",
    #     "https://www.kaitseliit.ee",
    #     "https://www.kriis.ee",
    #     "https://www.rescue.ee",
    #     "https://www.kapo.ee",
    #     "https://www.kul.ee",
    #     "https://www.kik.ee",
    #     "https://www.envir.ee",
    #     "https://www.keskkonnaagentuur.ee",
    #     "https://www.keskkonnaamet.ee",
    #     "https://www.pria.ee",
    #     "https://www.agri.ee",
    #     "https://www.peaasi.ee",
    #     "https://www.lasteabi.ee",
    #     "https://www.vaimnetervis.ee",
    #     "https://koolirahu.lastekaitseliit.ee/et/",
    #     "https://www.itvaatlik.ee",
    #     "https://www.riigikogu.ee",
    #     "https://www.muinsuskaitseamet.ee",
    #     "https://www.eesti.ee",
    #     "https://www.epa.ee",
    ]
    # custom_settings = {
    #     'ROBOTSTXT_OBEY': False
    # }
    task: BaseObject

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ua = UserAgent(platforms='desktop')
        self.report_id = None

        if isinstance(kwargs.get('task'), BaseObject):
            self.task = kwargs['task']

    def check_source_is_stopping(self):
        try:
            is_stopping = requests.get(
                f'{self.settings.get('RUUTER_INTERNAL')}/ckb/source/get',
                params={'baseId': self.task.source_id}
            ).json()['response'][0]['isStopping']
        except Exception:
            raise CloseSpider('source not found')
        if is_stopping:
            raise CloseSpider('source is stopping')

    def get_meta(self):
        return {
            'playwright': True,
            'playwright_include_page': True,
            'playwright_page_goto_kwargs': {
                'timeout': 5_000,
                'wait_until': 'load',
            },
            "playwright_context_kwargs": {
                "ignore_https_errors": True,
            },
        }

    def get_headers(self):
        return {
            "User-Agent": self.ua.random,
        }

    async def start(self) -> AsyncIterator[Any]:
        for url in self.start_urls:
            yield Request(
                url, dont_filter=True, meta=self.get_meta(), headers=self.get_headers(),  errback=self.errback
            )

    def guess_file_extension(self, content_type: str) -> str:
        pure_content_type = content_type.split(';')[0]
        guessed_extension = mimetypes.guess_extension(pure_content_type)
        return guessed_extension

    @contextlib.asynccontextmanager
    async def close_page(self, response: Response) -> AsyncIterator[Page]:
        page: Page = response.meta["playwright_page"]
        try:
            self.logger.info(f'Page returned {response.url}')
            yield page
        finally:
            await page.close()
            await page.context.close()
            self.logger.info(f'Page closed {response.url}')

    async def errback(self, failure):
        page = failure.request.meta.get("playwright_page")
        if page is not None:
            await page.close()

    async def parse(self, response: Response, **kwargs):
        async with self.close_page(response) as page:
            self.check_source_is_stopping()
            page: Page

            file_extension = self.guess_file_extension(
                response.headers.get(b'Content-Type', 'text/html').decode('utf-8')
            )

            if file_extension == '.html':
                title = await page.title()
            else:
                title = response.url

        if file_extension == '.html':
            soup = BeautifulSoup(response.body, 'lxml')
            text = soup.get_text()
            hashed = hashlib.sha1(text.encode()).hexdigest()
        else:
            hashed = hashlib.sha1(response.body).hexdigest()

        file_item = FileItem(body=response.body, source_url=response.url, extension=file_extension)

        metadata_item = MetadataItem(
            file_type=file_extension, metadata=Metadata(), source_url=response.url, page_title=title
        )

        scrapped_item = ScrappedItem(file=file_item, metadata=metadata_item, hash=hashed)
        yield scrapped_item
