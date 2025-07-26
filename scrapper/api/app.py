from fastapi import FastAPI

from api.models import SpecifiedLinksScrapeTask, SitemapCollectScrapperTask, EntireSourceScrapperTask
from worker.tasks import specified_links_scrapper_task, sitemap_collect_scrapper_task, entire_source_scrapped_task
from api.models import EestiScrapperTask
from worker.tasks import eesti_scrapper_task

app = FastAPI()


@app.post('/single-page-scrapper-task')
def trigger_single_page_scrapper_task(task: SpecifiedLinksScrapeTask):
    specified_links_scrapper_task.delay(task.model_dump(mode='json'))


@app.post('/sitemap-collect-scrapper-task')
def trigger_sitemap_collect_scrapper_task(task: SitemapCollectScrapperTask):
    sitemap_collect_scrapper_task.delay(task.model_dump(mode='json'))


@app.post('/entire-source-scrapper-task')
def trigger_entire_source_scrapper_task(task: EntireSourceScrapperTask):
    entire_source_scrapped_task.delay(task.model_dump(mode='json'))

@app.post('/eesti-scrapper-task')
def trigger_eesti_scrapper_task(task: EestiScrapperTask):
    eesti_scrapper_task.delay(task.model_dump(mode='json'))