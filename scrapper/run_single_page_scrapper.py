import json
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from api.models import SinglePageScrapperTask

from scrapper.spiders.single_url_spider import SingleUrlSpider





def main():
    task = SinglePageScrapperTask(**json.loads(sys.argv[1][1:-1]))
    process = CrawlerProcess(get_project_settings())
    process.crawl(SingleUrlSpider, start_urls=[task.url.unicode_string()])
    process.start()


if __name__ == '__main__':
    main()
