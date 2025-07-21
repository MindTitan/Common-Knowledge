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

    def parse(self, response: Response, **kwargs):
        file_extension = self.guess_file_extension(
            response.headers.get(b'Content-Type', 'text/html').decode('utf-8')
        )
        if file_extension not in self.settings.get('ALLOWED_FILETYPES'):
            # TODO: place log here
            return

        file_item = FileItem(body=response.body, source_url=response.url, extension=file_extension)

        metadata_item = MetadataItem(file_type=file_extension, metadata=Metadata(), source_url=response.url)

        scrapped_item = ScrappedItem(file=file_item, metadata=metadata_item)
        yield scrapped_item