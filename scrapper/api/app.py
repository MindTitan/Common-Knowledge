from fastapi import FastAPI

from api.models import SpecifiedLinksScrapeTask, SitemapCollectScrapperTask
from worker.tasks import specified_links_scrapper_task, sitemap_collect_scrapper_task

app = FastAPI()


@app.post('/single-page-scrapper-task')
def trigger_single_page_scrapper_task(task: SpecifiedLinksScrapeTask):
    specified_links_scrapper_task.delay(task.model_dump(mode='json'))


@app.post('/sitemap-collect-scrapper-task')
def trigger_sitemap_collect_scrapper_task(task: SitemapCollectScrapperTask):
    sitemap_collect_scrapper_task.delay(task.model_dump(mode='json'))
