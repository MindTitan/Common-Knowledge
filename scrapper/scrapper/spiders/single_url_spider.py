from scrapy.http import Response

from scrapper.items import FileItem, ScrappedItem, Metadata
from scrapper.spiders.sitemap_collect_spider import SitemapCollectSpider


class SingleUrlSpider(SitemapCollectSpider):
    name = 'single_url_spider'
    custom_settings = {
        'ROBOTSTXT_OBEY': False
    }

    def parse(self, response: Response, **kwargs):
        file_extension = self.guess_file_extension(
            response.headers.get(b'Content-Type', 'text/html').decode('utf-8')
        )
        if file_extension not in self.settings.get('ALLOWED_FILETYPES'):
            # TODO: place log here
            return

        yield FileItem(body=response.body, source_url=response.url, extension=file_extension)

        yield ScrappedItem(file_type=file_extension, metadata=Metadata(), source_url=response.url)
