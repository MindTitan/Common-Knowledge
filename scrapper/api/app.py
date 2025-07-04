from fastapi import FastAPI, BackgroundTasks

from api.models import SinglePageScrapperTask, SitemapCollectScrapperTask
from api.scrapper import single_page_scrapper_task, sitemap_collect_scrapper_task

app = FastAPI()


@app.post('/single-page-scrapper-task')
def trigger_single_page_scrapper_task(task: SinglePageScrapperTask, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        single_page_scrapper_task, task
    )

@app.post('/sitemap-collect-scrapper-task')
def trigger_sitemap_collect_scrapper_task(task: SitemapCollectScrapperTask, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        sitemap_collect_scrapper_task, task
    )
