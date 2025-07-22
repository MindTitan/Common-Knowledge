from playwright.async_api import Page
from scrapy import Request
from scrapy.http import Response

from scrapper.items import FileItem, MetadataItem, Metadata, ScrappedItem
from scrapper.spiders.sitemap_collect_spider import SitemapCollectSpider
from api.models import SpecifiedLinksScrapeTask


class SingleUrlSpider(SitemapCollectSpider):
    name = 'single_url_spider'
    custom_settings = {
        'ROBOTSTXT_OBEY': False
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(kwargs.get('task'), SpecifiedLinksScrapeTask):
            self.task: SpecifiedLinksScrapeTask = kwargs.get('task')
            self.start_urls = [url.url.unicode_string() for url in self.task.urls]

    async def parse(self, response: Response, **kwargs):
        async for obj in super().parse(response, **kwargs):
            if isinstance(obj, Request):
                continue

            if isinstance(obj, ScrappedItem):
                base_id = None
                hashed = None
                for source_file in self.task.urls:
                    if source_file.url == response.request.url:
                        base_id = source_file.id
                        hashed = source_file.hash

                obj.source_file_id = base_id

                if hashed is not None and obj.hash == hashed:
                    self.logger.info(
                        f'Skipping {obj.metadata.source_url} because hash did not changed and it contains same data'
                    )
                    continue

                yield obj
