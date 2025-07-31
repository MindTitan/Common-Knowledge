from fastapi import FastAPI

from api.models import (
    SpecifiedLinksScrapeTask, SitemapCollectScrapperTask, EntireSourceScrapperTask, UploadedFileTask, LinkToScrape
)
from worker.tasks import (
    specified_links_scrapper_task, sitemap_collect_scrapper_task,
    entire_source_scrapped_task, uploaded_file_task,
)
from api.models import EestiScrapperTask
from worker.tasks import eesti_scrapper_task

app = FastAPI()


@app.post('/specified-pages-scrapper-task')
def trigger_specified_pages_scrapper_task(task: SpecifiedLinksScrapeTask):
    specified_links_scrapper_task.delay(task.model_dump(mode='json'))


@app.post('/uploaded_file')
def trigger_uploaded_file_task(task: UploadedFileTask):
    links = []
    for url in task.urls:
        for download in task.download_files:
            if download.path == url.path:
                if download.download_url is None:
                    continue

                url.url = download.download_url
                links.append(LinkToScrape(**url.model_dump()))
    task_to_run = SpecifiedLinksScrapeTask(**{
        **task.model_dump(), 'urls': links
    })
    uploaded_file_task.delay(task_to_run.model_dump(mode='json'))


@app.post('/sitemap-collect-scrapper-task')
def trigger_sitemap_collect_scrapper_task(task: SitemapCollectScrapperTask):
    sitemap_collect_scrapper_task.delay(task.model_dump(mode='json'))


@app.post('/entire-source-scrapper-task')
def trigger_entire_source_scrapper_task(task: EntireSourceScrapperTask):
    entire_source_scrapped_task.delay(task.model_dump(mode='json'))


@app.post('/eesti-scrapper-task')
def trigger_eesti_scrapper_task(task: EestiScrapperTask):
    eesti_scrapper_task.delay(task.model_dump(mode='json'))