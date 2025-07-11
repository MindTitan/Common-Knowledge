import json
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from api.models import SpecifiedLinksScrapeTask

from scrapper.spiders.sitemap_collect_spider import SitemapCollectSpider





def main():
    task = SpecifiedLinksScrapeTask(**json.loads(sys.argv[1][1:-1]))
    process = CrawlerProcess(get_project_settings())
    process.crawl(SitemapCollectSpider, task=task)
    process.start()


if __name__ == '__main__':
    main()
