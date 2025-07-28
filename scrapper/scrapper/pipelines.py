import datetime
import json
import hashlib
import os
import requests

from itemadapter import ItemAdapter
from scrapy import Spider

from api.utils import get_path_for_task
from scrapper.spiders.sitemap_collect_spider import SitemapCollectSpider
from scrapper.spiders.single_url_spider import SingleUrlSpider

from scrapper.items import ScrappedItem
from api.models import BaseObject


def get_filename_as_hash(url: str) -> str:
    hashed_url = hashlib.sha1(url.encode()).hexdigest()
    return hashed_url


def get_path_for_scrapped_item(item: ScrappedItem, spider: Spider) -> str:
    scrapper_directory = spider.settings.get('SCRAPED_DIRECTORY', '/scrapped-data')

    path = get_path_for_task(spider.task)
    scraped_str = get_filename_as_hash(item.metadata.source_url)

    return os.path.join(scrapper_directory, path, scraped_str)


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

        r = requests.post(
            f"{spider.settings.get('RUUTER_INTERNAL')}/ckb/pipeline/upload-file-sync",
            json={
                'source_file_path': full_path,
            }
        )
        item.metadata_path_uploaded = r.json()['response']

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

        r = requests.post(
            f"{spider.settings.get('RUUTER_INTERNAL')}/ckb/pipeline/upload-file-sync",
            json={
                'source_file_path': full_path,
            }
        )
        item.file_path_uploaded = r.json()['response']

        return item


class TriggerCleaningPipeline:
    def process_item(self, item, spider: Spider):
        if not isinstance(item, ScrappedItem):
            return item

        requests.post(
            f"{spider.settings.get('RUUTER_INTERNAL')}/ckb/pipeline/clean-scraped-file",
            json={
                'file_path': item.file_path,
                'meta_data_path': item.metadata_path,
                'directory_path': item.path,
                'source_file_id': item.source_file_id,
            }
        )

        return item


class CreateSourceFile:
    def process_item(self, item, spider: Spider):
        if not hasattr(spider, 'task'):
            return item

        if not isinstance(item, ScrappedItem):
            return item

        if item.source_file_id is not None:
            return item

        spider: SitemapCollectSpider
        task: BaseObject = spider.task

        res = requests.post(f'{spider.settings.get('RUUTER_INTERNAL')}/ckb/source-file/add-scrapped-file', json={
            'agency_id': task.agency_id,
            'source_id': task.source_id,
            'url': item.metadata.source_url,
            'page_title': item.metadata.page_title,
            'original_data_url': item.file_path_uploaded,
            'original_metadata_url': item.metadata_path_uploaded,
            'original_data_hash': item.hash,
            'scraped_at': item.metadata.created_at
        })
        item.source_file_id = res.json()['response']
        return item


class UpdateSourceFile:
    def process_item(self, item, spider: Spider):
        if not isinstance(item, ScrappedItem):
            return item

        if item.source_file_id is None:
            return item

        requests.post(f'{spider.settings.get('RUUTER_INTERNAL')}/ckb/source-file/update-scrapped-file', json={
            'base_id': item.source_file_id,
            'url': item.metadata.source_url,
            'page_title': item.metadata.page_title,
            'original_data_url': item.file_path_uploaded,
            'original_metadata_url': item.metadata_path_uploaded,
            'original_data_hash': item.hash,
            'scraped_at': item.metadata.created_at
        })
        return item


class ScrappingFinishedPipeline:
    def close_spider(self, spider: Spider):
        if not hasattr(spider, 'task'):
            return

        spider: SitemapCollectSpider | SingleUrlSpider
        task: BaseObject = spider.task

        requests.post(f'{spider.settings.get('RUUTER_INTERNAL')}/ckb/source/update-status', json={
            'source_id': task.source_id,
            'status': 'finished',
        })


class InitLoggingPipeline:
    def open_spider(self, spider: Spider):
        pass


class SetSourceStatusRunningPipeline:
    def open_spider(self, spider: Spider):
        if not hasattr(spider, 'task'):
            return

        spider: SitemapCollectSpider | SingleUrlSpider
        task: BaseObject = spider.task

        requests.post(f'{spider.settings.get('RUUTER_INTERNAL')}/ckb/source/update-status', json={
            'source_id': task.source_id,
            'status': 'running',
        })


class CreateSourceRunReportPipeline:
    def open_spider(self, spider: Spider):
        if not hasattr(spider, 'task'):
            return

        task: BaseObject = spider.task

        agency_name = requests.get(
            f'{spider.settings.get('RUUTER_INTERNAL')}/ckb/agency/get',
            params={'baseId': task.agency_id}
        ).json()['response'][0]['name']
        spider.logger.info(f'agency_name: {agency_name}')
        url = requests.get(
            f'{spider.settings.get('RUUTER_INTERNAL')}/ckb/source/get',
            params={'baseId': task.source_id}
        ).json()['response'][0]['url']


        report_id = requests.post(f'{spider.settings.get('RUUTER_INTERNAL')}/ckb/reports/add', json={
            'agencyBaseId': task.agency_id,
            'sourceBaseId': task.source_id,
            'agencyName': agency_name,
            'url': url,
            'scrapingStartedAt': datetime.datetime.now(datetime.UTC).isoformat(),
            'scrapingFinishedAt': None,
            'error': 0,
            'scrapingLogUrl': None,
            'cleaningLogUrl': None
        }).json()['response'][0]['baseId']

        spider.report_id = report_id



class UploadLogsPipeline:
    def close_spider(self, spider: Spider):
        if not hasattr(spider, 'report_id'):
            return

