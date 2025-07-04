# import urllib.parse

import json
import hashlib
import os

from itemadapter import ItemAdapter
from scrapy import Spider
from scrapper.spiders.sitemap_collect_spider import SitemapCollectSpider

from scrapper.items import ScrappedItem, FileItem


def get_filename_from_url(url: str) -> str:
    # relative_url = urllib.parse.urlparse(url)
    # encoded_name = urllib.parse.quote_plus(relative_url.path)
    hashed_url = hashlib.sha1(url.encode()).hexdigest()
    return hashed_url



class ScrapedPipeline:

    def process_item(self, item, spider: Spider):
        if not isinstance(item, ScrappedItem):
            return item


        encoded_name = get_filename_from_url(item.source_url)

        scrapper_directory = spider.settings.get('SCRAPED_DIRECTORY', '/scrapped-data')
        filename = f'{encoded_name}{item.file_type}.meta.json'
        full_path = os.path.join(scrapper_directory, filename)

        with open(full_path, 'w') as f:
            json.dump(ItemAdapter(item).asdict(), f)

        return item


class FilePipeline:
    def process_item(self, item, spider: Spider):
        if not isinstance(item, FileItem):
            return item

        encoded_name = get_filename_from_url(item.source_url)
        scrapper_directory = spider.settings.get('SCRAPED_DIRECTORY', '/scrapped-data')
        filename = f'{encoded_name}{item.extension}'
        full_path = os.path.join(scrapper_directory, filename)
        with open(full_path, 'wb') as f:
            f.write(item.body)


class VisitedUrlsPipeline:
    def close_spider(self, spider: Spider):
        if type(spider) != SitemapCollectSpider:
            return
        spider: SitemapCollectSpider
        spider.logger.info(spider.valid_urls)
