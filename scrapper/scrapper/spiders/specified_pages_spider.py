from contextlib import suppress

import requests
from scrapy import Request
from scrapy.http import Response

from scrapper.spiders.base_spider import BaseSpider
from api.models import SpecifiedLinksScrapeTask


class SpecifiedPagesSpider(BaseSpider):
    name = 'specified_pages_spider'
    custom_settings = {
        'ROBOTSTXT_OBEY': False
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(kwargs.get('task'), SpecifiedLinksScrapeTask):
            self.task: SpecifiedLinksScrapeTask = kwargs.get('task')
            self.start_urls = [self.task.urls[0].url.unicode_string()]
            self.url_iter = iter([url.url.unicode_string() for url in self.task.urls[1:]])
            self.urls = self.task.urls


    async def parse(self, response: Response, **kwargs):
        async for obj in super().parse(response, **kwargs):
            base_id = None
            hashed = None
            self.logger.info(f'number of urls: {len(self.urls)}')
            for source_file in self.urls:
                if source_file.url.unicode_string() == response.request.url:
                    base_id = source_file.id
                    hashed = source_file.hash

            obj.source_file_id = base_id

            self.logger.info(f'url is {response.request.url} vs {self.urls[-1].url.unicode_string()}')
            self.logger.info(f'base id is {base_id}')
            self.logger.info(f'hashed is {hashed} vs {obj.hash}')

            if hashed is not None and obj.hash == hashed:
                self.logger.info(
                    f'Skipping {obj.metadata.source_url} because hash did not changed and it contains same data'
                )
                requests.post(
                    f"{self.settings.get('RUUTER_INTERNAL')}/ckb/source-file/update-scrapped-file-stop-scrapping",
                    json={'base_id': base_id}
                )
                continue

            yield obj

        with suppress(StopIteration):
            yield Request(
                next(self.url_iter), callback=self.parse, errback=self.errback,
                meta=self.get_meta(), headers=self.get_headers()
            )
