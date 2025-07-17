import json
import hashlib
import os
import requests

from itemadapter import ItemAdapter
from scrapy import Spider
from scrapper.spiders.sitemap_collect_spider import SitemapCollectSpider

from scrapper.items import ScrappedItem
from api.models import BaseObject


def get_filename_as_hash(url: str) -> str:
    hashed_url = hashlib.sha1(url.encode()).hexdigest()
    return hashed_url


def get_path_for_scrapped_item(item: ScrappedItem, spider: Spider) -> str:
    scrapper_directory = spider.settings.get('SCRAPED_DIRECTORY', '/scrapped-data')

    task: BaseObject = spider.task

    agency_str = task.agency_name + '_' + task.agency_id
    source_str = task.source_name + '_' + task.source_id
    scraped_str = get_filename_as_hash(item.metadata.source_url)

    return os.path.join(scrapper_directory, agency_str, source_str, scraped_str)



class CreateDirectoryPipeline:
    def process_item(self, item, spider: Spider):
        if not isinstance(item, ScrappedItem):
            return item

        if not hasattr(spider, 'task'):
            return item

        path = get_path_for_scrapped_item(item, spider)
        os.makedirs(path, exist_ok=True)

        item.path = path

        return item



class MetadataPipeline:

    def process_item(self, item, spider: Spider):
        if not isinstance(item, ScrappedItem):
            return item

        filename = 'source.meta.json'
        full_path = os.path.join(item.path, filename)

        with open(full_path, 'w') as f:
            json.dump(ItemAdapter(item.metadata).asdict(), f)

        item.metadata_path = full_path
        return item


class FilePipeline:
    def process_item(self, item, spider: Spider):
        if not isinstance(item, ScrappedItem):
            return item


        filename = f'source{item.file.extension}'
        full_path = os.path.join(item.path, filename)
        with open(full_path, 'wb') as f:
            f.write(item.file.body)

        item.file_path = full_path
        return item


class TriggerCleaningPipeline:
    def process_item(self, item, spider: Spider):
        if not isinstance(item, ScrappedItem):
            return item

        requests.post(
            f"{spider.settings.get('RUUTER_PRIVATE')}/ckb/pipeline/clean-scraped-file",
            json={
                'file_path': item.file_path,
                'meta_data_path': item.metadata_path,
                'directory_path': item.path
            }
        )


class VisitedUrlsPipeline:
    def close_spider(self, spider: Spider):
        if type(spider) != SitemapCollectSpider:
            return
        spider: SitemapCollectSpider
        spider.logger.info(spider.valid_urls)
